-- Scientific identities and counters only; no performance payloads.
CREATE TABLE research_authority.envelope_registry (
    envelope_id TEXT NOT NULL,
    envelope_version INTEGER NOT NULL CHECK (envelope_version > 0),
    content_sha256 TEXT NOT NULL CHECK (content_sha256 ~ '^sha256:[0-9a-f]{64}$'),
    repo_sha TEXT NOT NULL CHECK (repo_sha ~ '^[0-9a-f]{40}$'),
    approved_by TEXT NOT NULL CHECK (approved_by = 'Karl'),
    approved_at TIMESTAMPTZ NOT NULL,
    semantic_payload TEXT NOT NULL CHECK (jsonb_typeof(semantic_payload::jsonb) = 'object'),
    registered_at TIMESTAMPTZ NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (envelope_id, envelope_version),
    UNIQUE (envelope_id, envelope_version, content_sha256)
);

CREATE TABLE research_authority.authority_audit (
    event_id TEXT PRIMARY KEY,
    campaign_id TEXT,
    event_type TEXT NOT NULL CHECK (event_type IN ('register_envelope', 'control_envelope', 'open_campaign', 'open_search', 'proposal_wave', 'trial_attempt', 'finalize_search', 'holdout_attempt', 'holdout_escape', 'evidence_reference')),
    event_sequence BIGINT NOT NULL CHECK (event_sequence > 0),
    previous_lineage_sha256 TEXT NOT NULL CHECK (previous_lineage_sha256 ~ '^sha256:[0-9a-f]{64}$'),
    normalized_payload TEXT NOT NULL CHECK (jsonb_typeof(normalized_payload::jsonb) = 'object'),
    event_content_sha256 TEXT NOT NULL CHECK (event_content_sha256 ~ '^sha256:[0-9a-f]{64}$'),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT transaction_timestamp(),
    UNIQUE (campaign_id, event_sequence),
    UNIQUE (campaign_id, event_sequence, event_content_sha256)
);

CREATE TABLE research_authority.envelope_control_state (
    envelope_id TEXT NOT NULL,
    envelope_version INTEGER NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('active', 'revoked', 'replaced')),
    control_action TEXT,
    last_event_id TEXT NOT NULL REFERENCES research_authority.authority_audit(event_id) DEFERRABLE INITIALLY DEFERRED,
    PRIMARY KEY (envelope_id, envelope_version),
    FOREIGN KEY (envelope_id, envelope_version) REFERENCES research_authority.envelope_registry,
    CHECK ((state = 'active') = (control_action IS NULL))
);

CREATE TABLE research_authority.campaign_state (
    campaign_id TEXT PRIMARY KEY,
    envelope_id TEXT NOT NULL,
    envelope_version INTEGER NOT NULL,
    envelope_content_sha256 TEXT NOT NULL,
    contamination_domain_id TEXT NOT NULL,
    holdout_id TEXT NOT NULL,
    hypothesis_fingerprint TEXT NOT NULL,
    proposal_ceiling BIGINT NOT NULL CHECK (proposal_ceiling > 0),
    trial_ceiling BIGINT NOT NULL CHECK (trial_ceiling > 0),
    search_ceiling BIGINT NOT NULL CHECK (search_ceiling > 0),
    proposals_used BIGINT NOT NULL DEFAULT 0 CHECK (proposals_used >= 0),
    scientific_trials_used BIGINT NOT NULL DEFAULT 0 CHECK (scientific_trials_used >= 0),
    reserved_proposals BIGINT NOT NULL DEFAULT 0 CHECK (reserved_proposals >= 0),
    reserved_trials BIGINT NOT NULL DEFAULT 0 CHECK (reserved_trials >= 0),
    search_count BIGINT NOT NULL DEFAULT 0 CHECK (search_count >= 0),
    lineage_version BIGINT NOT NULL DEFAULT 0 CHECK (lineage_version >= 0),
    lineage_sha256 TEXT NOT NULL CHECK (lineage_sha256 ~ '^sha256:[0-9a-f]{64}$'),
    state TEXT NOT NULL CHECK (state IN ('open', 'closed')),
    FOREIGN KEY (envelope_id, envelope_version, envelope_content_sha256) REFERENCES research_authority.envelope_registry(envelope_id, envelope_version, content_sha256),
    CHECK (proposals_used + reserved_proposals <= proposal_ceiling),
    CHECK (scientific_trials_used + reserved_trials <= trial_ceiling),
    CHECK (search_count <= search_ceiling)
);

