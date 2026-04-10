"""
Document management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from dependencies import get_doc_agent
from models.documents import (
    CritiqueRequest,
    ExportRequest,
    GenerateRequest,
    ImproveRequest,
    RestoreVersionRequest,
    SaveDocumentRequest,
    UpdateDocumentRequest,
)
from services.document_agent import DocumentAgent
from services.export_service import export_to_docx, export_to_excel, export_to_markdown
from storage import document_store

router = APIRouter()


# ── Document generation ──────────────────────────────────────────────────────

@router.post("/documents/generate")
async def generate_document(
    req: GenerateRequest,
    doc_agent: DocumentAgent = Depends(get_doc_agent),
):
    """Generate a PM artifact from a template."""
    history = [{"role": m.role, "content": m.content} for m in req.history]
    html = doc_agent.generate_from_template(
        template_id=req.template_id,
        user_context=req.user_context,
        conversation_history=history or None,
    )
    return {"html": html}


# ── CRUD ─────────────────────────────────────────────────────────────────────

@router.post("/documents")
async def create_document(req: SaveDocumentRequest):
    """Save a new document. Returns the new document UUID."""
    doc_id = document_store.save_document(
        session_id=req.session_id,
        title=req.title,
        template_id=req.template_id,
        content_html=req.content_html,
    )
    if not doc_id:
        raise HTTPException(status_code=500, detail="Failed to save document")
    return {"id": doc_id}


@router.patch("/documents/{document_id}")
async def update_document(document_id: str, req: UpdateDocumentRequest):
    """Update an existing document's title and/or content. Saves a version snapshot."""
    existing = document_store.load_document(document_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")

    title = req.title if req.title is not None else existing["title"]
    content_html = req.content_html if req.content_html is not None else existing["content_html"]

    doc_id = document_store.save_document(
        session_id=existing["session_id"],
        title=title,
        template_id=existing["template_id"],
        content_html=content_html,
        document_id=document_id,
    )
    if not doc_id:
        raise HTTPException(status_code=500, detail="Failed to update document")

    updated = document_store.load_document(document_id)
    updated_at = updated.get("updated_at", "") if updated else ""
    return {"id": doc_id, "updated_at": updated_at}


@router.get("/documents")
async def list_documents(session_id: str):
    """List all documents for a session, newest first."""
    docs = document_store.list_documents(session_id)
    return {"documents": docs}


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Load a single document by ID."""
    doc = document_store.load_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/documents/{document_id}/versions")
async def get_document_versions(document_id: str):
    """Return the last 3 versions for a document."""
    versions = document_store.get_versions(document_id)
    return {"versions": versions}


@router.post("/documents/{document_id}/restore")
async def restore_document_version(document_id: str, req: RestoreVersionRequest):
    """Restore a previous version as the current document content."""
    restored_html = document_store.restore_version(document_id, req.version_id)
    if restored_html is None:
        raise HTTPException(status_code=404, detail="Version not found or restore failed")
    return {"html": restored_html}


# ── AI co-editing ─────────────────────────────────────────────────────────────

@router.post("/documents/improve")
async def improve_document_direct(
    req: ImproveRequest,
    doc_agent: DocumentAgent = Depends(get_doc_agent),
):
    """Rewrite a selected passage without requiring a saved document ID."""
    html = doc_agent.improve_selection(
        selected_text=req.selected_text,
        full_document=req.full_html,
        instruction=req.action,
    )
    return {"html": html}


@router.post("/documents/critique")
async def critique_document_direct(
    req: CritiqueRequest,
    doc_agent: DocumentAgent = Depends(get_doc_agent),
):
    """Critique a document without requiring a saved document ID."""
    html = doc_agent.critique_document(
        document_html=req.document_html,
        template_id=req.template_id,
    )
    return {"html": html}


@router.post("/documents/{document_id}/improve")
async def improve_document_selection(
    document_id: str,
    req: ImproveRequest,
    doc_agent: DocumentAgent = Depends(get_doc_agent),
):
    """Rewrite a selected passage in the document."""
    html = doc_agent.improve_selection(
        selected_text=req.selected_text,
        full_document=req.full_html,
        instruction=req.action,
    )
    return {"html": html}


@router.post("/documents/{document_id}/critique")
async def critique_document(
    document_id: str,
    req: CritiqueRequest,
    doc_agent: DocumentAgent = Depends(get_doc_agent),
):
    """Provide a structured critique of the document."""
    html = doc_agent.critique_document(
        document_html=req.document_html,
        template_id=req.template_id,
    )
    return {"html": html}


# ── Export ───────────────────────────────────────────────────────────────────

@router.post("/export/markdown")
async def export_markdown(req: ExportRequest):
    """Export document HTML as Markdown. Returns plain text response."""
    md = export_to_markdown(req.document_html, title=req.title)
    return Response(
        content=md,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{req.title or "document"}.md"'},
    )


@router.post("/export/excel")
async def export_excel(req: ExportRequest):
    """Export document tables as an Excel workbook."""
    xlsx_bytes = export_to_excel(req.document_html, title=req.title)
    filename = (req.title or "document").replace(" ", "_") + ".xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export/docx")
async def export_docx(req: ExportRequest):
    """Export document as a Word (.docx) file."""
    docx_bytes = export_to_docx(req.document_html, title=req.title)
    filename = (req.title or "document").replace(" ", "_") + ".docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
