"""
Translation endpoints — PRD → agent.md and Idea → agent.md.

SSE event types:
  token               {"type": "token", "content": "..."}
  extraction_done     {"type": "extraction_done", "extracted_sections": {...}}
  agent_section_done  {"type": "agent_section_done", "section_key": "...", "html": "...", "confidence": "green|yellow|red"}
  gap_analysis_done   {"type": "gap_analysis_done", "gaps": [...]}
  clarifying_questions {"type": "clarifying_questions", "questions": [...]}
  section_updated     {"type": "section_updated", "section_key": "...", "html": "...", "confidence": "green"}
  final_agent_html    {"type": "final_agent_html", "html": "..."}
  error               {"type": "error", "message": "..."}
  done                {"type": "done"}
"""
import json

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from data.question_trees import QUESTION_TREES
from models.artifacts import (
    StartTranslationRequest,
    ClarifyGapRequest,
    StartArtifactSessionRequest,
    StartArtifactSessionResponse,
    QuestionOut,
)
import storage.translation_session_store as store
import storage.artifact_session_store as artifact_store

router = APIRouter()


# ---------------------------------------------------------------------------
# Sub-Feature B: PRD → agent.md
# ---------------------------------------------------------------------------

@router.post("/translation/prd-to-agent")
async def start_prd_translation(req: StartTranslationRequest, request: Request):
    """
    Multi-phase SSE stream:
      Phase 1 — extraction (FRONTIER)
      Phase 2 — agent.md generation (FRONTIER)
      Phase 3 — gap analysis (FRONTIER)
      Phase 4 — emit clarifying questions
    """
    translation_agent = request.app.state.translation_agent

    translation_session_id = store.create_session(
        req.session_id, "prd-to-agent", req.prd_text
    )

    async def event_generator():
        # --- Phase 1: Extract PRD ---
        extracted_sections = {}
        try:
            async for event_type, payload in translation_agent.stream_extract_prd(req.prd_text):
                if event_type == "token":
                    yield {"data": json.dumps({"type": "token", "content": payload})}
                elif event_type == "done":
                    extracted_sections = payload
                    store.set_extracted_sections(translation_session_id, extracted_sections)
                    yield {
                        "data": json.dumps({
                            "type": "extraction_done",
                            "extracted_sections": extracted_sections,
                        })
                    }
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": f"Extraction failed: {e}"})}
            return

        # --- Phase 2: Generate agent.md sections ---
        agent_sections = []
        try:
            async for event_type, payload in translation_agent.stream_generate_agent_md(
                extracted_sections
            ):
                if event_type == "token":
                    yield {"data": json.dumps({"type": "token", "content": payload})}
                elif event_type == "section":
                    agent_sections.append(payload)
                    yield {
                        "data": json.dumps({
                            "type": "agent_section_done",
                            "section_key": payload.get("section_key"),
                            "html": payload.get("html"),
                            "confidence": payload.get("confidence"),
                        })
                    }
                elif event_type == "done":
                    agent_sections = payload
                    store.set_agent_sections(translation_session_id, agent_sections)
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": f"Generation failed: {e}"})}
            return

        # --- Phase 3: Gap analysis ---
        try:
            gaps = await translation_agent.analyze_gaps(req.prd_text, agent_sections)
            store.set_gaps(translation_session_id, gaps)
            yield {
                "data": json.dumps({
                    "type": "gap_analysis_done",
                    "gaps": gaps,
                    "translation_session_id": translation_session_id,
                })
            }
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": f"Gap analysis failed: {e}"})}
            return

        # --- Phase 4: Emit clarifying questions (high/medium severity gaps first) ---
        sorted_gaps = sorted(
            gaps,
            key=lambda g: {"high": 0, "medium": 1, "low": 2}.get(g.get("severity", "low"), 2),
        )
        clarifying_questions = [
            {
                "id": f"gap_{i}",
                "gap_category": g.get("category"),
                "section": g.get("section"),
                "question": g.get("suggested_question"),
                "severity": g.get("severity"),
                "description": g.get("description"),
            }
            for i, g in enumerate(sorted_gaps[:8])  # max 8 clarifying questions
        ]
        yield {
            "data": json.dumps({
                "type": "clarifying_questions",
                "questions": clarifying_questions,
                "translation_session_id": translation_session_id,
            })
        }
        yield {"data": json.dumps({"type": "done"})}

    return EventSourceResponse(
        event_generator(),
        headers={"X-Accel-Buffering": "no"},
    )