ALTER TABLE research_authority.authority_audit ADD FOREIGN KEY (campaign_id)
    REFERENCES research_authority.campaign_state DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE research_authority.search_lineage (
    search_id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL REFERENCES research_authority.campaign_state,
    parent_search_id TEXT REFERENCES research_authority.search_lineage,
    reason_for_change TEXT,
    contract_sha256 TEXT NOT NULL CHECK (contract_sha256 ~ '^sha256:[0-9a-f]{64}$'),
    contract_payload TEXT NOT NULL CHECK (jsonb_typeof(contract_payload::jsonb) = 'object'),
    envelope_id TEXT NOT NULL,
    envelope_version INTEGER NOT NULL,
    envelope_content_sha256 TEXT NOT NULL,
    pre_lineage_version BIGINT NOT NULL CHECK (pre_lineage_version > 0),
    pre_lineage_sha256 TEXT NOT NULL,
    proposals_before_search BIGINT NOT NULL CHECK (proposals_before_search >= 0),
    trials_before_search BIGINT NOT NULL CHECK (trials_before_search >= 0),
    reserved_proposals BIGINT NOT NULL CHECK (reserved_proposals > 0),
    reserved_trials BIGINT NOT NULL CHECK (reserved_trials > 0),
    state TEXT NOT NULL CHECK (state IN ('open', 'finalized')),
    FOREIGN KEY (envelope_id, envelope_version, envelope_content_sha256) REFERENCES research_authority.envelope_registry(envelope_id, envelope_version, content_sha256),
    FOREIGN KEY (campaign_id, pre_lineage_version, pre_lineage_sha256) REFERENCES research_authority.authority_audit(campaign_id, event_sequence, event_content_sha256),
    UNIQUE (search_id, campaign_id, contract_sha256),
    CHECK ((parent_search_id IS NULL) = (reason_for_change IS NULL)),
    CHECK (parent_search_id IS NULL OR parent_search_id <> search_id)
);
CREATE UNIQUE INDEX one_successor_per_parent ON research_authority.search_lineage(parent_search_id)
    WHERE parent_search_id IS NOT NULL;
CREATE UNIQUE INDEX one_initial_per_campaign ON research_authority.search_lineage(campaign_id)
    WHERE parent_search_id IS NULL;

CREATE TABLE research_authority.search_budget_reservation (
    search_id TEXT PRIMARY KEY REFERENCES research_authority.search_lineage,
    proposals_remaining BIGINT NOT NULL CHECK (proposals_remaining >= 0),
    trials_remaining BIGINT NOT NULL CHECK (trials_remaining >= 0),
    state TEXT NOT NULL CHECK (state IN ('active', 'released')),
    CHECK (state <> 'released' OR (proposals_remaining = 0 AND trials_remaining = 0))
);

CREATE TABLE research_authority.proposal_record (
    proposal_id TEXT PRIMARY KEY,
    proposal_sequence BIGINT NOT NULL CHECK (proposal_sequence >= 0),
    parameters_fingerprint TEXT NOT NULL CHECK (parameters_fingerprint ~ '^sha256:[0-9a-f]{64}$'),
    proposal_status TEXT NOT NULL CHECK (proposal_status IN ('ACCEPTED_FOR_SCIENTIFIC_EXECUTION', 'REJECTED_INVALID', 'DUPLICATE_NOT_NEW_OBSERVATION')),
    scientific_trial_id TEXT UNIQUE,
    search_id TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    contract_sha256 TEXT NOT NULL,
    FOREIGN KEY (search_id, campaign_id, contract_sha256) REFERENCES research_authority.search_lineage(search_id, campaign_id, contract_sha256),
    UNIQUE (search_id, proposal_sequence),
    UNIQUE (proposal_id, scientific_trial_id),
    CHECK ((proposal_status = 'ACCEPTED_FOR_SCIENTIFIC_EXECUTION') = (scientific_trial_id IS NOT NULL))
);

