#!/bin/bash
# Install git hooks for security protection

HOOK_DIR=".git/hooks"
HOOK_FILE="pre-commit"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOK_DIR"

# Copy pre-commit hook
HOOK_SOURCE="$SCRIPT_DIR/../.git/hooks/pre-commit"
if [ -f "$HOOK_SOURCE" ]; then
    cp "$HOOK_SOURCE" "$HOOK_DIR/$HOOK_FILE"
    chmod +x "$HOOK_DIR/$HOOK_FILE"
    echo "✅ Pre-commit hook installed successfully!"
    echo "   Location: $HOOK_DIR/$HOOK_FILE"
else
    echo "⚠️  Warning: Hook source not found. Creating from template..."
    
    # Create the hook directly
    cat > "$HOOK_DIR/$HOOK_FILE" << 'HOOK_EOF'
#!/bin/bash
# Pre-commit hook to prevent API keys and secrets from being committed

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔒 Checking for secrets and API keys..."

PATTERNS=(
    "AIzaSy[0-9A-Za-z_-]{35}"
    "sk-[0-9A-Za-z]{32,}"
    "AKIA[0-9A-Z]{16}"
    "[0-9a-zA-Z/+=]{40}"
    "xox[baprs]-[0-9a-zA-Z-]{10,48}"
    "ghp_[0-9a-zA-Z]{36}"
    "ghu_[0-9a-zA-Z]{36}"
    "gho_[0-9a-zA-Z]{36}"
    "ghr_[0-9a-zA-Z]{76}"
)

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
FOUND_SECRET=0

for file in $STAGED_FILES; do
    [ ! -f "$file" ] && continue
    
    if git diff --cached -- "$file" | grep -q "^Binary files differ"; then
        continue
    fi
    
    # Skip documentation files (they contain examples)
    if [[ "$file" == *.md ]] || [[ "$file" == *.txt ]] || [[ "$file" == SECURITY.md ]] || [[ "$file" == FIX_API_KEY.md ]] || [[ "$file" == PERMANENT_FIX.md ]]; then
        continue
    fi
    
    for pattern in "${PATTERNS[@]}"; do
        if git diff --cached -- "$file" | grep -qE "$pattern"; then
            echo -e "${RED}❌ SECRET DETECTED!${NC}"
            echo -e "${RED}File: $file${NC}"
            echo -e "${RED}Pattern matched: $pattern${NC}"
            echo -e "${YELLOW}⚠️  Do not commit secrets or API keys!${NC}"
            FOUND_SECRET=1
        fi
    done
    
    if [[ "$file" == *.env && "$file" != *.env.example ]]; then
        echo -e "${RED}❌ ERROR: Attempting to commit .env file: $file${NC}"
        echo -e "${YELLOW}⚠️  .env files should NEVER be committed!${NC}"
        FOUND_SECRET=1
    fi
done

if [ $FOUND_SECRET -eq 1 ]; then
    echo -e "${RED}🚫 Commit blocked!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ No secrets detected. Proceeding...${NC}"
exit 0
HOOK_EOF

    chmod +x "$HOOK_DIR/$HOOK_FILE"
    echo "✅ Pre-commit hook created and installed!"
fi

echo ""
echo "🔒 Security protection is now active!"
echo "   The pre-commit hook will block commits containing API keys."

