-- BROKER-3 dry-run dispatch: extend durable state and audit with an inert
-- dispatch lifecycle. This migration only extends the existing hermes_broker
-- schema created by 0001_broker_authority; it creates no new table and does not
-- alter nonce or idempotency uniqueness.

ALTER TABLE hermes_broker.broker_action_state
    ADD COLUMN dispatch_id TEXT;

ALTER TABLE hermes_broker.broker_authority_audit
    ADD COLUMN dispatch_id TEXT;

-- Replace the closed action-state vocabulary check with the final eight states.
DO $$
DECLARE
    constraint_name TEXT;
BEGIN
    SELECT conname INTO constraint_name
    FROM pg_constraint
    WHERE conrelid = 'hermes_broker.broker_action_state'::regclass
      AND contype = 'c'
      AND pg_get_constraintdef(oid) ILIKE '%state%submitted%verified%reserved%rejected%';
    IF constraint_name IS NOT NULL THEN
        EXECUTE format(
            'ALTER TABLE hermes_broker.broker_action_state DROP CONSTRAINT %I',
            constraint_name
        );
    END IF;
END $$;

ALTER TABLE hermes_broker.broker_action_state
    ADD CONSTRAINT broker_action_state_state_check
    CHECK (state IN (
        'submitted', 'verified', 'reserved', 'rejected',
        'dispatched', 'completed', 'failed', 'reconcile_required'
    ));

-- Replace the closed audit-event vocabulary and reason/binding checks.
DO $$
DECLARE
    constraint_name TEXT;
BEGIN
    FOR constraint_name IN
        SELECT conname
        FROM pg_constraint
        WHERE conrelid = 'hermes_broker.broker_authority_audit'::regclass
          AND contype = 'c'
          AND (
              pg_get_constraintdef(oid) ILIKE '%event_type%claim_submitted%'
              OR pg_get_constraintdef(oid) ILIKE '%claim_rejected%reason_code%'
              OR pg_get_constraintdef(oid) ILIKE '%reason_code%claim_rejected%'
              OR pg_get_constraintdef(oid) ILIKE '%nonce_reserved%reservation_id%'
          )
    LOOP
        EXECUTE format(
            'ALTER TABLE hermes_broker.broker_authority_audit DROP CONSTRAINT %I',
            constraint_name
        );
    END LOOP;
END $$;

ALTER TABLE hermes_broker.broker_authority_audit
    ADD CONSTRAINT broker_authority_audit_event_type_check
    CHECK (event_type IN (
        'claim_submitted', 'claim_verified', 'claim_rejected', 'nonce_reserved',
        'dispatch_requested', 'dispatch_completed', 'dispatch_failed', 'reconcile_required'
    ));

ALTER TABLE hermes_broker.broker_authority_audit
    ADD CONSTRAINT broker_authority_audit_reason_check
    CHECK (
        (event_type IN ('claim_rejected', 'dispatch_failed', 'reconcile_required')
            AND NULLIF(BTRIM(reason_code), '') IS NOT NULL)
        OR (event_type IN (
                'claim_submitted', 'claim_verified', 'nonce_reserved',
                'dispatch_requested', 'dispatch_completed'
            )
            AND reason_code IS NULL)
    );

ALTER TABLE hermes_broker.broker_authority_audit
    ADD CONSTRAINT broker_authority_audit_dispatch_binding_check
    CHECK (
        (event_type IN (
                'dispatch_requested', 'dispatch_completed', 'dispatch_failed', 'reconcile_required'
            )
            AND dispatch_id IS NOT NULL AND reservation_id IS NOT NULL)
        OR (event_type IN ('claim_submitted', 'claim_verified', 'claim_rejected', 'nonce_reserved')
            AND dispatch_id IS NULL)
    );

ALTER TABLE hermes_broker.broker_authority_audit
    ADD CONSTRAINT broker_authority_audit_nonce_reserved_check
    CHECK (event_type <> 'nonce_reserved' OR reservation_id IS NOT NULL);

-- Replace the action-state transition guard so only the final closed set of
-- transitions is legal and dispatch_id binds from `dispatched` onward.
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
           OR NEW.dispatch_id IS NOT NULL
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
    IF OLD.reservation_id IS NOT NULL
       AND NEW.reservation_id IS DISTINCT FROM OLD.reservation_id THEN
        RAISE EXCEPTION 'broker_action_state reservation_id is immutable once set'
            USING ERRCODE = '55000';
    END IF;
    IF OLD.dispatch_id IS NOT NULL
       AND NEW.dispatch_id IS DISTINCT FROM OLD.dispatch_id THEN
        RAISE EXCEPTION 'broker_action_state dispatch_id is immutable once set'
            USING ERRCODE = '55000';
    END IF;
    IF NOT (
        (OLD.state = 'submitted' AND NEW.state IN ('verified', 'rejected'))
        OR (OLD.state = 'verified' AND NEW.state IN ('reserved', 'rejected'))
        OR (OLD.state = 'reserved' AND NEW.state = 'dispatched')
        OR (OLD.state = 'dispatched'
            AND NEW.state IN ('completed', 'failed', 'reconcile_required'))
    ) THEN
        RAISE EXCEPTION 'illegal broker_action_state transition: % -> %', OLD.state, NEW.state
            USING ERRCODE = '23514';
    END IF;
    IF NEW.state = 'reserved'
       AND (NEW.reservation_id IS NULL
            OR NEW.dispatch_id IS NOT NULL
            OR NEW.last_reason_code IS NOT NULL) THEN
        RAISE EXCEPTION 'reserved state requires reservation_id and no dispatch or reason'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.state = 'dispatched'
       AND (NEW.reservation_id IS NULL
            OR NEW.dispatch_id IS NULL
            OR NEW.last_reason_code IS NOT NULL) THEN
        RAISE EXCEPTION 'dispatched state requires reservation_id, dispatch_id, and no reason'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.state = 'completed'
       AND (NEW.reservation_id IS NULL
            OR NEW.dispatch_id IS NULL
            OR NEW.last_reason_code IS NOT NULL) THEN
        RAISE EXCEPTION 'completed state requires reservation_id, dispatch_id, and no reason'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.state IN ('failed', 'reconcile_required')
       AND (NEW.reservation_id IS NULL
            OR NEW.dispatch_id IS NULL
            OR NULLIF(BTRIM(NEW.last_reason_code), '') IS NULL) THEN
        RAISE EXCEPTION 'failed/reconcile state requires reservation_id, dispatch_id, and a reason'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.state = 'rejected'
       AND (NEW.reservation_id IS NOT NULL
            OR NEW.dispatch_id IS NOT NULL
            OR NULLIF(BTRIM(NEW.last_reason_code), '') IS NULL) THEN
        RAISE EXCEPTION 'rejected state requires a reason and no reservation_id or dispatch_id'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.state IN ('submitted', 'verified')
       AND (NEW.reservation_id IS NOT NULL OR NEW.dispatch_id IS NOT NULL) THEN
        RAISE EXCEPTION 'pre-reservation state cannot link a reservation or dispatch'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