CREATE TABLE research_authority.scientific_trial (
    scientific_trial_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL UNIQUE,
    FOREIGN KEY (proposal_id, scientific_trial_id) REFERENCES research_authority.proposal_record(proposal_id, scientific_trial_id)
);
CREATE TABLE research_authority.trial_attempt (
    scientific_trial_id TEXT NOT NULL REFERENCES research_authority.scientific_trial,
    attempt_number INTEGER NOT NULL CHECK (attempt_number > 0),
    state TEXT NOT NULL CHECK (state = 'SOFTWARE_FAILED'),
    PRIMARY KEY (scientific_trial_id, attempt_number)
);

CREATE TABLE research_authority.holdout_state (
    contamination_domain_id TEXT NOT NULL,
    holdout_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('unexposed', 'attempted_isolated', 'consumed')),
    source_search_id TEXT REFERENCES research_authority.search_lineage,
    source_campaign_id TEXT REFERENCES research_authority.campaign_state,
    PRIMARY KEY (contamination_domain_id, holdout_id),
    UNIQUE (holdout_id),
    CHECK (state <> 'consumed' OR (source_search_id IS NOT NULL AND source_campaign_id IS NOT NULL))
);
CREATE TABLE research_authority.contamination_edge (
    event_id TEXT PRIMARY KEY REFERENCES research_authority.authority_audit DEFERRABLE INITIALLY DEFERRED,
    contamination_domain_id TEXT NOT NULL,
    holdout_id TEXT NOT NULL,
    source_search_id TEXT NOT NULL REFERENCES research_authority.search_lineage,
    source_campaign_id TEXT NOT NULL REFERENCES research_authority.campaign_state,
    FOREIGN KEY (contamination_domain_id, holdout_id) REFERENCES research_authority.holdout_state
);
CREATE TABLE research_authority.evidence_reference (
    reference_id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL REFERENCES research_authority.campaign_state,
    search_id TEXT NOT NULL REFERENCES research_authority.search_lineage,
    repo_path TEXT NOT NULL,
    repo_sha TEXT NOT NULL CHECK (repo_sha ~ '^[0-9a-f]{40}$'),
    content_sha256 TEXT NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$')
);

CREATE FUNCTION research_authority.deny_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'immutable scientific authority table: %', TG_TABLE_NAME;
END;
$$;

DO $$ DECLARE name TEXT; BEGIN
    FOREACH name IN ARRAY ARRAY['envelope_registry', 'authority_audit', 'proposal_record', 'scientific_trial', 'trial_attempt', 'contamination_edge', 'evidence_reference', 'schema_migrations'] LOOP
        EXECUTE format('CREATE TRIGGER immutable_rows BEFORE UPDATE OR DELETE ON research_authority.%I FOR EACH ROW EXECUTE FUNCTION research_authority.deny_mutation()', name);
        EXECUTE format('CREATE TRIGGER immutable_truncate BEFORE TRUNCATE ON research_authority.%I FOR EACH STATEMENT EXECUTE FUNCTION research_authority.deny_mutation()', name);
    END LOOP;
END $$;

