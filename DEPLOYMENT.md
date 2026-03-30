# 🚀 Deployment Guide - PM Assistant with Lenny

Complete guide for deploying the PM Assistant to Streamlit Cloud.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free tier available at [share.streamlit.io](https://share.streamlit.io))
- OpenAI API key
- Completed ingestion (vector database in `data/chroma_db/`)

## Deployment Steps

### 1. Prepare Your Repository

#### A. Ensure Vector Database is Ready

```bash
# Run ingestion locally first (if not already done)
python scripts/ingest_transcripts.py

# Verify the database exists
ls -la data/chroma_db/
```

**Important**: The `data/chroma_db/` directory must be committed to your repository for deployment.

#### B. Update .gitignore

Make sure your `.gitignore` does NOT exclude the vector database:

```bash
# Check if chroma_db is excluded
cat .gitignore | grep chroma

# If it's excluded, remove that line from .gitignore
```

The vector database should be included in your repository for Streamlit Cloud deployment.

#### C. Commit and Push to GitHub

```bash
# Add all files
git add .

# Commit changes
git commit -m "Prepare for Streamlit Cloud deployment"

# Push to GitHub
git push origin main
```

### 2. Deploy on Streamlit Cloud

#### A. Sign Up / Log In

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Authorize Streamlit to access your repositories

#### B. Create New App

1. Click **"New app"** button
2. Select your repository: `pm-assistant-with-lenny`
3. Choose branch: `main` (or your default branch)
4. Set main file path: `app.py`
5. Click **"Advanced settings"** (optional but recommended)

#### C. Configure Advanced Settings

**Python Version**: 3.9 or higher

**Secrets**: Add your OpenAI API key

```toml
# In the Secrets section, add:
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

**Note**: Never commit your `.env` file with real API keys to GitHub!

#### D. Deploy

1. Click **"Deploy!"**
2. Wait 2-5 minutes for initial deployment
3. Your app will be live at: `https://[your-app-name].streamlit.app`

### 3. Post-Deployment

#### A. Test Your Deployment

1. Visit your app URL
2. Create an account / log in
3. Click "New Chat"
4. Ask a sample question
5. Verify sources are loading correctly

#### B. Monitor Your App

- **Logs**: View real-time logs in Streamlit Cloud dashboard
- **Analytics**: Check usage metrics
- **Errors**: Monitor for any runtime errors

### 4. Update Your Deployment

When you make changes:

```bash
# Make your changes locally
# Test locally first
streamlit run app.py

# Commit and push
git add .
git commit -m "Update: description of changes"
git push origin main

# Streamlit Cloud will auto-deploy (usually within 1-2 minutes)
```

## Configuration Files

### Required Files for Deployment

1. **`app.py`** - Main application file
2. **`requirements.txt`** - Python dependencies
3. **`data/chroma_db/`** - Vector database (must be committed)
4. **`src/`** - Backend code
5. **`episodes/`** - Podcast transcripts (optional, used for ingestion)

### Optional Configuration

Create `.streamlit/config.toml` for custom settings:

```toml
[theme]
primaryColor = "#2563eb"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f1f5f9"
textColor = "#0f172a"

[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true
```

## Environment Variables

### Local Development (.env)

```bash
OPENAI_API_KEY=sk-your-key-here
```

### Streamlit Cloud (Secrets)

Add in Streamlit Cloud dashboard under **Settings > Secrets**:

```toml
OPENAI_API_KEY = "sk-your-key-here"
```

## Troubleshooting

### Common Issues

#### 1. "Vector store is empty"

**Problem**: Database not found or not committed to repository

**Solution**:
```bash
# Ensure database exists
ls -la data/chroma_db/

# Make sure it's not in .gitignore
cat .gitignore | grep chroma

# Commit and push
git add data/chroma_db/
git commit -m "Add vector database"
git push origin main
```

#### 2. "OPENAI_API_KEY not found"

**Problem**: API key not configured in Streamlit Cloud

**Solution**:
1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Go to **Settings > Secrets**
4. Add: `OPENAI_API_KEY = "sk-your-key"`
5. Save and reboot app

#### 3. "Module not found" errors

**Problem**: Missing dependencies in requirements.txt

**Solution**:
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

#### 4. App is slow or timing out

**Problem**: Large vector database or cold start

**Solutions**:
- Streamlit Cloud free tier has resource limits
- Consider upgrading to paid tier for better performance
- Optimize vector database size if needed
- Use caching effectively (already implemented with `@st.cache_resource`)

#### 5. Authentication not working

**Problem**: Session state issues

**Solution**:
- This is expected behavior - sessions are per-browser
- Users need to log in each time they visit
- For persistent auth, consider adding a database backend

## Cost Considerations

### Streamlit Cloud Free Tier

- **Cost**: Free
- **Resources**: 1 GB RAM, 1 CPU
- **Apps**: Up to 3 public apps
- **Limitations**: 
  - May sleep after inactivity
  - Limited concurrent users
  - Slower performance

### Streamlit Cloud Pro

- **Cost**: $20/month per user
- **Resources**: More RAM and CPU
- **Apps**: Unlimited
- **Benefits**:
  - Always-on apps
  - Better performance
  - More concurrent users
  - Priority support

### OpenAI API Costs

**Per Query** (approximate):
- Embedding lookup: Free (local vector search)
- GPT-4o-mini response: ~$0.0002 per query
- **Monthly estimate** (100 queries): ~$0.02

**One-time Setup**:
- Initial ingestion: ~$0.60 (already done locally)

## Security Best Practices

### 1. Never Commit Secrets

```bash
# Always use .env for local development
echo "OPENAI_API_KEY=sk-..." > .env

# Make sure .env is in .gitignore
echo ".env" >> .gitignore
```

### 2. Use Streamlit Secrets

- Store all API keys in Streamlit Cloud Secrets
- Never hardcode keys in your code
- Use `st.secrets` or `os.getenv()` to access keys

### 3. Implement Rate Limiting

Consider adding rate limiting for production:

```python
# Example: Limit queries per user
if "query_count" not in st.session_state:
    st.session_state.query_count = 0

if st.session_state.query_count > 50:
    st.error("Daily query limit reached. Please try again tomorrow.")
    st.stop()
```

## Monitoring and Maintenance

### 1. Check Logs Regularly

- View logs in Streamlit Cloud dashboard
- Monitor for errors or unusual activity
- Set up alerts for critical issues

### 2. Update Dependencies

```bash
# Periodically update packages
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
git commit -am "Update dependencies"
git push
```

### 3. Monitor API Usage

- Check OpenAI dashboard for API usage
- Set up billing alerts
- Monitor for unexpected spikes

### 4. Backup Your Data

```bash
# Backup vector database
tar -czf chroma_db_backup.tar.gz data/chroma_db/

# Store backup securely (not in git)
```

## Alternative Deployment Options

### 1. Docker Container

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. AWS / GCP / Azure

- Deploy Docker container to cloud provider
- Use managed services for better scalability
- More complex but more control

### 3. Self-Hosted

```bash
# Run on your own server
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Support

### Getting Help

1. **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
2. **Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
3. **GitHub Issues**: Report bugs in your repository

### Useful Links

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Deployment Tutorial](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)

---

## Quick Deployment Checklist

- [ ] Vector database created (`data/chroma_db/`)
- [ ] Database committed to git
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud account created
- [ ] App deployed on Streamlit Cloud
- [ ] OpenAI API key added to Secrets
- [ ] App tested and working
- [ ] Monitoring set up

**Ready to deploy?** Follow the steps above and your PM Assistant will be live in minutes! 🚀