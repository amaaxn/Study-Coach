# 🔧 Fix Backend "Application failed to respond" on Railway

## Common Causes & Fixes

### ✅ 1. Missing Required Environment Variables

Railway backend needs these environment variables to start:

**Go to Railway → Your Backend Service → Variables tab**

**Required Variables:**
```
ENVIRONMENT=production
FLASK_ENV=production
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/learnium_prod
MONGO_DB_NAME=learnium_prod
JWT_SECRET_KEY=your-32-character-secret-key
OPENAI_API_KEY=sk-your-openai-key
FRONTEND_URL=https://learnium.co
PORT=5000
```

**If any are missing, the app will crash on startup!**

---

### ✅ 2. Check Railway Logs

**To see what's wrong:**

1. Go to Railway → Your backend service
2. Click **"Logs"** tab (or **"Deployments"** → Latest → View logs)
3. Look for red error messages
4. Common errors you might see:
   - `ValueError: JWT_SECRET_KEY must be set...`
   - `ValueError: FRONTEND_URL must be set...`
   - `MongoClient: ...` (MongoDB connection errors)
   - `ModuleNotFoundError: ...` (missing dependency)
   - `ImportError: ...` (import error)

---

### ✅ 3. MongoDB Connection Issues

**If you see MongoDB errors:**

1. **Check MongoDB Atlas:**
   - Go to MongoDB Atlas → Network Access
   - Make sure IP `0.0.0.0/0` is allowed (or Railway IPs)
   
2. **Check Connection String:**
   - In Railway Variables, `MONGO_URI` should be:
   - `mongodb+srv://username:password@cluster.mongodb.net/learnium_prod`
   - Replace `<password>` with actual password
   - Make sure username/password are correct

3. **Test Connection:**
   - Try connecting from your local machine with the same connection string
   - If it works locally but not Railway, it's a network/IP issue

---

### ✅ 4. Application Not Starting

**Check if gunicorn is starting:**

In Railway logs, you should see:
```
Starting gunicorn ...
Listening on 0.0.0.0:5000
```

**If you don't see this:**

1. **Check Start Command:**
   - Railway → Settings → Deploy
   - Start Command should be: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
   
2. **Check Procfile exists:**
   - Should be in `backend/Procfile`
   - Content: `web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`

---

### ✅ 5. Port Binding Issues

**The app must bind to `0.0.0.0`, not `127.0.0.1`:**

Check your `backend/app.py`:
```python
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(debug=False, port=port, host="0.0.0.0")  # Must be 0.0.0.0
```

And `backend/Procfile`:
```
web: gunicorn --bind 0.0.0.0:$PORT ...
```

---

## 🔍 Step-by-Step Debugging

### Step 1: Check Railway Logs

1. Railway → Your service → **Logs** tab
2. Scroll to latest deployment
3. Look for errors (red text)
4. **Copy the error message**

### Step 2: Verify Environment Variables

1. Railway → Your service → **Variables** tab
2. Check each required variable exists:
   - ✅ `ENVIRONMENT=production`
   - ✅ `MONGO_URI=mongodb+srv://...`
   - ✅ `MONGO_DB_NAME=learnium_prod`
   - ✅ `JWT_SECRET_KEY=...` (32+ chars)
   - ✅ `OPENAI_API_KEY=sk-...`
   - ✅ `FRONTEND_URL=https://learnium.co`

3. **If missing, add them!**

### Step 3: Check MongoDB

1. Test connection string locally (if you have MongoDB tools)
2. Verify MongoDB Atlas Network Access allows Railway
3. Verify username/password are correct

### Step 4: Verify Startup

1. Check logs for "Listening on..." message
2. If no startup message, app crashed during import
3. Look for Python traceback/error

---

## 🚨 Most Common Issues

### Issue 1: Missing JWT_SECRET_KEY

**Error:** `ValueError: JWT_SECRET_KEY must be set...`

**Fix:**
1. Generate secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Add to Railway Variables as `JWT_SECRET_KEY`

### Issue 2: Missing FRONTEND_URL

**Error:** `ValueError: FRONTEND_URL must be set...`

**Fix:**
1. Add to Railway Variables: `FRONTEND_URL=https://learnium.co`

### Issue 3: MongoDB Connection Failed

**Error:** `MongoClient: ...` or connection timeout

**Fix:**
1. Check MongoDB Atlas Network Access
2. Verify connection string is correct
3. Check username/password

### Issue 4: Module Not Found

**Error:** `ModuleNotFoundError: No module named '...'`

**Fix:**
1. Check `backend/requirements.txt` includes all dependencies
2. Railway should auto-install, but verify in logs

---

## 📋 Quick Fix Checklist

1. [ ] Check Railway Logs for specific error
2. [ ] Verify all environment variables are set
3. [ ] Check MongoDB connection string is correct
4. [ ] Verify MongoDB Atlas Network Access allows Railway
5. [ ] Check Start Command in Railway settings
6. [ ] Verify Procfile exists and is correct
7. [ ] Redeploy backend after fixing variables

---

## 🆘 Still Not Working?

### Get the Exact Error:

1. Railway → Your service → Logs
2. Scroll to most recent error
3. Copy the full error message
4. Look for:
   - Python traceback
   - `ValueError:`
   - `ImportError:`
   - `MongoClient:`
   - Any red error text

### Common Error Patterns:

**"ValueError: ... must be set"**
→ Missing environment variable

**"MongoClient: ..."**
→ MongoDB connection issue

**"ModuleNotFoundError"**
→ Missing dependency in requirements.txt

**"ImportError"**
→ Code import issue

**"Address already in use"**
→ Port conflict (rare on Railway)

---

## ✅ After Fixing

Once you fix the issue:

1. Railway will auto-redeploy (or trigger manual redeploy)
2. Wait 1-2 minutes for deployment
3. Check logs - should see "Listening on..." message
4. Test: `https://your-backend.up.railway.app/api/health`
5. Should return: `{"status":"ok","environment":"production"}`

---

**The most common issue is missing environment variables. Check those first!**
