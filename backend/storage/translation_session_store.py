"""
Supabase-backed persistence for PRD → agent.md translation sessions.

Run this SQL in your Supabase SQL editor before using:

    create table translation_sessions (
      id uuid default gen_random_uuid() primary key,
      session_id text not null,
      translation_type text not null,
      status text not null default 'in_progress',
      prd_text text,
      extracted_sections jsonb,
      agent_sections jsonb,
      gaps jsonb,
      clarifications jsonb default '{}',
      final_html text,
      created_at timestamptz not null default now(),
      updated_at timestamptz not null default now()
    );
"""
import os
from typing import Optional

from supabase import create_client, Client

TABLE = "translation_sessions"


def _get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)


def create_session(session_id: str, translation_type: str, prd_text: str = "") -> str:
    client = _get_client()
    result = (
        client.table(TABLE)
        .insert({
            "session_id": session_id,
            "translation_type": translation_type,
            "prd_text": prd_text,
        })
        .execute()
    )
    return result.data[0]["id"]


def get_session(translation_session_id: str) -> Optional[dict]:
    client = _get_client()
    result = (
        client.table(TABLE)
        .select("*")
        .eq("id", translation_session_id)
        .single()
        .execute()
    )
    return result.data


def set_extracted_sections(translation_session_id: str, sections: dict) -> None:
    client = _get_client()
    client.table(TABLE).update(
        {"extracted_sections": sections}
    ).eq("id", translation_session_id).execute()


def set_agent_sections(translation_session_id: str, sections: list) -> None:
    client = _get_client()
    client.table(TABLE).update(
        {"agent_sections": sections}
    ).eq("id", translation_session_id).execute()


def set_gaps(translation_session_id: str, gaps: list) -> None:
    client = _get_client()
    client.table(TABLE).update(
        {"gaps": gaps}
    ).eq("id", translation_session_id).execute()


def add_clarification(translation_session_id: str, question_id: str, answer: str) -> None:
    client = _get_client()
    session = get_session(translation_session_id)
    if not session:
        return
    clarifications: dict = session.get("clarifications") or {}
    clarifications[question_id] = answer
    client.table(TABLE).update(
        {"clarifications": clarifications}
    ).eq("id", translation_session_id).execute()


def update_agent_section(
    translation_session_id: str,
    section_key: str,
    html: str,
    confidence: str,
) -> None:
    client = _get_client()
    session = get_session(translation_session_id)
    if not session:
        return
    sections: list = session.get("agent_sections") or []
    updated = False
    for sec in sections:
        if sec.get("section_key") == section_key:
            sec["html"] = html
            sec["confidence"] = confidence
            updated = True
            break
    if not updated:
        sections.append({"section_key": section_key, "html": html, "confidence": confidence})
    client.table(TABLE).update(
        {"agent_sections": sections}
    ).eq("id", translation_session_id).execute()


def set_final_html(translation_session_id: str, html: str) -> None:
    client = _get_client()
    client.table(TABLE).update(
        {"final_html": html, "status": "complete"}
    ).eq("id", translation_session_id).execute()
