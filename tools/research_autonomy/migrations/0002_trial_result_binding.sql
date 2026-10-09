-- Additive terminal evidence; metrics remain in noncanonical scratch artifacts.
ALTER TABLE research_authority.authority_audit DROP CONSTRAINT authority_audit_event_type_check;
ALTER TABLE research_authority.authority_audit ADD CONSTRAINT authority_audit_event_type_check
 CHECK(event_type IN ('register_envelope','control_envelope','open_campaign','open_search',
 'proposal_wave','trial_attempt','trial_result','finalize_search','holdout_attempt','holdout_escape','evidence_reference'));
ALTER TABLE research_authority.proposal_record ADD CONSTRAINT proposal_result_identity
 UNIQUE(proposal_id,scientific_trial_id,search_id,campaign_id,contract_sha256,parameters_fingerprint);
ALTER TABLE research_authority.authority_audit ADD CONSTRAINT audit_result_identity UNIQUE(event_id,campaign_id);

CREATE TABLE research_authority.trial_result_binding (
 scientific_trial_id TEXT NOT NULL,
 attempt_number INTEGER NOT NULL CHECK(attempt_number > 0),
 idempotency_id TEXT NOT NULL UNIQUE,
 campaign_id TEXT NOT NULL,
 search_id TEXT NOT NULL,
 contract_sha256 TEXT NOT NULL,
 proposal_id TEXT NOT NULL,
 variant_id TEXT NOT NULL CHECK(variant_id ~ '^VAR-[0-9]{6}$'),
 parameters_fingerprint TEXT NOT NULL,
 approval_id TEXT NOT NULL,
 approval_sha256 TEXT NOT NULL CHECK(approval_sha256 ~ '^sha256:[0-9a-f]{64}$'),
 prepared_spec_sha256 TEXT NOT NULL CHECK(prepared_spec_sha256 ~ '^sha256:[0-9a-f]{64}$'),
 prepared_vm_sha256 TEXT NOT NULL CHECK(prepared_vm_sha256 ~ '^sha256:[0-9a-f]{64}$'),
 prepared_sweep_sha256 TEXT NOT NULL CHECK(prepared_sweep_sha256 ~ '^sha256:[0-9a-f]{64}$'),
 runner_result_sha256 TEXT NOT NULL CHECK(runner_result_sha256 ~ '^sha256:[0-9a-f]{64}$'),
 fold_sha256 TEXT CHECK(fold_sha256 ~ '^sha256:[0-9a-f]{64}$'),
 robustness_sha256 TEXT CHECK(robustness_sha256 ~ '^sha256:[0-9a-f]{64}$'),
 classification TEXT NOT NULL CHECK(classification IN ('PERFORMANCE_RESULT','SOFTWARE_FAILED')),
 evidence_payload TEXT NOT NULL CHECK(jsonb_typeof(evidence_payload::jsonb)='object'),
 evidence_sha256 TEXT NOT NULL CHECK(evidence_sha256 ~ '^sha256:[0-9a-f]{64}$'),
 audit_event_id TEXT NOT NULL UNIQUE,
 PRIMARY KEY(scientific_trial_id,attempt_number),
 FOREIGN KEY(proposal_id,scientific_trial_id,search_id,campaign_id,contract_sha256,parameters_fingerprint)
 REFERENCES research_authority.proposal_record(proposal_id,scientific_trial_id,search_id,campaign_id,contract_sha256,parameters_fingerprint),
 FOREIGN KEY(scientific_trial_id) REFERENCES research_authority.scientific_trial,
 FOREIGN KEY(audit_event_id,campaign_id) REFERENCES research_authority.authority_audit(event_id,campaign_id)
 DEFERRABLE INITIALLY DEFERRED
);
CREATE UNIQUE INDEX one_performance_result_per_trial ON research_authority.trial_result_binding(scientific_trial_id)
 WHERE classification='PERFORMANCE_RESULT';
CREATE TRIGGER immutable_rows BEFORE UPDATE OR DELETE ON research_authority.trial_result_binding
 FOR EACH ROW EXECUTE FUNCTION research_authority.deny_mutation();
CREATE TRIGGER immutable_truncate BEFORE TRUNCATE ON research_authority.trial_result_binding
 FOR EACH STATEMENT EXECUTE FUNCTION research_authority.deny_mutation();

