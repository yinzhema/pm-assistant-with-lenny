# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a static content archive containing 303 episode transcripts from Lenny's Podcast, with an AI-generated topic index for easy discovery.

## Structure

```
├── episodes/
│   └── {guest-name}/
│       └── transcript.md    # YAML frontmatter + transcript content
├── index/
│   ├── README.md            # Main entry point with topic links
│   └── {topic}.md           # Individual topic files (e.g., product-management.md)
└── scripts/
    └── build-index.sh       # Script to regenerate the topic index
```

## Transcript Format

Each transcript.md contains:
- **YAML frontmatter**: guest, title, youtube_url, video_id, publish_date, description, duration_seconds, duration, view_count, channel, keywords
- **Transcript content**: Timestamped speaker dialogue

The `publish_date` field is in YYYY-MM-DD format and represents the YouTube upload date.

## Index

The `index/` folder contains AI-generated keyword tags for each episode:
- Topic files (e.g., `product-management.md`) - Episodes grouped by topic keyword

## Working with Large Transcript Files

Transcript files are large (often 25,000+ tokens). Use these strategies:

### 1. Use Grep for targeted searches (preferred)
```
# Search for specific topics across all transcripts
Grep pattern="product.market fit" path="episodes/"

# Search with context lines for better understanding
Grep pattern="early stage" path="episodes/" output_mode="content" -C=5
```

### 2. Read frontmatter first (lines 1-15)
Get metadata before deciding to read more:
```
Read file_path="episodes/guest-name/transcript.md" limit=15
```

### 3. Read in chunks when needed
For sequential reading, use offset/limit:
```
Read file_path="..." offset=1 limit=500    # First chunk
Read file_path="..." offset=500 limit=500  # Second chunk
```

### 4. Use Task tool with Explore agent
For research across multiple transcripts:
```
Task subagent_type="Explore" prompt="Find insights about X across transcripts"
```

### 5. Handle persisted output
When Read returns a persisted output path like:
`Output saved to: ~/.claude/.../tool-results/xxx.txt`
Read that file to access the full content.

## Rebuilding the Index

```bash
./scripts/build-index.sh
```

This calls Claude CLI for each episode to generate keywords. The script is idempotent - it skips episodes already present in keyword files, so it can be run multiple times safely.

## Adding Publication Dates

All episodes should include `publish_date` in ISO 8601 format (YYYY-MM-DD). To fetch the publication date for a new episode:

1. Use the `video_id` from the transcript's frontmatter
2. Call the YouTube Data API v3:
   ```
   https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={API_KEY}
   ```
3. Extract `snippet.publishedAt` from the response
4. Add `publish_date: YYYY-MM-DD` to the frontmatter after `video_id`

---

## Phase 1 Architecture (completed)

The app now uses a **multi-source RAG pipeline** with hybrid retrieval. Key files added:

```
src/ingestion/sources/       # Source abstractions
  base.py                    # RawDocument dataclass + BaseSource ABC
  rss_source.py              # RSS/Atom feed ingestion (feedparser + BeautifulSoup)
  html_scraper.py            # HTML blog scraping
  registry.py                # All SOURCES instances — edit here to add/remove sources
src/ingestion/
  article_chunker.py         # Paragraph-aware chunking for articles (700 tokens, 100 overlap)
  deduplicator.py            # URL + content_hash dedup against Pinecone
src/retrieval/
  bm25_index.py              # In-memory BM25 (rank_bm25), corpus at data/bm25_corpus.jsonl
  hybrid_retriever.py        # RRF fusion (70% semantic + 30% BM25) + credibility tier boost
scripts/
  ingest_web_sources.py      # CLI: python scripts/ingest_web_sources.py [--source X] [--dry-run]
.github/workflows/
  ingest_sources.yml         # Weekly cron + manual GitHub Actions trigger
```

### Ingestion pipeline (new sources)
```
source.fetch_documents() → deduplicator.filter_new() → article_chunker.chunk_document()
→ embedder.embed_chunks() → vector_store.add_chunks() → bm25_index.add_chunks() → bm25_index.save()
```

