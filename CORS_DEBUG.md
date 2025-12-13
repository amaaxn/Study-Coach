# CORS Debugging Guide

## Current Issue
CORS error: `No 'Access-Control-Allow-Origin' header is present on the requested resource`

## Quick Checks

### 1. Check Railway Environment Variable
In Railway → Your Backend Service → Variables, ensure:
- `FRONTEND_URL` = `https://www.learnium.co` (or `https://learnium.co`)
- Make sure it's exactly as shown above (with `https://`)

### 2. Check Railway Logs
After Railway redeploys, check the startup logs. You should see:
```
✅ CORS configured for: ['https://www.learnium.co', 'https://learnium.co', ...]
```

If you see:
```
⚠️ WARNING: FRONTEND_URL not set in production. Using permissive CORS.
```
Then `FRONTEND_URL` is not set correctly in Railway.

### 3. Test Backend Health Endpoint
Try accessing in your browser:
```
https://learnium-production.up.railway.app/api/health
```

Should return JSON like:
```json
{"status":"ok","database":"connected",...}
```

### 4. Test OPTIONS Request
Open browser console on your frontend and run:
```javascript
fetch('https://learnium-production.up.railway.app/api/auth/login', {
  method: 'OPTIONS',
  headers: {
    'Origin': 'https://www.learnium.co',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'Content-Type'
  }
}).then(r => {
  console.log('OPTIONS Response:', r.status);
  console.log('CORS Headers:', {
    'Access-Control-Allow-Origin': r.headers.get('Access-Control-Allow-Origin'),
    'Access-Control-Allow-Methods': r.headers.get('Access-Control-Allow-Methods'),
    'Access-Control-Allow-Headers': r.headers.get('Access-Control-Allow-Headers')
  });
}).catch(e => console.error('OPTIONS Error:', e));
```

### 5. Check Railway Logs for OPTIONS Debugging
After the latest code change, Railway logs will show:
```
🔍 OPTIONS request from origin: https://www.learnium.co
✅ CORS header set: https://www.learnium.co
```

If you see `❌ CORS header NOT set`, there's a configuration issue.

## Common Fixes

### Fix 1: Set FRONTEND_URL in Railway
1. Railway → Backend Service → Variables
2. Add/Edit: `FRONTEND_URL` = `https://www.learnium.co`
3. Wait for redeploy (2-3 minutes)

### Fix 2: Verify Railway Redeployed
Check Railway logs timestamp - should be recent (last few minutes).

### Fix 3: Clear Browser Cache
Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

## Still Not Working?

1. Share Railway startup logs (the section showing "CORS configured for:")
2. Share the output of the OPTIONS test above
3. Verify Railway has redeployed with latest code
