"""
Pydantic models for document endpoints.
"""
from typing import List, Optional

from pydantic import BaseModel

from models.chat import HistoryMessage


class GenerateRequest(BaseModel):
    template_id: str
    user_context: str = ""
    history: List[HistoryMessage] = []


class ImproveRequest(BaseModel):
    selected_text: str
    full_html: str
    action: str  # improve | expand | critique | simplify | rewrite


class CritiqueRequest(BaseModel):
    document_html: str
    template_id: str


class SaveDocumentRequest(BaseModel):
    session_id: str
    title: str
    template_id: str
    content_html: str


class UpdateDocumentRequest(BaseModel):
    title: Optional[str] = None
    content_html: Optional[str] = None


class RestoreVersionRequest(BaseModel):
    version_id: str


class ExportRequest(BaseModel):
    document_html: str
    title: str