CREATE FUNCTION research_authority.guard_transition() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP IN ('DELETE', 'TRUNCATE') THEN
        RAISE EXCEPTION 'authority state cannot be erased';
    END IF;
    IF TG_TABLE_NAME = 'campaign_state' THEN
        IF (to_jsonb(NEW) - ARRAY['proposals_used', 'scientific_trials_used', 'reserved_proposals', 'reserved_trials', 'search_count', 'lineage_version', 'lineage_sha256', 'state']) IS DISTINCT FROM
           (to_jsonb(OLD) - ARRAY['proposals_used', 'scientific_trials_used', 'reserved_proposals', 'reserved_trials', 'search_count', 'lineage_version', 'lineage_sha256', 'state']) OR
           NEW.proposals_used < OLD.proposals_used OR NEW.scientific_trials_used < OLD.scientific_trials_used OR
           NEW.search_count < OLD.search_count OR NEW.lineage_version < OLD.lineage_version OR
           NEW.state <> OLD.state THEN
            RAISE EXCEPTION 'illegal campaign transition';
        END IF;
    ELSIF TG_TABLE_NAME = 'search_lineage' THEN
        IF (to_jsonb(NEW) - 'state') IS DISTINCT FROM (to_jsonb(OLD) - 'state') OR OLD.state <> 'open' OR NEW.state <> 'finalized' THEN
            RAISE EXCEPTION 'illegal search transition';
        END IF;
    ELSIF TG_TABLE_NAME = 'envelope_control_state' THEN
        IF NEW.envelope_id <> OLD.envelope_id OR NEW.envelope_version <> OLD.envelope_version OR OLD.state <> 'active' OR NEW.state = 'active' THEN
            RAISE EXCEPTION 'illegal envelope control transition';
        END IF;
    ELSIF TG_TABLE_NAME = 'holdout_state' THEN
        IF NEW.contamination_domain_id <> OLD.contamination_domain_id OR NEW.holdout_id <> OLD.holdout_id OR
           OLD.state = 'consumed' OR NEW.state = 'unexposed' THEN
            RAISE EXCEPTION 'illegal holdout transition';
        END IF;
    ELSIF TG_TABLE_NAME = 'search_budget_reservation' THEN
        IF NEW.search_id <> OLD.search_id OR OLD.state <> 'active' OR NEW.proposals_remaining > OLD.proposals_remaining OR NEW.trials_remaining > OLD.trials_remaining THEN
            RAISE EXCEPTION 'illegal reservation transition';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
DO $$ DECLARE name TEXT; BEGIN
    FOREACH name IN ARRAY ARRAY['campaign_state', 'search_lineage', 'envelope_control_state', 'holdout_state', 'search_budget_reservation'] LOOP
        EXECUTE format('CREATE TRIGGER guarded_rows BEFORE UPDATE OR DELETE ON research_authority.%I FOR EACH ROW EXECUTE FUNCTION research_authority.guard_transition()', name);
        EXECUTE format('CREATE TRIGGER guarded_truncate BEFORE TRUNCATE ON research_authority.%I FOR EACH STATEMENT EXECUTE FUNCTION research_authority.guard_transition()', name);
    END LOOP;
END $$;

CREATE FUNCTION research_authority.guard_audit_insert() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE current_version BIGINT; current_hash TEXT; payload JSONB;
BEGIN
    payload := NEW.normalized_payload::jsonb;
    IF (payload->>'campaign_id') IS DISTINCT FROM NEW.campaign_id OR
       (payload->>'event_type') IS DISTINCT FROM NEW.event_type OR
       (payload->>'event_sequence')::bigint IS DISTINCT FROM NEW.event_sequence OR
       (payload->>'previous_lineage_sha256') IS DISTINCT FROM NEW.previous_lineage_sha256 OR
       jsonb_typeof(payload->'input') IS DISTINCT FROM 'object' THEN
        RAISE EXCEPTION 'audit normalized metadata mismatch';
    END IF;
    IF NEW.event_content_sha256 <> 'sha256:' || encode(sha256(convert_to(NEW.normalized_payload, 'UTF8')), 'hex') THEN
        RAISE EXCEPTION 'audit content hash mismatch';
    END IF;
    IF NEW.campaign_id IS NOT NULL THEN
        SELECT lineage_version, lineage_sha256 INTO current_version, current_hash
            FROM research_authority.campaign_state WHERE campaign_id = NEW.campaign_id FOR UPDATE;
        IF current_version IS NULL OR NEW.event_sequence <> current_version + 1 OR NEW.previous_lineage_sha256 <> current_hash THEN
            RAISE EXCEPTION 'audit lineage discontinuity';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER hash_chain BEFORE INSERT ON research_authority.authority_audit
    FOR EACH ROW EXECUTE FUNCTION research_authority.guard_audit_insert();

