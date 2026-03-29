# Quick Start Guide

Get your PM Assistant running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up OpenAI API Key

1. Get your API key from [OpenAI](https://platform.openai.com/api-keys)
2. Create a `.env` file:

```bash
cp .env.example .env
```

3. Edit `.env` and add your key:

```
OPENAI_API_KEY=sk-your-key-here
```

## Step 3: Ingest Transcripts (One-Time Setup)

This processes all podcast transcripts and creates embeddings:

```bash
python scripts/ingest_transcripts.py
```

**Time**: ~10-15 minutes  
**Cost**: ~$0.60 in OpenAI credits

### Quick Test (Optional)

To test with just one episode first:

```bash
python scripts/ingest_transcripts.py --episode brian-chesky
```

## Step 4: Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Step 5: Ask Questions!

Try these example questions:
- "How do I find product-market fit?"
- "What makes a great product manager?"
- "How should I prioritize my roadmap?"

## Troubleshooting

### "Vector store is empty"
You need to run the ingestion script first (Step 3)

### "OPENAI_API_KEY not found"
Make sure your `.env` file exists and has the correct key

### Import errors
Run `pip install -r requirements.txt` again

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [PLAN.md](PLAN.md) for technical architecture
- Deploy to Streamlit Cloud (see README.md)

---

**Need help?** Open an issue on GitHub