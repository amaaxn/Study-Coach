# 🔧 Fix All Issues - Complete Checklist

## What I Fixed

### ✅ 1. Routing (404 Errors)
- Moved `vercel.json` to `frontend/` directory (where Vercel looks when Root Directory is set to `frontend`)
- Added proper rewrites to serve `index.html` for all routes
- Fixed URL handling after login/register

### ✅ 2. Blank Page After Login
- Added proper authentication state management
- Fixed token validation logic
- Added error handling for API calls
- Added loading states

### ✅ 3. API Configuration
- Added console logging to debug API calls
- Added 30 second timeout
- Better error messages

---

## ⚠️ CRITICAL: Verify These Settings

### 1. Vercel Environment Variable (MUST CHECK!)

Go to Vercel → Your Project → Settings → Environment Variables

**Check if `VITE_API_URL` is set:**
```
VITE_API_URL=https://your-railway-backend.up.railway.app/api
```

**Replace `your-railway-backend.up.railway.app` with your actual Railway backend URL!**

If it's NOT set or wrong:
1. Add/Update the variable
2. Select **all environments** (Production, Preview, Development)
3. Click **Save**
4. **Redeploy** your frontend

---

### 2. Railway Backend CORS

Go to Railway → Your Backend → Variables

**Check if `FRONTEND_URL` is set:**
```
FRONTEND_URL=https://learnium.co
```

If it's NOT set or wrong:
1. Add/Update the variable
2. Save (this triggers redeploy)

---

### 3. MongoDB Connection

Go to Railway → Your Backend → Variables

**Check if these are set:**
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/learnium_prod
MONGO_DB_NAME=learnium_prod
```

If NOT set:
1. Go to MongoDB Atlas
2. Get connection string
3. Add to Railway variables

---

## 🔍 How to Debug

### Check Browser Console

1. Open your site: `https://learnium.co`
2. Press `F12` (or right-click → Inspect)
3. Go to **Console** tab
4. Look for:
   - `API Base URL: ...` - should show your Railway URL
   - Any red error messages

### Check Network Tab

1. In browser DevTools, go to **Network** tab
2. Try to login
3. Look for requests to `/api/auth/login`
4. Check if:
   - Request goes to correct URL
   - Status is 200 (success) or shows error

---

## 🚀 Step-by-Step Fix

### Step 1: Verify Environment Variables

**In Vercel:**
```bash
VITE_API_URL=https://your-backend.up.railway.app/api
```

**In Railway:**
```bash
FRONTEND_URL=https://learnium.co
MONGO_URI=mongodb+srv://...
MONGO_DB_NAME=learnium_prod
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=your-secret
```

### Step 2: Redeploy Everything

1. **Railway:** Variables update triggers auto-redeploy
2. **Vercel:** 
   - Go to Deployments
   - Click "..." → "Redeploy"

### Step 3: Test

1. Visit `https://learnium.co`
2. Should load (not 404)
3. Try `/register` - should work
4. Try to register/login
5. Check browser console for errors

---

## 🐛 Common Issues & Solutions

### Issue: Still Getting 404

**Solution:**
- Make sure `frontend/vercel.json` exists with rewrites
- Wait 2-3 minutes for Vercel to rebuild
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)

### Issue: Blank Page After Login

**Check:**
1. Browser console for errors
2. `VITE_API_URL` is set correctly in Vercel
3. Railway backend is running (check Railway logs)
4. Backend URL is accessible (test in browser: `https://your-backend.up.railway.app/api/health`)

### Issue: "Cannot connect to server"

**Check:**
1. Railway backend is running
2. Backend URL in `VITE_API_URL` is correct
3. No typos in URL (include `/api` at the end)
4. Test backend directly: `https://your-backend.up.railway.app/api/health`

### Issue: CORS Errors

**Check:**
1. `FRONTEND_URL` in Railway matches your domain exactly
2. No trailing slash: use `https://learnium.co` not `https://learnium.co/`
3. Backend redeployed after updating `FRONTEND_URL`

---

## 📋 Quick Checklist

- [ ] `VITE_API_URL` set in Vercel with Railway backend URL + `/api`
- [ ] `FRONTEND_URL` set in Railway with `https://learnium.co`
- [ ] MongoDB connection string set in Railway
- [ ] All other Railway env vars set (JWT_SECRET_KEY, OPENAI_API_KEY, etc.)
- [ ] Frontend redeployed in Vercel
- [ ] Backend redeployed in Railway (after env var changes)
- [ ] Test backend directly: `https://your-backend.up.railway.app/api/health`
- [ ] Test frontend: `https://learnium.co`
- [ ] Check browser console for errors

---

## ✅ What Should Work Now

After fixing env vars and redeploying:

1. ✅ `https://learnium.co` - loads homepage
2. ✅ `https://learnium.co/register` - loads register page
3. ✅ `https://learnium.co/login` - loads login page
4. ✅ Registration works - creates user in MongoDB
5. ✅ Login works - sets token, redirects to app
6. ✅ Main app loads after login
7. ✅ All API calls work

---

## 🆘 Still Not Working?

1. **Check Railway Logs:**
   - Railway → Your service → Logs
   - Look for errors

2. **Check Vercel Logs:**
   - Vercel → Your project → Deployments → Latest → View logs

3. **Check Browser Console:**
   - F12 → Console tab
   - Look for red errors

4. **Test Backend Directly:**
   - Visit: `https://your-backend.up.railway.app/api/health`
   - Should return: `{"status":"ok","environment":"production"}`

The most common issue is **missing or incorrect `VITE_API_URL`** in Vercel. Double-check that first!
