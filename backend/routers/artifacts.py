"""
Artifact Builder endpoints — REST + SSE.

SSE event types:
  preview_chunk   {"type": "preview_chunk", "section_key": "...", "content": "..."}
  kb_snippet      {"type": "kb_snippet", "question_id": "...", "snippet": "..."}
  preview_done    {"type": "preview_done", "section_key": "..."}
  token           {"type": "token", "content": "..."}          (synthesis)
  synthesis_done  {"type": "synthesis_done", "html": "..."}    (synthesis complete)
  error           {"type": "error", "message": "..."}
  done            {"type": "done"}
"""
import json

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from data.question_trees import QUESTION_TREES, ARTIFACT_TYPES
from models.artifacts import (
    ArtifactTypesResponse,
    StartArtifactSessionRequest,
    StartArtifactSessionResponse,
    AnswerQuestionRequest,
    SkipQuestionRequest,
    JumpToQuestionRequest,
    JumpToQuestionResponse,
    QuestionOut,
    ArtifactTypeOut,
)
import storage.artifact_session_store as store

router = APIRouter()


@router.get("/artifacts/types", response_model=ArtifactTypesResponse)
async def list_artifact_types():
    return ArtifactTypesResponse(
        artifact_types=[ArtifactTypeOut(**t) for t in ARTIFACT_TYPES]
    )


@router.post("/artifacts/sessions", response_model=StartArtifactSessionResponse)
async def start_artifact_session(req: StartArtifactSessionRequest):
    tree = QUESTION_TREES.get(req.artifact_type)
    if not tree:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Unknown artifact type: {req.artifact_type}")

    artifact_session_id = store.create_session(req.session_id, req.artifact_type)
    questions = [QuestionOut(**q) for q in tree.as_dict_list()]

    return StartArtifactSessionResponse(
        artifact_session_id=artifact_session_id,
        artifact_type=req.artifact_type,
        questions=questions,
    )


@router.get("/artifacts/sessions/{artifact_session_id}")
async def get_artifact_session(artifact_session_id: str):
    session = store.get_session(artifact_session_id)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/artifacts/sessions/{artifact_session_id}/answer")
async def answer_question(
    artifact_session_id: str,
    req: AnswerQuestionRequest,
    request: Request,
):
    """
    Submit an answer for a question.
    Streams per-section preview HTML (EFFICIENT model) + optional KB snippet.
    """
    artifact_agent = request.app.state.artifact_agent

    # Get session + tree
    session = store.get_session(artifact_session_id)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found")

    tree = QUESTION_TREES.get(session["artifact_type"])
    if not tree:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Unknown artifact type")

    # Find the question
    question = next((q for q in tree.questions if q.id == req.question_id), None)
    if not question:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Unknown question id: {req.question_id}")

    async def event_generator():
        # 1. Save the answer
        store.update_answer(artifact_session_id, req.question_id, req.answer)

        # 2. Emit KB snippet if the question has a kb_query
        if question.kb_query:
            snippet = artifact_agent.get_kb_snippet(question.kb_query)
            if snippet:
                yield {
                    "data": json.dumps({
                        "type": "kb_snippet",
                        "question_id": req.question_id,
                        "snippet": snippet,
                    })
                }

        # 3. Stream section preview (EFFICIENT model)
        answers_so_far = session.get("answers") or {}
        answers_so_far[req.question_id] = req.answer  # include current answer

        try:
            async for chunk in artifact_agent.stream_section_preview(
                artifact_type=session["artifact_type"],
                section_key=question.section_key,
                section_label=question.section_label,
                answer=req.answer,
                answers_so_far=answers_so_far,
            ):
                yield {
                    "data": json.dumps({
                        "type": "preview_chunk",
                        "section_key": question.section_key,
                        "content": chunk,
                    })
                }
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}
            return

        yield {"data": json.dumps({"type": "preview_done", "section_key": question.section_key})}
        yield {"data": json.dumps({"type": "done"})}

    return EventSourceResponse(
        event_generator(),
        headers={"X-Accel-Buffering": "no"},
    )


@router.post("/artifacts/sessions/{artifact_session_id}/skip")
async def skip_question(artifact_session_id: str, req: SkipQuestionRequest):
    store.skip_question(artifact_session_id, req.question_id)
    return {"ok": True}


@router.post("/artifacts/sessions/{artifact_session_id}/jump", response_model=JumpToQuestionResponse)
async def jump_to_question(artifact_session_id: str, req: JumpToQuestionRequest):
    session = store.get_session(artifact_session_id)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found")

    tree = QUESTION_TREES.get(session["artifact_type"])
    if not tree:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Unknown artifact type")

    index = next(
        (i for i, q in enumerate(tree.questions) if q.id == req.question_id),
        0,
    )
    store.set_current_index(artifact_session_id, index)
    return JumpToQuestionResponse(current_index=index)


@router.post("/artifacts/sessions/{artifact_session_id}/synthesize")
async def synthesize_artifact(artifact_session_id: str, request: Request):
    """
    Synthesize the complete artifact from all collected answers.
    Uses the FRONTIER model — streams token events, ends with synthesis_done.
    """
    artifact_agent = request.app.state.artifact_agent

    session = store.get_session(artifact_session_id)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found")

    tree = QUESTION_TREES.get(session["artifact_type"])
    if not tree:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Unknown artifact type")

    async def event_generator():
        answers = session.get("answers") or {}
        skipped = session.get("skipped") or []
        questions = tree.as_dict_list()

        accumulated_html = ""
        try:
            async for token in artifact_agent.synthesize_artifact(
                artifact_type=session["artifact_type"],
                artifact_title=tree.title,
                questions=questions,
                answers=answers,
                skipped=skipped,
            ):
                accumulated_html += token
                yield {"data": json.dumps({"type": "token", "content": token})}
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}
            return

        # Save final HTML to DB
        store.set_final_html(artifact_session_id, accumulated_html)

        yield {
            "data": json.dumps({
                "type": "synthesis_done",
                "html": accumulated_html,
                "artifact_type": session["artifact_type"],
                "title": tree.title,
            })
        }
        yield {"data": json.dumps({"type": "done"})}

    return EventSourceResponse(
        event_generator(),
        headers={"X-Accel-Buffering": "no"},
    )
