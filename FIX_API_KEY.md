# 🚨 FIX: API Key Reported as Leaked (403 Error)

## What Happened?
Your Gemini API key was reported as leaked. This happens when an API key is accidentally exposed (e.g., in GitHub commits, logs, or public repositories). Google automatically disables leaked keys for security.

## ✅ Solution: Get a NEW API Key

### Step 1: Create a New Gemini API Key

1. **Go to Google AI Studio**: https://aistudio.google.com/apikey
2. **Sign in** with your Google account
3. **Click "Create API Key"** or **"Get API Key"**
4. **Choose an existing project** or **create a new one**
5. **Copy the new API key** (it looks like: `AIzaSy...`)

### Step 2: Update on Railway (Production)

1. **Go to your Railway project**: https://railway.app
2. **Click on your project** → **Variables** tab
3. **Find `GEMINI_API_KEY`** in the list
4. **Click the edit/pencil icon**
5. **Paste your NEW API key**
6. **Save**
7. **Redeploy** (Railway will automatically redeploy when you save)

### Step 3: Update Locally (Development)

**Option A: Environment Variable (Recommended)**
```bash
export GEMINI_API_KEY="your-new-api-key-here"
```

**Option B: Create .env file**
```bash
# Create .env file in project root
echo "GEMINI_API_KEY=your-new-api-key-here" > .env
```

⚠️ **NEVER commit .env files to Git!** (It's already in .gitignore)

### Step 4: Verify It Works

Test locally:
```bash
python -c "import os; from prompt_based_generator import PromptBasedGenerator; from rag_system import RAGSystem; rag = RAGSystem(); gen = PromptBasedGenerator(rag); print('✅ API key works!')"
```

Or test via API:
```bash
curl -X POST "http://localhost:8000/api/generate-from-prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "max_tokens": 100}'
```

## 🔒 Prevent Future Leaks

✅ **DO:**
- Store API keys in environment variables
- Use Railway/Heroku environment variables for production
- Keep `.env` files in `.gitignore` (already done!)
- Use separate API keys for development and production

❌ **DON'T:**
- Commit API keys to Git
- Share API keys in screenshots or messages
- Hardcode API keys in source code
- Post API keys in public forums/issues

## 🆘 Still Having Issues?

If you still get 403 errors after creating a new key:
1. **Wait 5-10 minutes** - Google's API key propagation can take time
2. **Check the API key format** - Should start with `AIzaSy`
3. **Verify billing** - Free tier should work, but check https://aistudio.google.com/
4. **Check quota limits** - Visit https://aistudio.google.com/app/apikey

## 📝 Quick Checklist

- [ ] Created new API key at https://aistudio.google.com/apikey
- [ ] Updated `GEMINI_API_KEY` on Railway
- [ ] Updated local environment variable (if developing locally)
- [ ] Tested that it works
- [ ] Deleted/revoked old API key (optional but recommended)

---

**You got this! 🚀** Just create a new key and update it. The old one is permanently disabled.

