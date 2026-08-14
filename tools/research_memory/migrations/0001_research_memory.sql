CREATE TABLE research_memory.hypothesis_items (
    memory_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fingerprint_version TEXT NOT NULL,
    fingerprint_sha256 CHAR(64) NOT NULL UNIQUE,
    strategy_family TEXT NOT NULL,
    mechanism TEXT NOT NULL,
    primary_timeframe TEXT,
    instrument_scope TEXT NOT NULL,
    required_data_features TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    free_parameter_count INTEGER CHECK (free_parameter_count IS NULL OR free_parameter_count >= 0),
    canonical_definition JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (fingerprint_sha256 ~ '^[0-9a-f]{64}$')
);

CREATE TABLE research_memory.memory_records (
    memory_record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    memory_item_id BIGINT NOT NULL
        REFERENCES research_memory.hypothesis_items(memory_item_id) ON DELETE CASCADE,
    authority_state TEXT NOT NULL
        CHECK (authority_state IN ('REPO_INDEX', 'NON_AUTHORITATIVE')),
    source_key TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN (
            'DRAFT', 'CONCLUDED', 'ARCHIVED', 'PROMOTED', 'BLOCKED', 'INVALID',
            'INCOMPLETE', 'SUPERSEDED', 'REJECTED'
        )
    ),
    classification TEXT NOT NULL CHECK (
        classification IN (
            'PENDING', 'NO-GO', 'PASS', 'CONDITIONAL', 'BLOCKED', 'INVALID',
            'INCOMPLETE', 'SUPERSEDED', 'REJECTED'
        )
    ),
    negative_reason TEXT,
    source_created_at TEXT,
    source_updated_at TEXT,
    source_metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (authority_state, source_key),
    CHECK (
        classification NOT IN ('NO-GO', 'BLOCKED', 'INVALID', 'INCOMPLETE', 'SUPERSEDED', 'REJECTED')
        OR negative_reason IS NOT NULL
    )
);

CREATE TABLE research_memory.memory_aliases (
    memory_alias_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    memory_item_id BIGINT NOT NULL
        REFERENCES research_memory.hypothesis_items(memory_item_id) ON DELETE CASCADE,
    authority_state TEXT NOT NULL
        CHECK (authority_state IN ('REPO_INDEX', 'NON_AUTHORITATIVE')),
    source_key TEXT NOT NULL,
    alias_kind TEXT NOT NULL,
    alias_key TEXT NOT NULL,
    UNIQUE (authority_state, source_key, alias_kind, alias_key)
);

CREATE TABLE research_memory.evidence_references (
    evidence_reference_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    memory_record_id BIGINT NOT NULL
        REFERENCES research_memory.memory_records(memory_record_id) ON DELETE CASCADE,
    artifact_path TEXT NOT NULL,
    artifact_id TEXT,
    evidence_role TEXT NOT NULL,
    artifact_content_sha256 CHAR(64) NOT NULL,
    source_record_sha256 CHAR(64),
    supports_conclusion BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (memory_record_id, artifact_path, evidence_role),
    CHECK (artifact_content_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (source_record_sha256 IS NULL OR source_record_sha256 ~ '^[0-9a-f]{64}$'),
    CHECK (artifact_path !~ '(^|/)\.\.(/|$)')
);

CREATE INDEX hypothesis_items_family_timeframe_idx
    ON research_memory.hypothesis_items(strategy_family, primary_timeframe);
CREATE INDEX hypothesis_items_features_gin_idx
    ON research_memory.hypothesis_items USING GIN(required_data_features);
CREATE INDEX memory_records_classification_idx
    ON research_memory.memory_records(classification, status);
CREATE INDEX memory_records_negative_idx
    ON research_memory.memory_records(classification, memory_item_id)
    WHERE classification IN ('NO-GO', 'BLOCKED', 'INVALID', 'INCOMPLETE', 'SUPERSEDED', 'REJECTED');
CREATE INDEX memory_aliases_lookup_idx
    ON research_memory.memory_aliases(alias_kind, alias_key);
CREATE INDEX evidence_references_artifact_idx
    ON research_memory.evidence_references(artifact_id, artifact_path);
