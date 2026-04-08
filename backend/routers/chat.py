"""
SSE streaming chat endpoint.
"""
import json

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from models.chat import ChatRequest

router = APIRouter()


@router.post("/chat")
async def chat(req: ChatRequest, request: Request):
    """
    Stream chat responses as Server-Sent Events.

    Event types emitted:
      - token:            {"type": "token", "content": "..."}
      - sources:          {"type": "sources", "sources": [...]}
      - template_created: {"type": "template_created", "template_id": "...", "template_name": "...", "html": "..."}
      - template_offer:   {"type": "template_offer", "template_id": "...", "template_name": "..."}
      - error:            {"type": "error", "message": "..."}
      - done:             {"type": "done"}
    """
    pm_assistant = request.app.state.pm_assistant
    doc_agent = request.app.state.doc_agent

    async def event_generator():
        history = [{"role": m.role, "content": m.content} for m in req.history]

        # 1. Retrieve context (sync, fast)
        try:
            retrieval_result = pm_assistant.retriever.retrieve_with_context(req.message, n_results=8)
            context = retrieval_result["context"]
            sources = retrieval_result["sources"]
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": f"Retrieval failed: {e}"})}
            return

        # 2. Build messages
        messages = [{"role": "system", "content": pm_assistant.system_prompt}]
        if history:
            messages.extend(history)
        user_message = (
            f"Based on the following insights from the PM knowledge base, "
            f"please answer this question:\n\n"
            f"Question: {req.message}\n\n"
            f"Relevant Insights:\n{context}\n\n"
            f"Please provide a helpful answer with specific citations."
        )
        messages.append({"role": "user", "content": user_message})

        # 3. Stream tokens
        try:
            stream = pm_assistant.client.chat.completions.create(
                model=pm_assistant.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield {"data": json.dumps({"type": "token", "content": delta})}
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}
            return

        # 4. Emit sources
        yield {"data": json.dumps({"type": "sources", "sources": sources})}

        # 5. Detect template intent (full message)
        from services.document_agent import TEMPLATES

        full_message = req.message
        template_id = doc_agent.detect_template_intent(full_message)
        if template_id:
            # Auto-generate document
            try:
                html = doc_agent.generate_from_template(template_id, full_message, history or None)
                yield {
                    "data": json.dumps({
                        "type": "template_created",
                        "template_id": template_id,
                        "template_name": TEMPLATES.get(template_id, template_id),
                        "html": html,
                    })
                }
            except Exception as e:
                yield {"data": json.dumps({"type": "error", "message": f"Template generation failed: {e}"})}
        else:
            # Check for mention (offer CTA)
            mention_id = doc_agent.detect_template_mention(full_message)
            if mention_id:
                yield {
                    "data": json.dumps({
                        "type": "template_offer",
                        "template_id": mention_id,
                        "template_name": TEMPLATES.get(mention_id, mention_id),
                    })
                }

        yield {"data": json.dumps({"type": "done"})}

    return EventSourceResponse(event_generator())
