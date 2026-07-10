"""Local-first FastAPI app for read-only operator dashboard projections."""

from __future__ import annotations

from fastapi import FastAPI

from tools.operator_dashboard_api import readers
from tools.operator_dashboard_api.models import ApiEnvelope


def create_app() -> FastAPI:
    """Create the read-only dashboard API app without binding a server."""

    api = FastAPI(
        title="Local Operator Dashboard Read-Only API",
        version="0.1.0",
        description=(
            "Local-first read-only API over committed repo artifacts and existing "
            "static dashboard/cockpit readers. It exposes no mutation or control routes."
        ),
    )

    @api.get("/api/dashboard/summary", response_model=ApiEnvelope)
    def dashboard_summary() -> ApiEnvelope:
        return readers.read_dashboard_summary()

    @api.get("/api/research/jobs", response_model=ApiEnvelope)
    def research_jobs() -> ApiEnvelope:
        return readers.read_research_jobs()

    @api.get("/api/research/result-populations", response_model=ApiEnvelope)
    def result_populations() -> ApiEnvelope:
        return readers.read_result_populations()

    @api.get("/api/research/result-populations/{id}", response_model=ApiEnvelope)
    def result_population(id: str) -> ApiEnvelope:
        return readers.read_result_population(id)

    @api.get(
        "/api/research/result-populations/{id}/artifact-projections",
        response_model=ApiEnvelope,
    )
    def result_population_artifact_projections(id: str) -> ApiEnvelope:
        return readers.read_result_population_artifact_projections(id)

    @api.get("/api/strategies", response_model=ApiEnvelope)
    def strategies() -> ApiEnvelope:
        return readers.read_strategies()

    @api.get("/api/strategies/{id}", response_model=ApiEnvelope)
    def strategy(id: str) -> ApiEnvelope:
        return readers.read_strategy(id)

    @api.get("/api/candidates/funnel", response_model=ApiEnvelope)
    def candidates_funnel() -> ApiEnvelope:
        return readers.read_candidate_funnel()

    @api.get("/api/reports/daily", response_model=ApiEnvelope)
    def daily_report() -> ApiEnvelope:
        return readers.read_daily_report()

    @api.get("/api/reports/weekly", response_model=ApiEnvelope)
    def weekly_report() -> ApiEnvelope:
        return readers.read_weekly_report()

    @api.get("/api/system/data-health", response_model=ApiEnvelope)
    def system_data_health() -> ApiEnvelope:
        return readers.read_data_health()

    @api.get("/api/agent/intake-schema", response_model=ApiEnvelope)
    def agent_intake_schema() -> ApiEnvelope:
        return readers.read_agent_intake_schema()

    return api


app = create_app()