-- At commit, current counters must equal retained scientific identities and reservations.
CREATE FUNCTION research_authority.check_campaign_integrity() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE c research_authority.campaign_state; n BIGINT; p BIGINT; t BIGINT; rp BIGINT; rt BIGINT;
BEGIN
    SELECT * INTO c FROM research_authority.campaign_state WHERE campaign_id = NEW.campaign_id;
    SELECT count(*) INTO n FROM research_authority.search_lineage WHERE campaign_id = c.campaign_id;
    SELECT count(*), count(scientific_trial_id) INTO p,t FROM research_authority.proposal_record WHERE campaign_id = c.campaign_id;
    SELECT coalesce(sum(r.proposals_remaining),0), coalesce(sum(r.trials_remaining),0) INTO rp,rt
        FROM research_authority.search_budget_reservation r JOIN research_authority.search_lineage s USING(search_id)
        WHERE s.campaign_id = c.campaign_id;
    IF c.campaign_id IS NULL THEN RETURN NULL; END IF;
    IF (c.search_count,c.proposals_used,c.scientific_trials_used,c.reserved_proposals,c.reserved_trials) IS DISTINCT FROM (n,p,t,rp,rt) OR
       c.lineage_version <> (SELECT count(*) FROM research_authority.authority_audit WHERE campaign_id=c.campaign_id) OR
       NOT EXISTS (SELECT 1 FROM research_authority.authority_audit WHERE campaign_id = c.campaign_id AND event_sequence = c.lineage_version AND event_content_sha256 = c.lineage_sha256
           AND xmin::text::bigint = txid_current() % 4294967296) OR
       t <> (SELECT count(*) FROM research_authority.scientific_trial st JOIN research_authority.proposal_record pr USING(proposal_id) WHERE pr.campaign_id=c.campaign_id) OR
       EXISTS(SELECT 1 FROM research_authority.search_lineage s LEFT JOIN research_authority.search_budget_reservation r USING(search_id)
           WHERE s.campaign_id=c.campaign_id AND (r.search_id IS NULL OR (s.state='open') IS DISTINCT FROM (r.state='active'))) THEN
        RAISE EXCEPTION 'campaign counters or audit binding mismatch';
    END IF;
    RETURN NULL;
END;
$$;
CREATE CONSTRAINT TRIGGER campaign_integrity AFTER INSERT OR UPDATE ON research_authority.campaign_state
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.check_campaign_integrity();
CREATE CONSTRAINT TRIGGER audit_current_binding AFTER INSERT ON research_authority.authority_audit
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.check_campaign_integrity();
CREATE CONSTRAINT TRIGGER proposal_conservation AFTER INSERT ON research_authority.proposal_record
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.check_campaign_integrity();
CREATE CONSTRAINT TRIGGER search_conservation AFTER INSERT OR UPDATE ON research_authority.search_lineage
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.check_campaign_integrity();

