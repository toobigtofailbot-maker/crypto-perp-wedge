-- Owner-controlled metadata in the existing authority store; no trust is seeded.
ALTER TABLE research_authority.authority_audit DROP CONSTRAINT authority_audit_event_type_check;
ALTER TABLE research_authority.authority_audit ADD CONSTRAINT authority_audit_event_type_check
 CHECK(event_type IN ('register_envelope','control_envelope','open_campaign','open_search',
 'proposal_wave','trial_attempt','trial_result','finalize_search','holdout_attempt','holdout_escape',
 'evidence_reference','nonholdout_control','nonholdout_read'));

CREATE TABLE research_authority.nonholdout_control (
 record_id TEXT PRIMARY KEY,
 kind TEXT NOT NULL CHECK(kind IN ('custodian','designation','revocation')),
 semantic_payload TEXT NOT NULL,
 content_sha256 TEXT NOT NULL CHECK(content_sha256 ~ '^sha256:[0-9a-f]{64}$'),
 event_id TEXT NOT NULL UNIQUE REFERENCES research_authority.authority_audit(event_id)
);
CREATE TRIGGER immutable_rows BEFORE UPDATE OR DELETE ON research_authority.nonholdout_control
 FOR EACH ROW EXECUTE FUNCTION research_authority.deny_mutation();
CREATE TRIGGER immutable_truncate BEFORE TRUNCATE ON research_authority.nonholdout_control
 FOR EACH STATEMENT EXECUTE FUNCTION research_authority.deny_mutation();

CREATE FUNCTION research_authority.check_nonholdout_control() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE event research_authority.authority_audit; payload JSONB;
BEGIN
 -- Also serialize a direct privileged insert with every existing kernel writer.
 PERFORM pg_advisory_xact_lock(721026002);
 SELECT * INTO event FROM research_authority.authority_audit WHERE event_id=NEW.event_id;
 payload := event.normalized_payload::jsonb->'input';
 IF event.event_type IS DISTINCT FROM 'nonholdout_control' OR
    payload->>'record_id' IS DISTINCT FROM NEW.record_id OR
    payload->>'kind' IS DISTINCT FROM NEW.kind OR
    payload->>'content_sha256' IS DISTINCT FROM NEW.content_sha256 OR
    payload->'record' IS DISTINCT FROM NEW.semantic_payload::jsonb THEN
   RAISE EXCEPTION 'nonholdout control audit mismatch';
 END IF;
 RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER control_audit AFTER INSERT ON research_authority.nonholdout_control
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION research_authority.check_nonholdout_control();
