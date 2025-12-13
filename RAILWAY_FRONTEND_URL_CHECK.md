# CRITICAL: Set FRONTEND_URL in Railway

## The Problem
You're getting CORS errors because the backend doesn't know which frontend origin to allow.

## The Fix

### Step 1: Go to Railway Dashboard
1. Open Railway → Your Backend Service
2. Click on **"Variables"** tab

### Step 2: Add/Edit FRONTEND_URL
1. Look for `FRONTEND_URL` in the environment variables list
2. If it exists, click **Edit**
3. If it doesn't exist, click **"New Variable"**

### Step 3: Set the Value
- **Key:** `FRONTEND_URL`
- **Value:** `https://www.learnium.co`
- Make sure it's EXACTLY: `https://www.learnium.co` (with `https://` and no trailing slash)

### Step 4: Save and Wait
1. Click **Save**
2. Railway will automatically redeploy (takes 2-3 minutes)
3. Check the logs - you should see:
   ```
   🔧 FRONTEND_URL: https://www.learnium.co
   ✅ CORS configured for: ['https://www.learnium.co', 'https://learnium.co', ...]
   ```

## If FRONTEND_URL is Already Set

If `FRONTEND_URL` is already set but you're still getting CORS errors:

1. **Check the value** - make sure it's `https://www.learnium.co` (not `http://` or missing `www`)
2. **Check Railway logs** - after redeploy, look for the CORS configuration message
3. **Verify it deployed** - check the timestamp in Railway logs is recent

## Alternative: Temporary Fix (Less Secure)

If you want to test quickly without setting FRONTEND_URL:
- The code will use permissive CORS (allows all origins) if FRONTEND_URL is not set
- **This is less secure** but will work for testing
- You should still set FRONTEND_URL properly for production

## After Setting FRONTEND_URL

1. Wait for Railway to redeploy (2-3 minutes)
2. Check Railway logs for "✅ CORS configured for:"
3. Test your frontend - CORS errors should be gone
