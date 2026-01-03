#!/bin/bash
# Script to check for secrets and API keys in the repository

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Scanning repository for secrets and API keys..."

FOUND_ISSUES=0

# Check for API keys in current files (excluding .git, node_modules, and documentation)
PATTERNS=(
    "AIzaSy[0-9A-Za-z_-]{35}"
    "sk-[0-9A-Za-z]{32,}"
)

# Exclude documentation files from pattern matching
EXCLUDE_FILES="--exclude=*.md --exclude=*.txt --exclude=*.sh --exclude=SECURITY.md --exclude=FIX_API_KEY.md"

for pattern in "${PATTERNS[@]}"; do
    results=$(grep -rE $EXCLUDE_FILES "$pattern" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=vector_db --exclude-dir=__pycache__ --exclude-dir=scripts 2>/dev/null | grep -v ".git/hooks" | grep -v "test" | grep -v "example" || true)
    if [ ! -z "$results" ]; then
        echo -e "${RED}❌ Found potential secrets matching pattern: $pattern${NC}"
        echo "$results"
        FOUND_ISSUES=1
    fi
done

# Check for .env files (should only have .env.example)
ENV_FILES=$(find . -name ".env" -not -path "./.git/*" -not -name ".env.example" 2>/dev/null || true)
if [ ! -z "$ENV_FILES" ]; then
    echo -e "${YELLOW}⚠️  Found .env files (should not be in repo):${NC}"
    echo "$ENV_FILES"
    echo -e "${YELLOW}   Consider adding to .gitignore${NC}"
    FOUND_ISSUES=1
fi

# Check git history for API keys
echo ""
echo "🔍 Checking git history for leaked keys (this may take a moment)..."
HISTORY_MATCHES=$(git log --all --full-history -p 2>/dev/null | grep -E "AIzaSy[0-9A-Za-z_-]{35}" | head -5 || true)
if [ ! -z "$HISTORY_MATCHES" ]; then
    echo -e "${RED}❌ WARNING: Found API keys in git history!${NC}"
    echo -e "${RED}   Your repository history contains API keys.${NC}"
    echo -e "${YELLOW}   Consider using git-filter-repo to remove them (advanced)${NC}"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ No API keys found in git history${NC}"
fi

# Summary
echo ""
if [ $FOUND_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ No secrets found! Repository looks secure.${NC}"
    exit 0
else
    echo -e "${RED}❌ Found potential security issues. Review the output above.${NC}"
    exit 1
fi

