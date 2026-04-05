"""
Supabase-backed conversation persistence.

Table schema (run once in Supabase SQL editor):

    create table conversations (
      id text not null,
      username text not null,
      title text not null default 'New Chat',
      messages jsonb not null default '[]',
      updated_at timestamptz not null default now(),
      primary key (username, id)
    );

    create table feedback (
      id uuid default gen_random_uuid() primary key,
      username text not null,
      comment text not null,
      created_at timestamptz not null default now()
    );
"""
import os
from datetime import datetime
from typing import List, Dict

from supabase import create_client, Client


def _get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)


def _serialize_messages(messages: List[Dict]) -> List[Dict]:
    """Convert datetime objects to ISO strings for JSON storage."""
    result = []
    for m in messages:
        msg = dict(m)
        ts = msg.get("timestamp")
        if isinstance(ts, datetime):
            msg["timestamp"] = ts.isoformat()
        result.append(msg)
    return result


def _deserialize_messages(messages: List[Dict]) -> List[Dict]:
    """Convert ISO timestamp strings back to datetime objects."""
    result = []
    for m in messages:
        msg = dict(m)
        ts = msg.get("timestamp")
        if isinstance(ts, str):
            try:
                msg["timestamp"] = datetime.fromisoformat(ts)
            except ValueError:
                pass
        result.append(msg)
    return result


def load_conversations(username: str) -> List[Dict]:
    """Load the last 5 conversations for a user, newest first."""
    try:
        client = _get_client()
        res = (
            client.table("conversations")
            .select("id, title, messages, updated_at")
            .eq("username", username)
            .order("updated_at", desc=True)
            .limit(5)
            .execute()
        )
        conversations = []
        for row in (res.data or []):
            conv = {
                "id": row["id"],
                "title": row["title"],
                "timestamp": datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")),
                "messages": _deserialize_messages(row.get("messages") or []),
            }
            conversations.append(conv)
        return conversations
    except Exception as e:
        print(f"[conversation_store] load_conversations failed: {e}")
        return []


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


def upsert_conversation(username: str, conversation: Dict) -> None:
    """Save or update a conversation in Supabase."""
    try:
        client = _get_client()
        client.table("conversations").upsert(
            {
                "id": conversation["id"],
                "username": username,
                "title": conversation.get("title", "New Chat"),
                "messages": _serialize_messages(conversation.get("messages", [])),
                "updated_at": datetime.utcnow().isoformat(),
            },
            on_conflict="username,id",
        ).execute()
    except Exception as e:
        print(f"[conversation_store] upsert_conversation failed: {e}")