CREATE FUNCTION research_authority.guard_scientific_insert() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE c research_authority.campaign_state; envelope JSONB; contract JSONB; parent research_authority.search_lineage;
BEGIN
    IF TG_TABLE_NAME = 'campaign_state' THEN
        SELECT semantic_payload::jsonb INTO envelope FROM research_authority.envelope_registry
            WHERE envelope_id=NEW.envelope_id AND envelope_version=NEW.envelope_version AND content_sha256=NEW.envelope_content_sha256;
        IF envelope IS NULL OR NEW.contamination_domain_id IS DISTINCT FROM envelope->>'contamination_domain_id' OR
            NOT EXISTS(SELECT 1 FROM jsonb_array_elements(envelope->'search_policy'->'split_protocols') split WHERE split->>'final_holdout_ref'=NEW.holdout_id) OR
            (NEW.proposal_ceiling,NEW.trial_ceiling,NEW.search_ceiling) IS DISTINCT FROM
            ((envelope->'budgets'->>'campaign_proposals')::bigint,(envelope->'budgets'->>'campaign_trials')::bigint,(envelope->'budgets'->>'campaign_searches')::bigint) OR
            (NEW.proposals_used,NEW.scientific_trials_used,NEW.reserved_proposals,NEW.reserved_trials,NEW.search_count,NEW.lineage_version) <> (0,0,0,0,0,0) THEN
            RAISE EXCEPTION 'campaign envelope ceiling or initial state mismatch';
        END IF;
    ELSIF TG_TABLE_NAME = 'search_lineage' THEN
        SELECT * INTO c FROM research_authority.campaign_state WHERE campaign_id=NEW.campaign_id FOR UPDATE;
        contract := NEW.contract_payload::jsonb;
        IF NEW.contract_sha256 <> 'sha256:' || encode(sha256(convert_to(NEW.contract_payload,'UTF8')),'hex') OR
            (NEW.envelope_id,NEW.envelope_version,NEW.envelope_content_sha256,NEW.pre_lineage_version,NEW.pre_lineage_sha256,NEW.proposals_before_search,NEW.trials_before_search) IS DISTINCT FROM
            (c.envelope_id,c.envelope_version,c.envelope_content_sha256,c.lineage_version,c.lineage_sha256,c.proposals_used,c.scientific_trials_used) OR
            (contract->>'campaign_id',contract->>'search_id') IS DISTINCT FROM (NEW.campaign_id,NEW.search_id) OR
            (contract->>'authority_lineage_version')::bigint <> c.lineage_version OR
            contract->>'authority_lineage_sha256' <> c.lineage_sha256 THEN
            RAISE EXCEPTION 'search durable authority binding mismatch';
        END IF;
        IF NEW.parent_search_id IS NOT NULL THEN
            SELECT * INTO parent FROM research_authority.search_lineage WHERE search_id=NEW.parent_search_id;
            IF parent.campaign_id IS DISTINCT FROM NEW.campaign_id OR parent.state <> 'finalized' THEN
                RAISE EXCEPTION 'successor requires finalized same-campaign parent';
            END IF;
        END IF;
    ELSIF TG_TABLE_NAME = 'holdout_state' THEN
        IF NEW.state <> 'unexposed' OR NEW.source_search_id IS NOT NULL OR NEW.source_campaign_id IS NOT NULL THEN
            RAISE EXCEPTION 'new holdout identity must start unexposed';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
DO $$ DECLARE name TEXT; BEGIN
    FOREACH name IN ARRAY ARRAY['campaign_state','search_lineage','holdout_state'] LOOP
        EXECUTE format('CREATE TRIGGER scientific_insert BEFORE INSERT ON research_authority.%I FOR EACH ROW EXECUTE FUNCTION research_authority.guard_scientific_insert()',name);
    END LOOP;
END $$;

CREATE FUNCTION research_authority.check_control_audit() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE event research_authority.authority_audit; payload JSONB;
BEGIN
    SELECT * INTO event FROM research_authority.authority_audit WHERE event_id=NEW.last_event_id;
    payload := event.normalized_payload::jsonb->'input';
    IF NOT EXISTS(SELECT 1 FROM research_authority.authority_audit WHERE event_id=NEW.last_event_id AND xmin::text::bigint=txid_current()%4294967296) OR
       (payload->>'envelope_id',(payload->>'envelope_version')::integer) IS DISTINCT FROM (NEW.envelope_id,NEW.envelope_version) OR
       (NEW.state='active' AND event.event_type <> 'register_envelope') OR
       (NEW.state<>'active' AND (event.event_type <> 'control_envelope' OR payload IS DISTINCT FROM NEW.control_action::jsonb OR
           NEW.state IS DISTINCT FROM CASE WHEN payload->>'action'='revoke' THEN 'revoked' WHEN payload->>'action'='replace' THEN 'replaced' ELSE NULL END)) THEN
        RAISE EXCEPTION 'control transition lacks matching immutable audit';
    END IF;
    RETURN NULL;
END;
$$;
CREATE CONSTRAINT TRIGGER control_audit AFTER INSERT OR UPDATE ON research_authority.envelope_control_state
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.check_control_audit();

