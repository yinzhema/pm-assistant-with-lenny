#!/bin/bash

# Deployment Preparation Script for PM Assistant
# This script prepares your repository for Streamlit Cloud deployment

set -e  # Exit on error

echo "🚀 PM Assistant - Deployment Preparation"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: app.py not found. Please run this script from the project root.${NC}"
    exit 1
fi

echo "✅ Found app.py - in correct directory"
echo ""

# Check if vector database exists
if [ ! -d "data/chroma_db" ]; then
    echo -e "${RED}❌ Error: Vector database not found at data/chroma_db/${NC}"
    echo "Please run: python scripts/ingest_transcripts.py"
    exit 1
fi

echo "✅ Vector database found"
DB_SIZE=$(du -sh data/chroma_db/ | cut -f1)
echo "   Size: $DB_SIZE"
echo ""

# Check database size
DB_SIZE_MB=$(du -sm data/chroma_db/ | cut -f1)
if [ $DB_SIZE_MB -gt 100 ]; then
    echo -e "${YELLOW}⚠️  Warning: Database is ${DB_SIZE_MB}MB (>100MB)${NC}"
    echo "   GitHub has a 100MB file size limit per file"
    echo "   Consider using Git LFS for large files"
    echo ""
    
    # Check if Git LFS is installed
    if command -v git-lfs &> /dev/null; then
        echo "   Git LFS is installed ✅"
        echo ""
        read -p "   Would you like to set up Git LFS for the database? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "   Setting up Git LFS..."
            git lfs install
            git lfs track "data/chroma_db/**"
            git add .gitattributes
            echo "   ✅ Git LFS configured"
        fi
    else
        echo "   Git LFS not installed. Install with:"
        echo "   brew install git-lfs  (macOS)"
        echo "   or visit: https://git-lfs.github.com/"
    fi
    echo ""
fi

# Check .env file
if [ -f ".env" ]; then
    echo "✅ .env file found (for local development)"
    if grep -q "OPENAI_API_KEY" .env; then
        echo "   Contains OPENAI_API_KEY ✅"
    else
        echo -e "${YELLOW}   ⚠️  OPENAI_API_KEY not found in .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "   Create one from .env.example for local testing"
fi
echo ""

# Check .gitignore
if grep -q "^data/chroma_db/" .gitignore; then
    echo -e "${RED}❌ Error: data/chroma_db/ is in .gitignore${NC}"
    echo "   The database needs to be committed for deployment"
    echo "   Remove this line from .gitignore"
    exit 1
else
    echo "✅ Vector database not in .gitignore (will be committed)"
fi
echo ""

# Check requirements.txt
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
    
    # Check for key dependencies
    REQUIRED_DEPS=("streamlit" "openai" "chromadb" "python-dotenv")
    MISSING_DEPS=()
    
    for dep in "${REQUIRED_DEPS[@]}"; do
        if ! grep -q "$dep" requirements.txt; then
            MISSING_DEPS+=("$dep")
        fi
    done
    
    if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
        echo "   All required dependencies present ✅"
    else
        echo -e "${YELLOW}   ⚠️  Missing dependencies: ${MISSING_DEPS[*]}${NC}"
        echo "   Run: pip freeze > requirements.txt"
    fi
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    echo "   Run: pip freeze > requirements.txt"
    exit 1
fi
echo ""

# Check git status
echo "📊 Git Status:"
echo "-------------"
git status --short
echo ""

# Summary
echo "📋 Deployment Checklist:"
echo "----------------------"
echo "✅ Vector database exists ($DB_SIZE)"
echo "✅ Database not in .gitignore"
echo "✅ requirements.txt present"
echo "✅ .env file for local dev"
echo ""

# Next steps
echo "🎯 Next Steps:"
echo "-------------"
echo "1. Review changes: git status"
echo "2. Add all files: git add ."
echo "3. Commit: git commit -m 'Prepare for Streamlit Cloud deployment'"
echo "4. Push to GitHub: git push origin main"
echo ""
echo "5. Deploy on Streamlit Cloud:"
echo "   - Go to https://share.streamlit.io"
echo "   - Click 'New app'"
echo "   - Select your repository"
echo "   - Set main file: app.py"
echo "   - Add OPENAI_API_KEY to Secrets"
echo "   - Deploy!"
echo ""

# Ask if user wants to proceed with git add
read -p "Would you like to add all files to git now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Adding files to git..."
    git add .
    echo ""
    echo "✅ Files added. Review with: git status"
    echo ""
    echo "Next: git commit -m 'Prepare for deployment'"
fi

echo ""
echo "🎉 Preparation complete!"

# Made with Bob
