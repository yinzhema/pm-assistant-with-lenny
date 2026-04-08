"""
Feedback submission endpoint.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from storage.conversation_store import submit_feedback

router = APIRouter()


class FeedbackRequest(BaseModel):
    comment: str


@router.post("/feedback")
async def feedback(body: FeedbackRequest):
    """Save a feedback comment. Session ID defaults to 'anonymous'."""
    submit_feedback(username="anonymous", comment=body.comment)
    return {"ok": True}
