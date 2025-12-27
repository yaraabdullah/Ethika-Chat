# Gemini API Quota Information

## Current Issue

You're using the Gemini API free tier which has limited quotas. The `gemini-2.0-flash-exp` model has very restrictive free tier limits.

## Solution Applied

I've switched the default model to `gemini-1.5-flash` which has better free tier support:
- More requests per minute
- More tokens per day
- More reliable for free tier usage

## Free Tier Limits (Approximate)

- **Requests per minute**: ~15 requests
- **Requests per day**: ~1,500 requests
- **Tokens per day**: Limited (varies by model)

## If You Still Hit Quota Limits

1. **Wait**: The error message tells you how long to wait (usually 30-60 seconds)
2. **Check Usage**: Visit https://ai.dev/usage?tab=rate-limit
3. **Upgrade**: Consider upgrading to a paid plan for higher limits
4. **Reduce Usage**: 
   - Reduce `num_resources` parameter (fewer resources = smaller prompts)
   - Reduce `max_tokens` parameter
   - Wait between requests

## Model Recommendations

- ✅ **gemini-1.5-flash**: Best for free tier (fast, good quotas)
- ⚠️ **gemini-2.0-flash-exp**: Very limited free tier quotas
- 💰 **gemini-1.5-pro**: Better quality but uses more tokens (paid tier recommended)

## Current Configuration

The system now uses `gemini-1.5-flash` by default and includes:
- Automatic retry with exponential backoff for quota errors
- Better error messages
- Graceful handling of quota limits