CREATE FUNCTION research_authority.guard_trial_result() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE event research_authority.authority_audit; payload JSONB; last_attempt INTEGER; retry_limit INTEGER;
BEGIN
 PERFORM pg_advisory_xact_lock(721026002);
 SELECT * INTO event FROM research_authority.authority_audit WHERE event_id=NEW.audit_event_id;
 payload := NEW.evidence_payload::jsonb;
 IF (SELECT array_agg(key ORDER BY key) FROM jsonb_object_keys(payload) AS key) IS DISTINCT FROM
    ARRAY['approval_id','approval_sha256','attempt_number','authority_lineage_sha256','authority_lineage_version',
    'campaign_id','classification','contract_hash','embargo_bars','fold_binding','fold_manifest_binding','fold_sha256',
    'idempotency_id','mapping_binding','params_fingerprint','prepared_hashes','proposal_id','purge_bars',
    'robustness_binding','robustness_sha256','runner_result_sha256','scientific_trial_id','search_id','summary_binding','variant_id'] OR
    NEW.variant_id IS DISTINCT FROM (SELECT 'VAR-' || lpad((proposal_sequence+1)::text,6,'0')
      FROM research_authority.proposal_record WHERE proposal_id=NEW.proposal_id) THEN
    RAISE EXCEPTION 'closed trial evidence metadata and exact variant identity required';
 END IF;
 IF NEW.evidence_sha256 <> 'sha256:' || encode(sha256(convert_to(NEW.evidence_payload,'UTF8')),'hex') OR
    event.event_type IS DISTINCT FROM (CASE WHEN NEW.classification='SOFTWARE_FAILED' THEN 'trial_attempt' ELSE 'trial_result' END) OR
    event.campaign_id IS DISTINCT FROM NEW.campaign_id OR
    event.normalized_payload::jsonb->'input' IS DISTINCT FROM payload OR
    NOT EXISTS(SELECT 1 FROM research_authority.authority_audit WHERE event_id=NEW.audit_event_id AND xmin::text::bigint=txid_current()%4294967296) THEN
    RAISE EXCEPTION 'trial result lacks exact same-transaction audit';
 END IF;
 IF (payload->>'scientific_trial_id',payload->>'proposal_id',payload->>'campaign_id',payload->>'search_id',
     payload->>'contract_hash',payload->>'variant_id',payload->>'params_fingerprint',payload->>'classification',
     payload->>'idempotency_id',(payload->>'attempt_number')::integer,payload->>'approval_id',payload->>'approval_sha256',
     payload->'prepared_hashes'->>'spec',payload->'prepared_hashes'->>'vm',payload->'prepared_hashes'->>'sweep',
     payload->>'runner_result_sha256',payload->>'fold_sha256',payload->>'robustness_sha256') IS DISTINCT FROM
    (NEW.scientific_trial_id,NEW.proposal_id,NEW.campaign_id,NEW.search_id,NEW.contract_sha256,NEW.variant_id,
     NEW.parameters_fingerprint,NEW.classification,NEW.idempotency_id,NEW.attempt_number,NEW.approval_id,
     NEW.approval_sha256,NEW.prepared_spec_sha256,NEW.prepared_vm_sha256,NEW.prepared_sweep_sha256,
     NEW.runner_result_sha256,NEW.fold_sha256,NEW.robustness_sha256) THEN
    RAISE EXCEPTION 'trial result column/payload mismatch';
 END IF;
 SELECT coalesce(max(attempt_number),0) INTO last_attempt FROM research_authority.trial_attempt
 WHERE scientific_trial_id=NEW.scientific_trial_id;
 SELECT (contract_payload::jsonb->'policies'->>'retry_limit')::integer INTO retry_limit
 FROM research_authority.search_lineage WHERE search_id=NEW.search_id;
 IF NEW.attempt_number > retry_limit+1 OR
    NEW.attempt_number <> last_attempt + (CASE WHEN NEW.classification='SOFTWARE_FAILED' THEN 0 ELSE 1 END) OR
    (NEW.classification='SOFTWARE_FAILED' AND NOT EXISTS(SELECT 1 FROM research_authority.trial_attempt
        WHERE scientific_trial_id=NEW.scientific_trial_id AND attempt_number=NEW.attempt_number)) THEN
    RAISE EXCEPTION 'trial result retry sequence mismatch';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM research_authority.search_lineage s JOIN research_authority.envelope_control_state e
 USING(envelope_id,envelope_version) JOIN research_authority.campaign_state c USING(campaign_id)
 JOIN research_authority.holdout_state h ON h.contamination_domain_id=c.contamination_domain_id AND h.holdout_id=c.holdout_id
 WHERE s.search_id=NEW.search_id AND s.state='open' AND e.state='active' AND c.state='open' AND h.state='unexposed') OR
 EXISTS(SELECT 1 FROM research_authority.contamination_edge x JOIN research_authority.campaign_state c
 USING(contamination_domain_id) WHERE c.campaign_id=NEW.campaign_id) THEN
    RAISE EXCEPTION 'trial result active unexposed authority required';
 END IF;
 RETURN NULL;
END;
$$;
CREATE CONSTRAINT TRIGGER trial_result_audit AFTER INSERT ON research_authority.trial_result_binding
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.guard_trial_result();

CREATE FUNCTION research_authority.guard_attempt_after_result() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 PERFORM pg_advisory_xact_lock(721026002);
 IF EXISTS(SELECT 1 FROM research_authority.trial_result_binding
 WHERE scientific_trial_id=NEW.scientific_trial_id AND classification='PERFORMANCE_RESULT') THEN
    RAISE EXCEPTION 'terminal scientific trial cannot retry';
 END IF;
 RETURN NEW;
END;
$$;
CREATE TRIGGER trial_attempt_terminal BEFORE INSERT ON research_authority.trial_attempt
 FOR EACH ROW EXECUTE FUNCTION research_authority.guard_attempt_after_result();
