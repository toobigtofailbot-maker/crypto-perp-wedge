-- Run as the Research Memory database owner. Set authentication separately.
-- The MCP also rejects this role at connection time if any listed table has
-- INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, or TRIGGER privilege.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'hermes_research_memory_reader') THEN
        CREATE ROLE hermes_research_memory_reader LOGIN NOINHERIT;
    END IF;
END
$$;

ALTER ROLE hermes_research_memory_reader
    LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
ALTER ROLE hermes_research_memory_reader SET default_transaction_read_only = on;
REVOKE CREATE ON SCHEMA research_memory FROM hermes_research_memory_reader;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA research_memory
    FROM hermes_research_memory_reader;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA research_memory
    FROM hermes_research_memory_reader;
GRANT USAGE ON SCHEMA research_memory TO hermes_research_memory_reader;
GRANT SELECT ON TABLE
    research_memory.hypothesis_items,
    research_memory.memory_records,
    research_memory.memory_aliases,
    research_memory.evidence_references
TO hermes_research_memory_reader;