### Extended Pinecone metadata schema
New chunks include: `source_name`, `source_id`, `source_type`, `author`, `url`, `credibility_tier`, `content_hash`.
Old Lenny podcast chunks lack these fields — retrieval code defaults gracefully (treats missing tier as tier-1).

---

## Phase 2 — AI Coworker Workspace (DEFERRED — implement next)

### Goal
Add a two-panel document canvas alongside the chat: generate PM artifacts, edit inline, AI co-edit, save, and export.

### Frontend Architecture: Stay on Streamlit
Use `st.columns([1, 1])` for the two-panel layout + a custom Streamlit component wrapping **Tiptap editor** (CDN, no Node.js build). The Tiptap component fires events to Python only on explicit user actions (not every keystroke), keeping Streamlit re-render cost acceptable.

### Layout
```python
# Workspace mode
col_chat, col_canvas = st.columns([1, 1], gap="medium")
# Chat mode (existing)
render_single_column_chat()
```
Remove `max-width: 760px` CSS when `workspace_mode` is True.

### Templates
| Category | Templates |
|----------|-----------|
| Docs | PRD (1-pager), PRD (full), Strategy doc |
| Prioritization | RICE, ICE, MoSCoW, Kano, WSJF |
| Roadmap | Now/Next/Later, Outcome-based |
| Discovery | Jobs-to-be-done, Opportunity Solution Tree |

### New Files to Create
| File | Purpose |
|------|---------|
| `src/ui/document_canvas.py` | `render_canvas()`, `render_template_picker()`, `render_canvas_toolbar()` |
| `src/ui/tiptap_component/__init__.py` | `st.components.v1.declare_component` wrapper |
| `src/ui/tiptap_component/index.html` | Self-contained Tiptap editor (CDN, StarterKit + Table) |
| `src/ui/tiptap_component/component.js` | Editor init, onChange, selection menu (Improve/Expand/Critique/Simplify) |
| `src/agent/document_agent.py` | `DocumentAgent` (GPT-4o) — `generate_from_template()`, `improve_selection()`, `critique_document()`, `detect_template_intent()` |
| `src/storage/document_store.py` | Supabase CRUD — save/load/list documents + 3-version history |
| `src/agent/export.py` | `export_to_markdown()` (markdownify), `export_to_excel()` (openpyxl) |

### Supabase SQL (run before implementing)
```sql
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

create or replace function trim_versions() returns trigger as $$
begin
  delete from document_versions
  where document_id = NEW.document_id
    and id not in (
      select id from document_versions
      where document_id = NEW.document_id
      order by version_number desc limit 3
    );
  return NEW;
end;
$$ language plpgsql;

create trigger after_version_insert
  after insert on document_versions
  for each row execute function trim_versions();
```

### app.py Changes (Phase 2)
- Add "Workspace" button to top bar
- Add session state: `workspace_mode`, `active_document`, `document_id`
- Wrap existing chat in `render_single_column_chat()`
- Add `render_workspace()` calling `render_chat_panel()` + `render_document_canvas()`
- Route canvas AI action events to `DocumentAgent`
- Conditional wide-layout CSS

### pm_assistant.py Changes (Phase 2)
Add `detect_template_intent(message) -> Optional[str]` — detects if a chat message intends to create a PM artifact.

### New requirements (Phase 2)
```
markdownify>=0.11.6
openpyxl>=3.1.2
html2text>=2024.2.26
```

### AI Co-editing Flow
```
User highlights text → Tiptap selection menu → clicks "Improve"
→ component sends {action, selectedText, fullHtml} → DocumentAgent.improve_selection()
→ replacement HTML → Tiptap replaces selection
```

### Document Persistence
- Autosave every 60s if dirty → `document_store.save_document()`
- Manual save + version bump via toolbar
- Max 3 versions retained (Postgres trigger)
- Export: MD (`st.download_button`) and Excel (`st.download_button`)
