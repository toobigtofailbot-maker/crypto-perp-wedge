CREATE OR REPLACE FUNCTION hermes_broker.reject_immutable_change()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION '% is immutable', TG_TABLE_NAME
        USING ERRCODE = '55000';
END;
$$;

CREATE OR REPLACE FUNCTION hermes_broker.guard_action_state_transition()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'broker_action_state rows cannot be deleted'
            USING ERRCODE = '55000';
    END IF;

    IF TG_OP = 'INSERT' THEN
        IF NEW.state <> 'submitted'
           OR NEW.state_version <> 1
           OR NEW.reservation_id IS NOT NULL
           OR NEW.last_reason_code IS NOT NULL THEN
            RAISE EXCEPTION 'broker_action_state must begin as submitted version 1'
                USING ERRCODE = '23514';
        END IF;
        RETURN NEW;
    END IF;

    IF NEW.executable_action_id <> OLD.executable_action_id
       OR NEW.executable_action_sha256 <> OLD.executable_action_sha256
       OR NEW.approval_id <> OLD.approval_id THEN
        RAISE EXCEPTION 'broker_action_state identity is immutable'
            USING ERRCODE = '55000';
    END IF;
    IF NEW.state_version <> OLD.state_version + 1 THEN
        RAISE EXCEPTION 'broker_action_state version must increment by one'
            USING ERRCODE = '23514';
    END IF;
    IF NOT (
        (OLD.state = 'submitted' AND NEW.state IN ('verified', 'rejected'))
        OR (OLD.state = 'verified' AND NEW.state IN ('reserved', 'rejected'))
    ) THEN
        RAISE EXCEPTION 'illegal broker_action_state transition: % -> %', OLD.state, NEW.state
            USING ERRCODE = '23514';
    END IF;
    IF NEW.state = 'reserved'
       AND (NEW.reservation_id IS NULL OR NEW.last_reason_code IS NOT NULL) THEN
        RAISE EXCEPTION 'reserved state requires reservation_id and no reason'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.state = 'rejected'
       AND (NEW.reservation_id IS NOT NULL
            OR NULLIF(BTRIM(NEW.last_reason_code), '') IS NULL) THEN
        RAISE EXCEPTION 'rejected state requires a reason and no reservation_id'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.state IN ('submitted', 'verified') AND NEW.reservation_id IS NOT NULL THEN
        RAISE EXCEPTION 'pre-reservation state cannot link a reservation'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TABLE hermes_broker.broker_approval (
    approval_id TEXT PRIMARY KEY,
    executable_action_id TEXT NOT NULL,
    executable_action_sha256 CHAR(64) NOT NULL,
    executable_action_canonical BYTEA NOT NULL,
    signed_claim_sha256 CHAR(64) NOT NULL UNIQUE,
    signed_claim_canonical BYTEA NOT NULL,
    prepared_record_id TEXT NOT NULL,
    prepared_payload_sha256 CHAR(64) NOT NULL,
    source_proposal_id TEXT NOT NULL,
    source_proposal_content_sha256 CHAR(64) NOT NULL,
    repo_sha CHAR(40) NOT NULL,
    authority_class TEXT NOT NULL,
    action_type TEXT NOT NULL,
    action_registry_version TEXT NOT NULL,
    adapter_id TEXT NOT NULL,
    adapter_version TEXT NOT NULL,
    key_registry_version TEXT NOT NULL,
    scope_digest CHAR(64) NOT NULL,
    budget_bound JSONB NOT NULL,
    count_or_quantity_bound JSONB,
    timeout_bound JSONB NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL,
    not_before TIMESTAMPTZ NOT NULL,
    expiry TIMESTAMPTZ NOT NULL,
    single_use_nonce TEXT NOT NULL,
    signer_key_id TEXT NOT NULL,
    signature_algorithm TEXT NOT NULL,
    signature_encoding TEXT NOT NULL,
    retention_root_ref TEXT NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL,
    CHECK (executable_action_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (signed_claim_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (prepared_payload_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (source_proposal_content_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (scope_digest ~ '^[0-9a-f]{64}$'),
    CHECK (repo_sha ~ '^[0-9a-f]{40}$'),
    CHECK (authority_class = 'A1'),
    CHECK (signature_algorithm = 'ed25519'),
    CHECK (signature_encoding = 'lowercase_hex'),
    CHECK (issued_at <= not_before),
    CHECK (not_before <= expiry),
    CHECK (expiry > issued_at)
);

CREATE TABLE hermes_broker.broker_reservation (
    reservation_id TEXT PRIMARY KEY,
    approval_id TEXT NOT NULL REFERENCES hermes_broker.broker_approval(approval_id),
    executable_action_id TEXT NOT NULL,
    executable_action_sha256 CHAR(64) NOT NULL,
    prepared_record_id TEXT NOT NULL,
    prepared_payload_sha256 CHAR(64) NOT NULL,
    single_use_nonce TEXT NOT NULL,
    idempotency_key CHAR(64) NOT NULL,
    reserved_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_broker_reservation_single_use_nonce UNIQUE (single_use_nonce),
    CONSTRAINT uq_broker_reservation_idempotency_key UNIQUE (idempotency_key),
    CONSTRAINT uq_broker_reservation_approval_id UNIQUE (approval_id),
    CHECK (executable_action_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (prepared_payload_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (idempotency_key ~ '^[0-9a-f]{64}$')
);

CREATE TABLE hermes_broker.broker_authority_audit (
    audit_sequence BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    approval_id TEXT,
    executable_action_id TEXT,
    executable_action_sha256 CHAR(64),
    prepared_record_id TEXT,
    prepared_payload_sha256 CHAR(64),
    source_proposal_id TEXT,
    source_proposal_content_sha256 CHAR(64),
    repo_sha CHAR(40),
    action_registry_version TEXT,
    adapter_id TEXT,
    adapter_version TEXT,
    key_registry_version TEXT,
    single_use_nonce TEXT,
    reservation_id TEXT,
    occurred_at TIMESTAMPTZ NOT NULL,
    actor TEXT NOT NULL,
    reason_code TEXT,
    event_payload_canonical BYTEA NOT NULL,
    event_payload_sha256 CHAR(64) NOT NULL UNIQUE,
    CHECK (event_type IN (
        'claim_submitted', 'claim_verified', 'claim_rejected', 'nonce_reserved'
    )),
    CHECK (actor = 'broker'),
    CHECK (executable_action_sha256 IS NULL
           OR executable_action_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (prepared_payload_sha256 IS NULL
           OR prepared_payload_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (source_proposal_content_sha256 IS NULL
           OR source_proposal_content_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (repo_sha IS NULL OR repo_sha ~ '^[0-9a-f]{40}$'),
    CHECK (event_payload_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (
        (event_type = 'claim_rejected' AND NULLIF(BTRIM(reason_code), '') IS NOT NULL)
        OR (event_type <> 'claim_rejected' AND reason_code IS NULL)
    ),
    CHECK (event_type <> 'nonce_reserved' OR reservation_id IS NOT NULL)
);

CREATE TABLE hermes_broker.broker_trusted_key (
    registry_epoch BIGINT NOT NULL CHECK (registry_epoch > 0),
    key_registry_version TEXT NOT NULL,
    key_id TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    public_key_encoding TEXT NOT NULL,
    public_key CHAR(64) NOT NULL,
    state TEXT NOT NULL,
    added_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    revocation_reason TEXT,
    fixture_only BOOLEAN NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (registry_epoch, key_id),
    UNIQUE (key_registry_version, key_id),
    CHECK (algorithm = 'ed25519'),
    CHECK (public_key_encoding = 'lowercase_hex'),
    CHECK (public_key ~ '^[0-9a-f]{64}$'),
    CHECK (state IN ('active', 'revoked')),
    CHECK (
        (state = 'active' AND revoked_at IS NULL AND revocation_reason IS NULL)
        OR (state = 'revoked' AND revoked_at IS NOT NULL
            AND NULLIF(BTRIM(revocation_reason), '') IS NOT NULL)
    ),
    CHECK (revoked_at IS NULL OR revoked_at >= added_at)
);

CREATE TABLE hermes_broker.broker_action_state (
    executable_action_id TEXT PRIMARY KEY,
    executable_action_sha256 CHAR(64) NOT NULL,
    approval_id TEXT NOT NULL REFERENCES hermes_broker.broker_approval(approval_id),
    state TEXT NOT NULL,
    state_version INTEGER NOT NULL CHECK (state_version > 0),
    reservation_id TEXT,
    last_reason_code TEXT,
    updated_at TIMESTAMPTZ NOT NULL,
    CHECK (executable_action_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (state IN ('submitted', 'verified', 'reserved', 'rejected'))
);

CREATE TRIGGER broker_approval_immutable
BEFORE UPDATE OR DELETE ON hermes_broker.broker_approval
FOR EACH ROW EXECUTE FUNCTION hermes_broker.reject_immutable_change();

CREATE TRIGGER broker_reservation_immutable
BEFORE UPDATE OR DELETE ON hermes_broker.broker_reservation
FOR EACH ROW EXECUTE FUNCTION hermes_broker.reject_immutable_change();

CREATE TRIGGER broker_authority_audit_immutable
BEFORE UPDATE OR DELETE ON hermes_broker.broker_authority_audit
FOR EACH ROW EXECUTE FUNCTION hermes_broker.reject_immutable_change();

CREATE TRIGGER broker_trusted_key_immutable
BEFORE UPDATE OR DELETE ON hermes_broker.broker_trusted_key
FOR EACH ROW EXECUTE FUNCTION hermes_broker.reject_immutable_change();

CREATE TRIGGER broker_action_state_guard
BEFORE INSERT OR UPDATE OR DELETE ON hermes_broker.broker_action_state
FOR EACH ROW EXECUTE FUNCTION hermes_broker.guard_action_state_transition();
