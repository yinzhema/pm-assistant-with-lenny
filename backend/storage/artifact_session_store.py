"""
Supabase-backed persistence for Artifact Builder sessions.

Run this SQL in your Supabase SQL editor before using:

    create table artifact_sessions (
      id uuid default gen_random_uuid() primary key,
      session_id text not null,
      artifact_type text not null,
      status text not null default 'in_progress',
      answers jsonb not null default '{}',
      skipped jsonb not null default '[]',
      current_question_index int not null default 0,
      final_html text,
      created_at timestamptz not null default now(),
      updated_at timestamptz not null default now()
    );
"""
import json
import os
from typing import Optional

from supabase import create_client, Client

TABLE = "artifact_sessions"


def _get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)


def create_session(session_id: str, artifact_type: str) -> str:
    """Create a new artifact session row and return its UUID."""
    client = _get_client()
    result = (
        client.table(TABLE)
        .insert({"session_id": session_id, "artifact_type": artifact_type})
        .execute()
    )
    return result.data[0]["id"]


def get_session(artifact_session_id: str) -> Optional[dict]:
    client = _get_client()
    result = (
        client.table(TABLE)
        .select("*")
        .eq("id", artifact_session_id)
        .single()
        .execute()
    )
    return result.data


def update_answer(artifact_session_id: str, question_id: str, answer: str) -> bool:
    """Upsert a single answer into the answers JSONB column."""
    client = _get_client()
    session = get_session(artifact_session_id)
    if not session:
        return False
    answers: dict = session.get("answers") or {}
    answers[question_id] = answer

    client.table(TABLE).update(
        {"answers": answers}
    ).eq("id", artifact_session_id).execute()
    return True


def skip_question(artifact_session_id: str, question_id: str) -> bool:
    """Add question_id to the skipped list."""
    client = _get_client()
    session = get_session(artifact_session_id)
    if not session:
        return False
    skipped: list = session.get("skipped") or []
    if question_id not in skipped:
        skipped.append(question_id)
    client.table(TABLE).update({"skipped": skipped}).eq("id", artifact_session_id).execute()
    return True


def set_current_index(artifact_session_id: str, index: int) -> bool:
    client = _get_client()
    client.table(TABLE).update(
        {"current_question_index": index}
    ).eq("id", artifact_session_id).execute()
    return True


def set_final_html(artifact_session_id: str, html: str) -> bool:
    client = _get_client()
    client.table(TABLE).update(
        {"final_html": html, "status": "complete"}
    ).eq("id", artifact_session_id).execute()
    return True
