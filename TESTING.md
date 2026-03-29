# Testing Guide

This document outlines how to test the PM Assistant system.

## Pre-Testing Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up `.env` with your OpenAI API key
3. Run ingestion (at least one episode): `python scripts/ingest_transcripts.py --episode brian-chesky`

## Component Testing

### 1. Test Parser

```bash
python -m src.ingestion.parser
```

**Expected Output:**
- Episode metadata (title, guest, keywords)
- Number of dialogue entries
- Sample dialogue with speaker and timestamp

### 2. Test Chunker

```bash
python -m src.ingestion.chunker
```

**Expected Output:**
- Number of chunks created
- Token counts for chunks
- Sample chunk text

### 3. Test Embedder

```bash
python -m src.ingestion.embedder
```

**Expected Output:**
- Embedding dimension (1536)
- First few embedding values
- Success message

### 4. Test Vector Store

```bash
python -m src.retrieval.vector_store
```

**Expected Output:**
- Total chunks in store
- List of episodes

### 5. Test Retriever

```bash
python -m src.retrieval.retriever
```

**Expected Output:**
- Query results with similarity scores
- Source information

### 6. Test PM Assistant

```bash
python -m src.agent.pm_assistant
```

**Expected Output:**
- Answer to test question
- Source citations with links

## Integration Testing

### Test Full Ingestion Pipeline

```bash
# Ingest a single episode
python scripts/ingest_transcripts.py --episode brian-chesky

# Verify it worked
python -m src.retrieval.vector_store
```

**Expected:**
- Chunks added to vector store
- No errors during processing

### Test Query Flow

```bash
# Run the assistant test
python -m src.agent.pm_assistant
```

**Test Questions:**
1. "How do I find product-market fit?"
2. "What makes a great product manager?"
3. "How should I prioritize features?"

**Expected:**
- Relevant answers
- Multiple source citations
- YouTube links with timestamps

## UI Testing

### Start the App

```bash
streamlit run app.py
```

### Manual Test Cases

#### Test Case 1: Basic Query
1. Open app in browser
2. Type: "How do I find product-market fit?"
3. Submit query

**Expected:**
- Answer appears within 5-10 seconds
- Sources section is expandable
- YouTube links work
- Similarity scores shown

#### Test Case 2: Follow-up Question
1. Ask initial question: "What is product-market fit?"
2. Ask follow-up: "How do I measure it?"

**Expected:**
- Context from previous question maintained
- Relevant answer to follow-up

#### Test Case 3: Example Questions
1. Click an example question in sidebar
2. Verify it auto-submits

**Expected:**
- Question appears in chat
- Answer generated automatically

#### Test Case 4: Settings
1. Adjust "Number of sources" slider
2. Ask a question

**Expected:**
- Number of sources matches slider value

#### Test Case 5: Clear History
1. Have a conversation (2-3 exchanges)
2. Click "Clear Chat History"

**Expected:**
- All messages cleared
- Fresh start

## Performance Testing

### Response Time

Measure time from query submission to answer display:

**Acceptable:**
- < 5 seconds for simple queries
- < 10 seconds for complex queries

**If slower:**
- Check internet connection
- Reduce number of sources
- Verify OpenAI API status

### Embedding Generation

Time for ingesting 10 episodes:

**Expected:**
- ~2-3 minutes for 10 episodes
- ~10-15 minutes for all 300+ episodes

### Memory Usage

Monitor during ingestion:

**Expected:**
- < 2GB RAM during ingestion
- < 500MB RAM during queries

## Quality Testing

### Answer Relevance

For each test question, verify:
- [ ] Answer is relevant to question
- [ ] Sources support the answer
- [ ] Citations are accurate
- [ ] No hallucinations (made-up information)

### Test Questions & Expected Behavior

| Question | Expected Sources | Key Points |
|----------|-----------------|------------|
| "How do I find PMF?" | Rahul Vohra, Brian Chesky | Superhuman framework, iteration |
| "What makes a great PM?" | Multiple leaders | Skills, mindset, frameworks |
| "How to prioritize?" | Multiple sources | Frameworks (RICE, etc.) |
| "Building product culture?" | Brian Chesky, others | Values, processes |

### Edge Cases

#### Empty Query
- Type nothing and submit
- **Expected:** Prompt for input or graceful handling

#### Very Long Query
- Paste 500+ word question
- **Expected:** Still processes, may truncate

#### Rapid Queries
- Submit 5 queries quickly
- **Expected:** All process in order

#### No Results
- Ask about unrelated topic (e.g., "quantum physics")
- **Expected:** Graceful "no relevant information" message

## Error Testing

### Missing API Key

```bash
# Remove API key from .env
streamlit run app.py
```

**Expected:**
- Clear error message
- Instructions to add key

### Empty Vector Store

```bash
# Delete vector store
rm -rf data/chroma_db/*
streamlit run app.py
```

**Expected:**
- Warning message
- Instructions to run ingestion

### Network Issues

Disconnect internet and try query:

**Expected:**
- Error message about API connection
- Graceful failure

## Regression Testing

After making changes, verify:

1. [ ] Ingestion still works
2. [ ] Queries return relevant results
3. [ ] Citations are accurate
4. [ ] UI loads without errors
5. [ ] All example questions work

## Automated Testing (Future)

Consider adding:
- Unit tests for each module
- Integration tests for full pipeline
- UI tests with Selenium
- Performance benchmarks

## Reporting Issues

When reporting bugs, include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Error messages (if any)
4. System info (OS, Python version)
5. Relevant logs

## Success Criteria

System is ready for deployment when:
- [x] All component tests pass
- [x] Integration tests pass
- [x] UI is responsive and functional
- [x] Answers are relevant and accurate
- [x] Citations work correctly
- [x] Performance is acceptable
- [ ] No critical bugs
- [ ] Documentation is complete

---

**Last Updated:** 2026-03-29