CREATE FUNCTION research_authority.check_holdout_audit() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE c research_authority.campaign_state;
BEGIN
    SELECT * INTO c FROM research_authority.campaign_state WHERE campaign_id=NEW.source_campaign_id;
    IF c.contamination_domain_id IS DISTINCT FROM NEW.contamination_domain_id OR c.holdout_id IS DISTINCT FROM NEW.holdout_id OR
       NOT EXISTS(SELECT 1 FROM research_authority.search_lineage WHERE search_id=NEW.source_search_id AND campaign_id=NEW.source_campaign_id) OR
       NOT EXISTS(SELECT 1 FROM research_authority.authority_audit WHERE campaign_id=NEW.source_campaign_id
           AND xmin::text::bigint=txid_current()%4294967296
           AND event_type=CASE WHEN NEW.state='consumed' THEN 'holdout_escape' ELSE 'holdout_attempt' END
           AND normalized_payload::jsonb->'input'->>'search_id'=NEW.source_search_id
           AND normalized_payload::jsonb->'input'->>'holdout_id'=NEW.holdout_id) OR
       (NEW.state='consumed' AND NOT EXISTS(SELECT 1 FROM research_authority.contamination_edge WHERE source_search_id=NEW.source_search_id AND holdout_id=NEW.holdout_id AND contamination_domain_id=NEW.contamination_domain_id)) THEN
        RAISE EXCEPTION 'holdout transition lacks exact audit/ancestry';
    END IF;
    RETURN NULL;
END;
$$;
CREATE CONSTRAINT TRIGGER holdout_audit AFTER UPDATE ON research_authority.holdout_state
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.check_holdout_audit();

CREATE FUNCTION research_authority.check_scientific_audit() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE p research_authority.proposal_record; expected_event_type TEXT;
BEGIN
    IF TG_TABLE_NAME='proposal_record' THEN
        p := NEW;
        IF NOT EXISTS(SELECT 1 FROM research_authority.authority_audit a,
            jsonb_array_elements(a.normalized_payload::jsonb->'input'->'proposal_identities') identity
            WHERE a.campaign_id=p.campaign_id AND a.event_type='proposal_wave'
              AND a.xmin::text::bigint=txid_current()%4294967296
              AND identity->>'proposal_id'=p.proposal_id AND identity->>'params_fingerprint'=p.parameters_fingerprint
              AND identity->>'scientific_trial_id' IS NOT DISTINCT FROM p.scientific_trial_id) THEN
            RAISE EXCEPTION 'proposal lacks exact Governor identity audit';
        END IF;
    ELSIF TG_TABLE_NAME='trial_attempt' THEN
        IF NOT EXISTS(SELECT 1 FROM research_authority.authority_audit WHERE event_type='trial_attempt'
            AND xmin::text::bigint=txid_current()%4294967296
            AND normalized_payload::jsonb->'input'->>'scientific_trial_id'=NEW.scientific_trial_id
            AND (normalized_payload::jsonb->'input'->>'attempt_number')::integer=NEW.attempt_number) THEN
            RAISE EXCEPTION 'software attempt lacks exact audit';
        END IF;
    ELSIF TG_TABLE_NAME='search_lineage' THEN
        expected_event_type := CASE WHEN NEW.state='open' THEN 'open_search' ELSE 'finalize_search' END;
        IF NOT EXISTS(SELECT 1 FROM research_authority.authority_audit WHERE campaign_id=NEW.campaign_id AND authority_audit.event_type=expected_event_type
            AND xmin::text::bigint=txid_current()%4294967296
            AND coalesce(normalized_payload::jsonb->'input'->>'search_id',normalized_payload::jsonb->'input'->'request'->>'search_id')=NEW.search_id) THEN
            RAISE EXCEPTION 'search transition lacks matching audit';
        END IF;
    END IF;
    RETURN NULL;
END;
$$;
CREATE CONSTRAINT TRIGGER proposal_audit AFTER INSERT ON research_authority.proposal_record
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.check_scientific_audit();
CREATE CONSTRAINT TRIGGER attempt_audit AFTER INSERT ON research_authority.trial_attempt
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.check_scientific_audit();
CREATE CONSTRAINT TRIGGER search_audit AFTER INSERT OR UPDATE ON research_authority.search_lineage
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.check_scientific_audit();
