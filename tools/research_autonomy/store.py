"""Transactional scientific authority. No runner, scheduler or result writer."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from .envelope import canonical_json, content_hash, validate_control, validate_envelope
from .models import BudgetState, DurableLineageSnapshot, HoldoutState

ZERO_HASH = "sha256:" + "0" * 64


class AuthorityConflict(ValueError):
    """Missing, stale, conflicting or exhausted scientific authority."""


class ResearchAuthorityStore:
    def __init__(self, dsn: str):
        if not dsn:
            raise ValueError("authority DSN required")
        self._dsn = dsn

    @contextmanager
    def _transaction(self):
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            # The first kernel serializes authority writes across campaigns as well
            # as within them, including domain-wide informative holdout escape.
            conn.execute("SELECT pg_advisory_xact_lock(721026002)")
            yield conn

    @staticmethod
    def _campaign(conn, campaign_id):
        row = conn.execute("SELECT * FROM research_authority.campaign_state WHERE campaign_id=%s FOR UPDATE", (campaign_id,)).fetchone()
        if row is None:
            raise AuthorityConflict("campaign absent")
        return row

    @staticmethod
    def _active_envelope(conn, envelope):
        row = conn.execute("""SELECT r.semantic_payload, c.state
            FROM research_authority.envelope_registry r
            JOIN research_authority.envelope_control_state c USING(envelope_id,envelope_version)
            WHERE r.envelope_id=%s AND r.envelope_version=%s FOR UPDATE OF c""", (envelope.envelope_id, envelope.envelope_version)).fetchone()
        if row is None or row["state"] != "active" or row["semantic_payload"] != canonical_json(envelope.model_dump(mode="json")):
            raise AuthorityConflict("exact registered active envelope required")

    @staticmethod
    def _replay(conn, event_id, event_type, payload):
        row = conn.execute("SELECT * FROM research_authority.authority_audit WHERE event_id=%s", (event_id,)).fetchone()
        if row:
            stored = json.loads(row["normalized_payload"])
            if content_hash(stored) != row["event_content_sha256"]:
                raise AuthorityConflict("idempotency audit hash mismatch")
            if row["event_type"] != event_type or stored["input"] != json.loads(canonical_json(payload)):
                raise AuthorityConflict("conflicting idempotency replay")
            return stored
        return None

    @staticmethod
    def _prior_outcome(event):
        return DurableLineageSnapshot.model_validate_json(canonical_json({
            **event["outcome"], "lineage_version": event["event_sequence"],
            "lineage_sha256": content_hash(event),
        }))

    @staticmethod
    def _audit(conn, *, event_id, event_type, payload, campaign=None):
        sequence = campaign["lineage_version"] + 1 if campaign else 1
        previous = campaign["lineage_sha256"] if campaign else ZERO_HASH
        outcome = None
        if campaign:
            outcome = ResearchAuthorityStore._state_snapshot(conn, campaign["campaign_id"]).model_dump(mode="json", exclude={"lineage_version", "lineage_sha256"})
        normalized = canonical_json({"campaign_id": campaign["campaign_id"] if campaign else None,
            "event_type": event_type, "event_sequence": sequence,
            "previous_lineage_sha256": previous, "input": payload, "outcome": outcome})
        digest = content_hash(json.loads(normalized))
        conn.execute("""INSERT INTO research_authority.authority_audit
            (event_id,campaign_id,event_type,event_sequence,previous_lineage_sha256,normalized_payload,event_content_sha256)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""", (event_id, campaign["campaign_id"] if campaign else None, event_type, sequence, previous, normalized, digest))
        if campaign:
            conn.execute("UPDATE research_authority.campaign_state SET lineage_version=%s,lineage_sha256=%s WHERE campaign_id=%s", (sequence, digest, campaign["campaign_id"]))
        return digest

    def register_envelope(self, envelope):
        envelope = validate_envelope(envelope, repo_sha=envelope.repo_sha)
        payload = envelope.model_dump(mode="json")
        event_id = f"envelope:{envelope.envelope_id}:{envelope.envelope_version}"
        with self._transaction() as conn:
            if self._replay(conn, event_id, "register_envelope", payload):
                return envelope
            conn.execute("""INSERT INTO research_authority.envelope_registry
                (envelope_id,envelope_version,content_sha256,repo_sha,approved_by,approved_at,semantic_payload)
                VALUES (%s,%s,%s,%s,%s,%s,%s)""", (envelope.envelope_id, envelope.envelope_version, envelope.content_sha256, envelope.repo_sha, envelope.approved_by, envelope.approved_at, canonical_json(payload)))
            self._audit(conn, event_id=event_id, event_type="register_envelope", payload=payload)
            conn.execute("INSERT INTO research_authority.envelope_control_state VALUES (%s,%s,'active',NULL,%s)", (envelope.envelope_id, envelope.envelope_version, event_id))
        return envelope

    def apply_control(self, envelope, control):
        envelope = validate_envelope(envelope, repo_sha=envelope.repo_sha)
        control = validate_control(control, envelope=envelope)
        payload = control.model_dump(mode="json")
        event_id = f"control:{control.control_action_id}"
        with self._transaction() as conn:
            if self._replay(conn, event_id, "control_envelope", payload):
                return
            self._active_envelope(conn, envelope)
            if control.successor:
                row = conn.execute("SELECT r.content_sha256,c.state FROM research_authority.envelope_registry r JOIN research_authority.envelope_control_state c USING(envelope_id,envelope_version) WHERE envelope_id=%s AND envelope_version=%s", (control.successor.envelope_id, control.successor.envelope_version)).fetchone()
                if row is None or row["content_sha256"] != control.successor.content_sha256 or row["state"] != "active":
                    raise AuthorityConflict("exact active replacement envelope absent")
            self._audit(conn, event_id=event_id, event_type="control_envelope", payload=payload)
            conn.execute("UPDATE research_authority.envelope_control_state SET state=%s,control_action=%s,last_event_id=%s WHERE envelope_id=%s AND envelope_version=%s", ("revoked" if control.action == "revoke" else "replaced", canonical_json(payload), event_id, envelope.envelope_id, envelope.envelope_version))

    def open_campaign(self, envelope, *, campaign_id, contamination_domain_id, holdout_id, hypothesis_fingerprint):
        envelope = validate_envelope(envelope, repo_sha=envelope.repo_sha)
        if contamination_domain_id != envelope.contamination_domain_id or holdout_id not in {s.final_holdout_ref for s in envelope.search_policy.split_protocols}:
            raise AuthorityConflict("campaign domain/holdout outside human envelope binding")
        payload = {"campaign_id": campaign_id, "envelope": [envelope.envelope_id, envelope.envelope_version, envelope.content_sha256], "domain": contamination_domain_id, "holdout_id": holdout_id, "hypothesis_fingerprint": hypothesis_fingerprint}
        with self._transaction() as conn:
            self._active_envelope(conn, envelope)
            replay = self._replay(conn, f"campaign:{campaign_id}", "open_campaign", payload)
            if replay:
                return self._prior_outcome(replay)
            if not replay:
                b = envelope.budgets
                conn.execute("""INSERT INTO research_authority.campaign_state
                    (campaign_id,envelope_id,envelope_version,envelope_content_sha256,contamination_domain_id,holdout_id,hypothesis_fingerprint,proposal_ceiling,trial_ceiling,search_ceiling,lineage_sha256,state)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'open')""", (campaign_id, envelope.envelope_id, envelope.envelope_version, envelope.content_sha256, contamination_domain_id, holdout_id, hypothesis_fingerprint, b.campaign_proposals, b.campaign_trials, b.campaign_searches, ZERO_HASH))
                conn.execute("INSERT INTO research_authority.holdout_state VALUES (%s,%s,'unexposed',NULL,NULL) ON CONFLICT DO NOTHING", (contamination_domain_id, holdout_id))
                self._audit(conn, event_id=f"campaign:{campaign_id}", event_type="open_campaign", payload=payload, campaign=self._campaign(conn, campaign_id))
            return self._snapshot(conn, campaign_id)

    @staticmethod
    def _snapshot(conn, campaign_id):
        c = ResearchAuthorityStore._campaign(conn, campaign_id)
        events = conn.execute("SELECT * FROM research_authority.authority_audit WHERE campaign_id=%s ORDER BY event_sequence", (campaign_id,)).fetchall()
        previous = ZERO_HASH
        for sequence, row in enumerate(events, 1):
            payload = json.loads(row["normalized_payload"])
            if row["event_sequence"] != sequence or row["previous_lineage_sha256"] != previous or row["event_content_sha256"] != content_hash(payload) or payload["campaign_id"] != campaign_id or payload["event_sequence"] != sequence or payload["previous_lineage_sha256"] != previous or payload["event_type"] != row["event_type"]:
                raise AuthorityConflict("durable audit chain integrity mismatch")
            previous = row["event_content_sha256"]
        if c["lineage_version"] != len(events) or c["lineage_sha256"] != previous:
            raise AuthorityConflict("durable current lineage mismatch")
        return ResearchAuthorityStore._state_snapshot(conn, campaign_id)

    @staticmethod
    def _state_snapshot(conn, campaign_id):
        c = ResearchAuthorityStore._campaign(conn, campaign_id)
        h = conn.execute("SELECT * FROM research_authority.holdout_state WHERE contamination_domain_id=%s AND holdout_id=%s", (c["contamination_domain_id"], c["holdout_id"])).fetchone()
        contaminated = conn.execute("SELECT EXISTS(SELECT 1 FROM research_authority.contamination_edge WHERE contamination_domain_id=%s) AS contaminated", (c["contamination_domain_id"],)).fetchone()["contaminated"]
        return DurableLineageSnapshot(
            campaign_id=campaign_id, envelope_id=c["envelope_id"], envelope_version=c["envelope_version"],
            envelope_content_sha256=c["envelope_content_sha256"], contamination_domain_id=c["contamination_domain_id"],
            lineage_version=c["lineage_version"], lineage_sha256=c["lineage_sha256"],
            budget=BudgetState(**{key: c[key] for key in BudgetState.model_fields}),
            holdout=HoldoutState(contamination_domain_id=c["contamination_domain_id"], holdout_id=c["holdout_id"], state=h["state"], contaminated=contaminated),
        )

    def load_snapshot(self, campaign_id):
        with self._transaction() as conn:
            return self._snapshot(conn, campaign_id)

    def open_search(self, intent, envelope, request, *, repo_root: Path):
        from .contract_builder import construct_contract, contract_from_payload, validate_inputs

        intent, envelope, request = validate_inputs(intent, envelope, request, repo_root=repo_root)
        payload = {"request": request.model_dump(mode="json"), "intent_evidence": [e.model_dump(mode="json") for e in intent.evidence_anchors]}
        with self._transaction() as conn:
            self._active_envelope(conn, envelope)
            c = self._campaign(conn, request.campaign_id)
            if c["state"] != "open" or (request.parent_search_id is None and c["hypothesis_fingerprint"] != intent.fingerprint_sha256):
                raise AuthorityConflict("campaign state/hypothesis mismatch")
            replay = self._replay(conn, f"search:{request.search_id}", "open_search", payload)
            if replay:
                return self._load_contract(conn, request.search_id)
            if request.parent_search_id:
                parent = conn.execute("SELECT campaign_id,state FROM research_authority.search_lineage WHERE search_id=%s", (request.parent_search_id,)).fetchone()
                if parent is None or parent["campaign_id"] != request.campaign_id or parent["state"] != "finalized":
                    raise AuthorityConflict("exact finalized same-campaign parent required")
            snapshot = self._snapshot(conn, request.campaign_id)
            # A hypothesis cannot evade its ceiling by creating another campaign.
            totals = conn.execute("""SELECT coalesce(sum(
                    (SELECT count(*) FROM research_authority.proposal_record p WHERE p.search_id=s.search_id)+r.proposals_remaining),0) AS p,
                coalesce(sum((SELECT count(scientific_trial_id) FROM research_authority.proposal_record p WHERE p.search_id=s.search_id)+r.trials_remaining),0) AS t
                FROM research_authority.search_lineage s JOIN research_authority.search_budget_reservation r USING(search_id)
                WHERE s.envelope_id=%s AND s.envelope_version=%s AND s.contract_payload::jsonb->>'hypothesis_fingerprint'=%s""", (envelope.envelope_id, envelope.envelope_version, intent.fingerprint_sha256)).fetchone()
            if totals["p"] + request.max_proposals > envelope.budgets.hypothesis_proposals or totals["t"] + request.max_scientific_trials > envelope.budgets.hypothesis_trials:
                raise AuthorityConflict("hypothesis cumulative ceiling exhausted")
            contract = construct_contract(intent, envelope, request, snapshot)
            conn.execute("""INSERT INTO research_authority.search_lineage
                (search_id,campaign_id,parent_search_id,reason_for_change,contract_sha256,contract_payload,envelope_id,envelope_version,envelope_content_sha256,pre_lineage_version,pre_lineage_sha256,proposals_before_search,trials_before_search,reserved_proposals,reserved_trials,state)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'open')""", (contract.search_id, contract.campaign_id, contract.parent_search_id, contract.reason_for_change, contract.contract_hash, canonical_json(contract.to_dict()), contract.envelope_id, contract.envelope_version, contract.envelope_content_sha256, contract.authority_lineage_version, contract.authority_lineage_sha256, contract.campaign_proposals_before_search, contract.campaign_scientific_trials_before_search, contract.max_proposals, contract.max_scientific_trials))
            conn.execute("INSERT INTO research_authority.search_budget_reservation VALUES (%s,%s,%s,'active')", (contract.search_id, contract.max_proposals, contract.max_scientific_trials))
            conn.execute("UPDATE research_authority.campaign_state SET reserved_proposals=reserved_proposals+%s,reserved_trials=reserved_trials+%s,search_count=search_count+1 WHERE campaign_id=%s", (contract.max_proposals, contract.max_scientific_trials, contract.campaign_id))
            self._audit(conn, event_id=f"search:{contract.search_id}", event_type="open_search", payload=payload, campaign=c)
            # Round-trip is part of the frozen payload boundary.
            if contract_from_payload(json.loads(canonical_json(contract.to_dict()))).contract_hash != contract.contract_hash:
                raise AuthorityConflict("frozen contract serialization divergence")
            return contract

    @staticmethod
    def _load_contract(conn, search_id):
        from .contract_builder import contract_from_payload

        row = conn.execute("SELECT contract_payload,contract_sha256 FROM research_authority.search_lineage WHERE search_id=%s", (search_id,)).fetchone()
        if row is None:
            raise AuthorityConflict("search absent")
        contract = contract_from_payload(json.loads(row["contract_payload"]))
        if contract.contract_hash != row["contract_sha256"]:
            raise AuthorityConflict("durable contract hash mismatch")
        return contract

    def load_contract(self, search_id):
        with self._transaction() as conn:
            return self._load_contract(conn, search_id)

    @staticmethod
    def _search_active(conn, contract):
        row = conn.execute("""SELECT s.state AS search_state,c.state AS envelope_state
            FROM research_authority.search_lineage s JOIN research_authority.envelope_control_state c
            USING(envelope_id,envelope_version) WHERE s.search_id=%s""", (contract.search_id,)).fetchone()
        if row is None or row["search_state"] != "open" or row["envelope_state"] != "active":
            raise AuthorityConflict("active search and envelope required")

    def verify_recovery_binding(self, handoff, *, repo_root: Path):
        from .contract_builder import verify_evidence
        from .models import BoundedSearchRequest, EvidenceBinding
        with self._transaction() as conn:
            contract = self._load_contract(conn, handoff.search_id)
            self._search_active(conn, contract)
            snapshot = self._snapshot(conn, contract.campaign_id)
            if (snapshot.lineage_version, snapshot.lineage_sha256) != (handoff.authority_lineage_version, handoff.authority_lineage_sha256):
                raise AuthorityConflict("handoff current lineage mismatch")
            opened = conn.execute("SELECT normalized_payload FROM research_authority.authority_audit WHERE event_id=%s", (f"search:{contract.search_id}",)).fetchone()
            if opened is None:
                raise AuthorityConflict("handoff opening lineage absent")
            inputs = json.loads(opened["normalized_payload"])["input"]
            request = BoundedSearchRequest.model_validate_json(canonical_json(inputs["request"]))
            if request.intent_sha256 != handoff.intent_sha256:
                raise AuthorityConflict("handoff intent binding mismatch")
            for binding in [request.strategy_spec_evidence, request.data_evidence] + [EvidenceBinding.model_validate(e) for e in inputs["intent_evidence"]]:
                verify_evidence(repo_root, binding, repo_sha=contract.repo_sha)
            rows = conn.execute("SELECT * FROM research_authority.proposal_record WHERE search_id=%s ORDER BY proposal_sequence", (contract.search_id,)).fetchall()
            expected = [p.model_dump(mode="json") for p in handoff.pre_wave_snapshot.proposal_records] + [p.model_dump(mode="json") for p in handoff.proposal_records]
            keys = {"proposal_id": "proposal_id", "proposal_sequence": "proposal_sequence", "parameters_fingerprint": "params_fingerprint", "proposal_status": "status", "scientific_trial_id": "scientific_trial_id", "contract_sha256": "contract_hash"}
            if len(rows) != len(expected) or any(any(r[k] != p[v] for k,v in keys.items()) for r,p in zip(rows,expected)):
                raise AuthorityConflict("handoff proposal identities absent or different in authority")
            return snapshot, contract

    def record_proposal_wave(self, search_id, *, pre_snapshot, requested_count, records):
        from tools.research_search.governor import SearchGovernor

        records = json.loads(canonical_json([r.to_dict() if hasattr(r, "to_dict") else r for r in records]))
        with self._transaction() as conn:
            contract = self._load_contract(conn, search_id)
            self._search_active(conn, contract)
            replay = SearchGovernor.restore(contract, pre_snapshot)
            before = replay.proposal_count
            replay.propose_wave(requested_count)
            expected = json.loads(canonical_json([r.to_dict() for r in replay.proposal_records[before:]]))
            if expected != records:
                raise AuthorityConflict("Governor proposal replay divergence")
            payload = {"search_id": search_id, "wave_id": records[0]["wave_id"],
                "pre_snapshot_hash": pre_snapshot["snapshot_hash"], "requested_count": requested_count,
                "proposal_identities": [{key: r[key] for key in ("proposal_id", "proposal_sequence", "params_fingerprint", "status", "scientific_trial_id", "contract_hash")} for r in records]}
            event_id = f"wave:{search_id}:{records[0]['wave_id']}"
            replayed = self._replay(conn, event_id, "proposal_wave", payload)
            if replayed:
                return self._prior_outcome(replayed)
            c = self._campaign(conn, contract.campaign_id)
            s = conn.execute("SELECT state FROM research_authority.search_lineage WHERE search_id=%s", (search_id,)).fetchone()
            if s["state"] != "open":
                raise AuthorityConflict("search finalized")
            prior = conn.execute("SELECT count(*) AS p, count(scientific_trial_id) AS t FROM research_authority.proposal_record WHERE search_id=%s", (search_id,)).fetchone()
            if prior["p"] != before or prior["t"] != pre_snapshot["scientific_denominator"]:
                raise AuthorityConflict("pre-wave durable history mismatch")
            stored_prior = conn.execute("SELECT proposal_id,proposal_sequence,parameters_fingerprint,proposal_status,scientific_trial_id FROM research_authority.proposal_record WHERE search_id=%s ORDER BY proposal_sequence", (search_id,)).fetchall()
            keys = {"proposal_id": "proposal_id", "proposal_sequence": "proposal_sequence", "parameters_fingerprint": "params_fingerprint", "proposal_status": "status", "scientific_trial_id": "scientific_trial_id"}
            if len(stored_prior) != len(pre_snapshot["proposal_records"]) or any(any(r[k] != p[v] for k,v in keys.items()) for r,p in zip(stored_prior,pre_snapshot["proposal_records"])):
                raise AuthorityConflict("pre-wave identity history mismatch")
            accepted = {r["parameters_fingerprint"]: r["proposal_id"] for r in stored_prior if r["scientific_trial_id"] is not None}
            if pre_snapshot["accepted_by_fingerprint"] != accepted:
                raise AuthorityConflict("pre-wave dedup history mismatch")
            trials = sum(r["scientific_trial_id"] is not None for r in records)
            reservation = conn.execute("SELECT * FROM research_authority.search_budget_reservation WHERE search_id=%s FOR UPDATE", (search_id,)).fetchone()
            if reservation["proposals_remaining"] < len(records) or reservation["trials_remaining"] < trials:
                raise AuthorityConflict("wave exceeds remaining reservation")
            for r in records:
                conn.execute("INSERT INTO research_authority.proposal_record VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (r["proposal_id"], r["proposal_sequence"], r["params_fingerprint"], r["status"], r["scientific_trial_id"], search_id, contract.campaign_id, contract.contract_hash))
                if r["scientific_trial_id"]:
                    conn.execute("INSERT INTO research_authority.scientific_trial VALUES (%s,%s)", (r["scientific_trial_id"], r["proposal_id"]))
            conn.execute("UPDATE research_authority.search_budget_reservation SET proposals_remaining=proposals_remaining-%s,trials_remaining=trials_remaining-%s WHERE search_id=%s", (len(records), trials, search_id))
            conn.execute("UPDATE research_authority.campaign_state SET proposals_used=proposals_used+%s,scientific_trials_used=scientific_trials_used+%s,reserved_proposals=reserved_proposals-%s,reserved_trials=reserved_trials-%s WHERE campaign_id=%s", (len(records), trials, len(records), trials, contract.campaign_id))
            self._audit(conn, event_id=event_id, event_type="proposal_wave", payload=payload, campaign=c)
            return self._snapshot(conn, contract.campaign_id)

    def record_software_attempt(self, scientific_trial_id, *, attempt_number):
        with self._transaction() as conn:
            row = conn.execute("SELECT p.* FROM research_authority.scientific_trial t JOIN research_authority.proposal_record p USING(proposal_id) WHERE t.scientific_trial_id=%s", (scientific_trial_id,)).fetchone()
            if row is None:
                raise AuthorityConflict("scientific trial absent")
            contract = self._load_contract(conn, row["search_id"])
            if type(attempt_number) is not int or not 1 <= attempt_number <= contract.policies.retry_limit + 1:
                raise AuthorityConflict("same-trial software retry limit exhausted")
            payload = {"scientific_trial_id": scientific_trial_id, "attempt_number": attempt_number, "state": "SOFTWARE_FAILED"}
            event_id = f"attempt:{scientific_trial_id}:{attempt_number}"
            if self._replay(conn, event_id, "trial_attempt", payload):
                return
            last = conn.execute("SELECT coalesce(max(attempt_number),0) AS n FROM research_authority.trial_attempt WHERE scientific_trial_id=%s", (scientific_trial_id,)).fetchone()["n"]
            if last + 1 != attempt_number:
                raise AuthorityConflict("trial attempt sequence mismatch")
            conn.execute("INSERT INTO research_authority.trial_attempt VALUES (%s,%s,'SOFTWARE_FAILED')", (scientific_trial_id, attempt_number))
            self._audit(conn, event_id=event_id, event_type="trial_attempt", payload=payload, campaign=self._campaign(conn, row["campaign_id"]))

    def finalize_search(self, search_id):
        with self._transaction() as conn:
            contract = self._load_contract(conn, search_id)
            payload = {"search_id": search_id, "contract_hash": contract.contract_hash}
            replayed = self._replay(conn, f"finalize:{search_id}", "finalize_search", payload)
            if replayed:
                return self._prior_outcome(replayed)
            if not replayed:
                c = self._campaign(conn, contract.campaign_id)
                r = conn.execute("SELECT * FROM research_authority.search_budget_reservation WHERE search_id=%s FOR UPDATE", (search_id,)).fetchone()
                conn.execute("UPDATE research_authority.search_lineage SET state='finalized' WHERE search_id=%s", (search_id,))
                conn.execute("UPDATE research_authority.search_budget_reservation SET proposals_remaining=0,trials_remaining=0,state='released' WHERE search_id=%s", (search_id,))
                conn.execute("UPDATE research_authority.campaign_state SET reserved_proposals=reserved_proposals-%s,reserved_trials=reserved_trials-%s WHERE campaign_id=%s", (r["proposals_remaining"], r["trials_remaining"], contract.campaign_id))
                self._audit(conn, event_id=f"finalize:{search_id}", event_type="finalize_search", payload=payload, campaign=c)
            return self._snapshot(conn, contract.campaign_id)

    def record_holdout_event(self, search_id, *, event_id, informative_escape: bool):
        if type(informative_escape) is not bool:
            raise ValueError("explicit informative-escape boolean required")
        with self._transaction() as conn:
            contract = self._load_contract(conn, search_id)
            c = self._campaign(conn, contract.campaign_id)
            payload = {"search_id": search_id, "campaign_id": contract.campaign_id, "domain": c["contamination_domain_id"], "holdout_id": c["holdout_id"], "informative_escape": informative_escape}
            kind = "holdout_escape" if informative_escape else "holdout_attempt"
            replayed = self._replay(conn, event_id, kind, payload)
            if replayed:
                return self._prior_outcome(replayed).holdout
            state = conn.execute("SELECT state FROM research_authority.holdout_state WHERE contamination_domain_id=%s AND holdout_id=%s FOR UPDATE", (c["contamination_domain_id"], c["holdout_id"])).fetchone()["state"]
            if state == "consumed":
                raise AuthorityConflict("holdout permanently consumed")
            conn.execute("UPDATE research_authority.holdout_state SET state=%s,source_search_id=%s,source_campaign_id=%s WHERE contamination_domain_id=%s AND holdout_id=%s", ("consumed" if informative_escape else "attempted_isolated", search_id, contract.campaign_id, c["contamination_domain_id"], c["holdout_id"]))
            if informative_escape:
                conn.execute("INSERT INTO research_authority.contamination_edge VALUES (%s,%s,%s,%s,%s)", (event_id, c["contamination_domain_id"], c["holdout_id"], search_id, contract.campaign_id))
            self._audit(conn, event_id=event_id, event_type=kind, payload=payload, campaign=c)
            return self._snapshot(conn, contract.campaign_id).holdout

    def attach_evidence(self, search_id, *, reference_id, binding, repo_root: Path):
        from .contract_builder import verify_evidence

        contract = self.load_contract(search_id)
        verify_evidence(repo_root, binding, repo_sha=contract.repo_sha)
        payload = {"reference_id": reference_id, "search_id": search_id, "evidence": binding.model_dump(mode="json")}
        with self._transaction() as conn:
            if self._replay(conn, f"reference:{reference_id}", "evidence_reference", payload):
                return
            c = self._campaign(conn, contract.campaign_id)
            conn.execute("INSERT INTO research_authority.evidence_reference VALUES (%s,%s,%s,%s,%s,%s)", (reference_id, contract.campaign_id, search_id, binding.repo_path, binding.repo_sha, binding.artifact_sha256))
            self._audit(conn, event_id=f"reference:{reference_id}", event_type="evidence_reference", payload=payload, campaign=c)
