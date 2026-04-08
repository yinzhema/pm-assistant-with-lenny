"""
FastAPI dependency functions that pull singletons from request.app.state.
"""
from fastapi import Request

from services.pm_assistant import PMAssistant
from services.document_agent import DocumentAgent


def get_pm_assistant(request: Request) -> PMAssistant:
    """Return the PMAssistant singleton stored in app.state."""
    return request.app.state.pm_assistant


def get_doc_agent(request: Request) -> DocumentAgent:
    """Return the DocumentAgent singleton stored in app.state."""
    return request.app.state.doc_agent
