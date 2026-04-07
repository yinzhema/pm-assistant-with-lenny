"""
Supabase-backed document persistence for the AI Coworker Workspace.

Run this SQL in your Supabase SQL editor before using:

    create table documents (
      id uuid default gen_random_uuid() primary key,
      session_id text not null,
      title text not null default 'Untitled',
      template_id text not null,
      content_html text not null,
      created_at timestamptz not null default now(),
      updated_at timestamptz not null default now()
    );

    create table document_versions (
      id uuid default gen_random_uuid() primary key,
      document_id uuid not null references documents(id) on delete cascade,
      content_html text not null,
      version_number int not null,
      created_at timestamptz not null default now()
    );

    -- Keep only the last 3 versions per document
    create or replace function trim_versions() returns trigger as $$
    begin
      delete from document_versions
      where document_id = NEW.document_id
        and id not in (
          select id from document_versions
          where document_id = NEW.document_id
          order by version_number desc
          limit 3
        );
      return NEW;
    end;
    $$ language plpgsql;

    create trigger after_version_insert
      after insert on document_versions
      for each row execute function trim_versions();
"""
import os
from typing import Optional, List, Dict

from supabase import create_client, Client


def _get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)


def save_document(
    session_id: str,
    title: str,
    template_id: str,
    content_html: str,
    document_id: Optional[str] = None,
) -> Optional[str]:
    """
    Insert or update a document. On update, saves a version snapshot.
    Returns the document UUID string, or None on failure.
    """
    try:
        client = _get_client()

        if document_id:
            # Fetch current version count to set next version_number
            versions = (
                client.table("document_versions")
                .select("version_number")
                .eq("document_id", document_id)
                .order("version_number", desc=True)
                .limit(1)
                .execute()
            )
            next_ver = (versions.data[0]["version_number"] + 1) if versions.data else 1

            # Snapshot current content before overwriting
            current = (
                client.table("documents")
                .select("content_html")
                .eq("id", document_id)
                .single()
                .execute()
            )
            if current.data:
                client.table("document_versions").insert({
                    "document_id": document_id,
                    "content_html": current.data["content_html"],
                    "version_number": next_ver,
                }).execute()

            # Update document
            client.table("documents").update({
                "title": title,
                "content_html": content_html,
                "updated_at": "now()",
            }).eq("id", document_id).execute()
            return document_id

        else:
            result = client.table("documents").insert({
                "session_id": session_id,
                "title": title,
                "template_id": template_id,
                "content_html": content_html,
            }).execute()
            return result.data[0]["id"] if result.data else None

    except Exception as e:
        print(f"[document_store] save_document failed: {e}")
        return None


def load_document(document_id: str) -> Optional[Dict]:
    """Load a document by ID. Returns None if not found."""
    try:
        result = (
            _get_client()
            .table("documents")
            .select("*")
            .eq("id", document_id)
            .single()
            .execute()
        )
        return result.data
    except Exception as e:
        print(f"[document_store] load_document failed: {e}")
        return None


def list_documents(session_id: str) -> List[Dict]:
    """List all documents for a session, newest first."""
    try:
        result = (
            _get_client()
            .table("documents")
            .select("id, title, template_id, updated_at")
            .eq("session_id", session_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[document_store] list_documents failed: {e}")
        return []


def get_versions(document_id: str) -> List[Dict]:
    """Return the last 3 versions for a document, newest first."""
    try:
        result = (
            _get_client()
            .table("document_versions")
            .select("id, version_number, created_at")
            .eq("document_id", document_id)
            .order("version_number", desc=True)
            .limit(3)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[document_store] get_versions failed: {e}")
        return []


def restore_version(document_id: str, version_id: str) -> Optional[str]:
    """
    Restore a previous version as the current document content.
    Returns the restored HTML, or None on failure.
    """
    try:
        client = _get_client()
        ver = (
            client.table("document_versions")
            .select("content_html")
            .eq("id", version_id)
            .single()
            .execute()
        )
        if not ver.data:
            return None
        html = ver.data["content_html"]
        client.table("documents").update({
            "content_html": html,
            "updated_at": "now()",
        }).eq("id", document_id).execute()
        return html
    except Exception as e:
        print(f"[document_store] restore_version failed: {e}")
        return None
