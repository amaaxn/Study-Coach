# Vercel Environment Variables Setup

## Required Environment Variable

You **MUST** set `VITE_API_URL` in Vercel to point to your Railway backend.

### Steps:

1. Go to your Vercel project dashboard
2. Click **Settings** → **Environment Variables**
3. Add a new variable:
   - **Key:** `VITE_API_URL`
   - **Value:** Your Railway backend URL + `/api`
   - **Example:** `https://learnium-production.up.railway.app/api`
   - **Environment:** Select all (Production, Preview, Development)

4. **Important:** The URL **MUST include `/api`** at the end!

### Correct Examples:
- ✅ `https://learnium-production.up.railway.app/api`
- ✅ `https://your-backend.up.railway.app/api`

### Incorrect Examples:
- ❌ `https://learnium-production.up.railway.app` (missing `/api`)
- ❌ `https://learnium-production.up.railway.app/` (has trailing slash, might work but not recommended)

### After Setting:

1. **Redeploy** your Vercel frontend (or push a new commit)
2. Check browser console - should see: `🌐 API Base URL: https://your-backend.up.railway.app/api`

### Troubleshooting:

If you see a **405 error**, check:
1. Is `VITE_API_URL` set in Vercel?
2. Does it include `/api` at the end?
3. Did you redeploy after setting it?
4. Check browser console for the actual API Base URL being used
