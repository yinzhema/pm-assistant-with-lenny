"""
Supabase-backed feedback storage.

Table schema (run once in Supabase SQL editor):

    create table feedback (
      id uuid default gen_random_uuid() primary key,
      username text not null,
      comment text not null,
      created_at timestamptz not null default now()
    );
"""
import os

from supabase import create_client, Client


def _get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)


def submit_feedback(username: str, comment: str) -> None:
    """Save a feedback comment to Supabase."""
    try:
        client = _get_client()
        client.table("feedback").insert({
            "username": username,
            "comment": comment,
        }).execute()
    except Exception as e:
        print(f"[conversation_store] submit_feedback failed: {e}")
