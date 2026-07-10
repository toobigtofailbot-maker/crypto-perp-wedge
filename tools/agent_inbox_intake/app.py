"""FastAPI app for the isolated Agent Inbox scratch-write intake service."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException

from tools.agent_inbox_intake.models import (
    DraftHistoryError,
    DraftIdError,
    DraftNotFoundError,
    DraftReviewError,
    DraftReviewEventRequest,
    DraftReviewStorageError,
    IntakeDraftError,
    IntakeDraftRequest,
)
from tools.agent_inbox_intake.service import (
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_REVIEW_ROOT,
    append_draft_review_event,
    create_intake_draft,
    get_intake_draft,
    list_intake_drafts,
    list_draft_review_events,
)
from tools.lab_state.resolver import REPO_ROOT


def create_app(
    *, repo_root: Path = REPO_ROOT, output_root: Path = DEFAULT_OUTPUT_ROOT,
    review_root: Path = DEFAULT_REVIEW_ROOT,
) -> FastAPI:
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
            return create_intake_draft(
                request, repo_root=repo_root, output_root=output_root
            )
        except IntakeDraftError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @api.get("/api/agent/drafts")
    def agent_drafts() -> dict:
        try:
            return list_intake_drafts(repo_root=repo_root, output_root=output_root)
        except DraftHistoryError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @api.get("/api/agent/drafts/{draft_id}")
    def agent_draft(draft_id: str) -> dict:
        try:
            return get_intake_draft(
                draft_id, repo_root=repo_root, output_root=output_root
            )
        except DraftNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except DraftIdError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except DraftHistoryError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @api.get("/api/agent/drafts/{draft_id}/review-events")
    def agent_draft_review_events(draft_id: str) -> dict:
        try:
            return list_draft_review_events(
                draft_id, repo_root=repo_root, output_root=output_root,
                review_root=review_root,
            )
        except DraftNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except DraftIdError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (DraftHistoryError, DraftReviewStorageError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @api.post("/api/agent/drafts/{draft_id}/review-events")
    def agent_append_draft_review_event(
        draft_id: str, request: DraftReviewEventRequest
    ) -> dict:
        try:
            return append_draft_review_event(
                draft_id, request, repo_root=repo_root, output_root=output_root,
                review_root=review_root,
            )
        except DraftNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except DraftReviewStorageError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except (DraftIdError, DraftReviewError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except DraftHistoryError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    return api


app = create_app()
