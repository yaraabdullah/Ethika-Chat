# 🔒 Security Guide - Permanent API Key Protection

This document provides **permanent safeguards** to prevent API key leaks.

## 🛡️ Protection Mechanisms Implemented

### 1. Pre-commit Hook (Automatic Protection)

A pre-commit hook is installed that **automatically blocks commits** containing:
- Google API keys (AIzaSy...)
- OpenAI API keys (sk-...)
- AWS credentials
- GitHub tokens
- Any `.env` files (except `.env.example`)

**Status**: ✅ Installed at `.git/hooks/pre-commit`

**To test it:**
```bash
# Try to commit a file with an API key (should be blocked)
echo 'GEMINI_API_KEY="AIzaSy_test123456789012345678901234567890"' > test.txt
git add test.txt
git commit -m "test"  # Should be BLOCKED
rm test.txt
```

### 2. .gitignore Configuration

✅ **Already configured** to ignore:
- `.env` files
- `.env.local`, `.env.*.local`
- Environment variable files

### 3. Environment Variable Best Practices

**✅ DO:**
- Store API keys in environment variables ONLY
- Use Railway/Heroku environment variables for production
- Create `.env.example` with placeholder values
- Use different API keys for development and production
- Rotate API keys regularly (every 90 days)

**❌ NEVER:**
- Commit API keys to git
- Hardcode API keys in source code
- Share API keys in screenshots, messages, or forums
- Include API keys in logs (unless sanitized)
- Store API keys in config files that get committed

## 📋 Setup Checklist

### For Local Development

1. **Create `.env` file** (never commit it):
   ```bash
   echo "GEMINI_API_KEY=your-api-key-here" > .env
   ```

2. **Verify `.env` is ignored**:
   ```bash
   git status  # Should NOT show .env
   ```

3. **Test pre-commit hook**:
   ```bash
   # Should be blocked:
   echo 'key="AIzaSy_test"' > test.txt && git add test.txt && git commit -m "test"
   rm test.txt
   ```

### For Production (Railway)

1. **Set environment variables in Railway dashboard**
2. **Never hardcode keys in code**
3. **Use Railway's secret management**

## 🔍 How to Check for Leaked Keys

### Check Git History

```bash
# Search git history for API keys
git log --all --full-history -p -S "AIzaSy" -- .

# Search for any Google API keys
git log --all --full-history -p | grep -E "AIzaSy[0-9A-Za-z_-]{35}"
```

### Check Current Repository

```bash
# Search for API keys in current files
grep -r "AIzaSy" . --exclude-dir=.git --exclude-dir=node_modules

# Check for any hardcoded keys
grep -r "GEMINI_API_KEY.*=" . --exclude-dir=.git --exclude-dir=node_modules
```

### If You Find a Leaked Key

1. **IMMEDIATELY revoke the key** at https://aistudio.google.com/apikey
2. **Create a new key**
3. **Update all services** (Railway, local, etc.)
4. **Consider using git-filter-repo** to remove from history (advanced)

## 🔄 Key Rotation Schedule

**Recommended: Rotate API keys every 90 days**

1. Create new key
2. Update all services
3. Test thoroughly
4. Revoke old key after 7 days (buffer period)

## 🚨 Emergency Response

If your API key is leaked:

1. **Immediately revoke** at https://aistudio.google.com/apikey
2. **Check git history** for when it was committed
3. **Create new key**
4. **Update all services**
5. **Review access logs** if available
6. **Consider using git-filter-repo** to remove from history

## 🛠️ Advanced: Using git-secrets (Optional)

For even stronger protection, install `git-secrets`:

```bash
# macOS
brew install git-secrets

# Linux
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets
make install

# Setup for this repo
git secrets --install
git secrets --register-aws
git secrets --add 'AIzaSy[0-9A-Za-z_-]{35}'
git secrets --add 'GEMINI_API_KEY.*=.*["'"'"'][^"'"'"']+["'"'"']'
```

## 📝 Code Review Checklist

Before merging any PR, verify:
- [ ] No API keys in code
- [ ] No `.env` files committed
- [ ] No hardcoded credentials
- [ ] Environment variables used correctly
- [ ] No secrets in logs or error messages

## 🔗 Resources

- Google AI Studio: https://aistudio.google.com/apikey
- Railway Environment Variables: https://docs.railway.app/deploy/environment-variables
- Git Secrets Tool: https://github.com/awslabs/git-secrets
- OWASP Secret Management: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

---

**Remember**: Once a key is committed to git history, it's permanently exposed. Prevention is the only real solution!