@router.post("/translation/prd-to-agent/{translation_session_id}/clarify")
async def clarify_gap(
    translation_session_id: str,
    req: ClarifyGapRequest,
    request: Request,
):
    """
    Resolve a single gap with the PM's answer.
    Uses EFFICIENT model — streams updated section HTML.
    """
    translation_agent = request.app.state.translation_agent

    session = store.get_session(translation_session_id)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Translation session not found")

    # Find the gap this question refers to
    gaps = session.get("gaps") or []
    gap_index = int(req.question_id.replace("gap_", "")) if req.question_id.startswith("gap_") else 0
    gap = gaps[gap_index] if gap_index < len(gaps) else {}

    section_key = gap.get("section", "")
    agent_sections = session.get("agent_sections") or []
    current_section = next(
        (s for s in agent_sections if s.get("section_key") == section_key),
        {"html": "", "confidence": "red"},
    )

    async def event_generator():
        store.add_clarification(translation_session_id, req.question_id, req.answer)

        updated_html = ""
        try:
            async for event_type, payload in translation_agent.stream_resolve_clarification(
                section_key=section_key,
                section_label=gap.get("section", section_key),
                gap_description=gap.get("description", ""),
                pm_answer=req.answer,
                current_html=current_section.get("html", ""),
            ):
                if event_type == "token":
                    yield {"data": json.dumps({"type": "token", "content": payload})}
                elif event_type == "done":
                    updated_html = payload
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}
            return

        # Persist updated section
        store.update_agent_section(translation_session_id, section_key, updated_html, "green")

        yield {
            "data": json.dumps({
                "type": "section_updated",
                "section_key": section_key,
                "html": updated_html,
                "confidence": "green",
            })
        }
        yield {"data": json.dumps({"type": "done"})}

    return EventSourceResponse(
        event_generator(),
        headers={"X-Accel-Buffering": "no"},
    )


@router.post("/translation/prd-to-agent/{translation_session_id}/finalize")
async def finalize_translation(translation_session_id: str, request: Request):
    """
    Final synthesis of the complete agent.md.
    Uses FRONTIER model.
    """
    translation_agent = request.app.state.translation_agent

    session = store.get_session(translation_session_id)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Translation session not found")

    async def event_generator():
        agent_sections = session.get("agent_sections") or []
        clarifications = session.get("clarifications") or {}
        extracted = session.get("extracted_sections") or {}
        agent_name = extracted.get("product_name", "Agent") or "Agent"

        final_html = ""
        try:
            async for event_type, payload in translation_agent.stream_finalize(
                agent_sections=agent_sections,
                clarifications=clarifications,
                agent_name=agent_name,
            ):
                if event_type == "token":
                    final_html += payload
                    yield {"data": json.dumps({"type": "token", "content": payload})}
                elif event_type == "done":
                    final_html = payload
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}
            return

        store.set_final_html(translation_session_id, final_html)
        yield {"data": json.dumps({"type": "final_agent_html", "html": final_html})}
        yield {"data": json.dumps({"type": "done"})}

    return EventSourceResponse(
        event_generator(),
        headers={"X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Sub-Feature A: Idea → agent.md (reuses artifact builder with idea-to-agent tree)
# ---------------------------------------------------------------------------

@router.post("/translation/idea-to-agent/sessions", response_model=StartArtifactSessionResponse)
async def start_idea_to_agent_session(req: StartArtifactSessionRequest):
    """Start an Idea → agent.md session using the artifact builder question tree."""
    tree = QUESTION_TREES.get("idea-to-agent")
    if not tree:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="idea-to-agent tree not found")

    artifact_session_id = artifact_store.create_session(req.session_id, "idea-to-agent")
    questions = [QuestionOut(**q) for q in tree.as_dict_list()]

    return StartArtifactSessionResponse(
        artifact_session_id=artifact_session_id,
        artifact_type="idea-to-agent",
        questions=questions,
    )

# Note: answer, skip, jump, and synthesize for idea-to-agent use the existing
# /api/artifacts/sessions/{id}/* endpoints — the artifact_type "idea-to-agent"
# is handled by ArtifactBuilderAgent with agent.md-specific synthesis prompting.
