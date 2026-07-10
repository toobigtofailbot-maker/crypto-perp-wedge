"""FastAPI app for the isolated Agent Inbox scratch-write intake service."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from tools.agent_inbox_intake.models import IntakeDraftError, IntakeDraftRequest
from tools.agent_inbox_intake.service import create_intake_draft


def create_app() -> FastAPI:
    """Create the isolated write service app without touching dashboard API routes."""

    api = FastAPI(
        title="Agent Inbox Scratch Intake Draft Service",
        version="0.1.0",
        description=(
            "Isolated scratch-only Agent Inbox service. It produces noncanonical "
            "draft packets and exposes no execution, approval, promotion, runner, "
            "pipeline, scheduler, notification, paper/live, or runtime controls."
        ),
    )

    @api.post("/api/agent/intake-draft")
    def agent_intake_draft(request: IntakeDraftRequest) -> dict:
        try:
            return create_intake_draft(request)
        except IntakeDraftError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return api


app = create_app()
