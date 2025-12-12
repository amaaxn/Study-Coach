# ✅ Fix Vercel Error: "No flask entrypoint found"

## The Problem

Vercel is trying to deploy your **backend** (Flask app), but:
- ❌ **Backend should be on Railway** (not Vercel)
- ✅ **Frontend should be on Vercel**

## The Solution: Configure Vercel for Frontend Only

### Step 1: Set Root Directory in Vercel

1. **Go to Vercel Dashboard:**
   - Open your project
   - Go to **Settings** tab

2. **Set Root Directory:**
   - Scroll to **"Root Directory"** section
   - Click **"Edit"**
   - Enter: `frontend`
   - Click **"Save"**

3. **Verify Build Settings:**
   - Framework Preset: **Vite** (should auto-detect)
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

### Step 2: Add Environment Variable

1. **Go to Settings → Environment Variables**
2. **Add:**
   - **Key:** `VITE_API_URL`
   - **Value:** `https://your-railway-url.up.railway.app/api` (your Railway backend URL)
   - **Select all environments** (Production, Preview, Development)
3. **Click "Save"**

### Step 3: Redeploy

1. Go to **Deployments** tab
2. Click **"..."** on latest deployment
3. Select **"Redeploy"**
   - Or make a small change and push to GitHub to trigger new deployment

---

## What Changed

- ✅ Vercel now only builds the `frontend/` folder
- ✅ No more Flask/backend errors
- ✅ Frontend connects to Railway backend via `VITE_API_URL`

---

## Verification

After redeploy, check:
1. Build logs should show Vite build (not Flask)
2. Deployment should succeed
3. Visit your Vercel URL - frontend should load
4. Test login - should connect to Railway backend

---

## Quick Fix Checklist

- [ ] Root Directory set to `frontend`
- [ ] Framework Preset is `Vite`
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`
- [ ] Environment variable `VITE_API_URL` is set to Railway backend URL
- [ ] Redeploy the project

---

## Alternative: Use vercel.json

If Root Directory setting doesn't work, create `vercel.json` in project root:

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install",
  "framework": "vite"
}
```

But **Root Directory method is simpler and recommended**.

---

## Summary

**The issue:** Vercel was deploying the entire repo (including backend)
**The fix:** Tell Vercel to only deploy the `frontend/` folder
