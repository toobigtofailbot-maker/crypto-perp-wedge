DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cpw_research_authority_writer') THEN
        CREATE ROLE cpw_research_authority_writer NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
    END IF;
END $$;
ALTER ROLE cpw_research_authority_writer NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
REVOKE ALL ON SCHEMA research_authority FROM PUBLIC;
GRANT USAGE ON SCHEMA research_authority TO cpw_research_authority_writer;
REVOKE ALL ON ALL TABLES IN SCHEMA research_authority FROM cpw_research_authority_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA research_authority TO cpw_research_authority_writer;
GRANT INSERT ON research_authority.envelope_registry, research_authority.envelope_control_state,
    research_authority.campaign_state, research_authority.search_lineage,
    research_authority.search_budget_reservation, research_authority.proposal_record,
    research_authority.scientific_trial, research_authority.trial_attempt,
    research_authority.holdout_state, research_authority.contamination_edge,
    research_authority.evidence_reference, research_authority.authority_audit
    TO cpw_research_authority_writer;
GRANT UPDATE ON research_authority.envelope_control_state, research_authority.campaign_state,
    research_authority.search_lineage, research_authority.search_budget_reservation,
    research_authority.holdout_state TO cpw_research_authority_writer;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA research_authority FROM PUBLIC;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA research_authority TO cpw_research_authority_writer;
