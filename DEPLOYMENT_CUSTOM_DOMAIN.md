# 🌐 Production Deployment with Custom Domain

This guide covers deploying Learnium with a **custom domain** (not .vercel.app).

## 🎯 Recommended Stack: Railway + Vercel + Custom Domain

### Why This Stack?
- ✅ Free tiers available
- ✅ Easy custom domain setup
- ✅ Automatic SSL/HTTPS
- ✅ Simple environment variable management
- ✅ Excellent performance

---

## 📋 Prerequisites

1. **Domain Name** (from Namecheap, GoDaddy, Google Domains, etc.)
2. **GitHub Account** (your code is already there)
3. **Railway Account** (for backend)
4. **Vercel Account** (for frontend)
5. **MongoDB Atlas Account** (free tier available)

---

## 🚀 Step 1: Deploy Backend to Railway

### 1.1 Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your Learnium repository

### 1.2 Configure Backend
1. **Set Root Directory:**
   - Click on your service
   - Go to "Settings" → "Root Directory"
   - Set to: `backend`

2. **Add Environment Variables:**
   Go to "Variables" tab and add:
   ```
   ENVIRONMENT=production
   FLASK_ENV=production
   OPENAI_API_KEY=sk-your-openai-key-here
   JWT_SECRET_KEY=<generate-strong-secret>
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/learnium_prod
   MONGO_DB_NAME=learnium_prod
   FRONTEND_URL=https://learnium.yourdomain.com
   PORT=5000
   ```

   **Generate JWT Secret:**
   
   Run this command to generate a secure random secret (copy the output):
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   Or use this online tool: https://www.grc.com/passwords.htm (use 64 character random password)
   
   **Important:** Store this secret securely! You'll need it for Railway environment variables.

3. **Set Start Command:**
   - Go to "Settings" → "Deploy"
   - Custom start command: `gunicorn -w 4 --bind 0.0.0.0:$PORT --timeout 120 app:app`

4. **Get Backend URL:**
   - Railway will provide: `https://your-app.up.railway.app`
   - **Note this URL** - you'll use it for the frontend

---

## 🌍 Step 2: Deploy Frontend to Vercel with Custom Domain

### 2.1 Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub
3. Click "Add New" → "Project"
4. Import your GitHub repository

### 2.2 Configure Frontend Build
1. **Root Directory (CRITICAL):**
   - Go to "Settings" → "General" → "Root Directory"
   - Click "Edit"
   - Set to: `frontend`
   - **This tells Vercel to only deploy the frontend, not the backend!**
   - Click "Save"

2. **Build Settings (should auto-detect after setting root):**
   - Framework Preset: **Vite** (should auto-detect)
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
   
   **Note:** If you see "No flask entrypoint found" error, it means Root Directory is not set correctly. Make sure it's set to `frontend`.

3. **Environment Variables:**
   Add in Vercel dashboard:
   ```
   VITE_API_URL=https://your-app.up.railway.app/api
   ```

4. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete
   - You'll get: `https://your-app.vercel.app` (temporary)

### 2.3 Add Custom Domain
1. **In Vercel Dashboard:**
   - Go to your project
   - Click "Settings" → "Domains"
   - Enter your domain: `learnium.yourdomain.com` (or `yourdomain.com`)
   - Click "Add"

2. **Configure DNS:**
   
   **If using subdomain (learnium.yourdomain.com):**
   - Go to your domain registrar (Namecheap, GoDaddy, etc.)
   - Add DNS record:
     - Type: `CNAME`
     - Name: `learnium` (or `@` for root)
     - Value: `cname.vercel-dns.com`
     - TTL: Auto or 3600

   **If using root domain (yourdomain.com):**
   - Add DNS record:
     - Type: `A`
     - Name: `@`
     - Value: `76.76.21.21`
     - TTL: Auto
   
   **Also add for www (optional):**
   - Type: `CNAME`
   - Name: `www`
   - Value: `cname.vercel-dns.com`

3. **Wait for DNS Propagation:**
   - Usually takes 5-60 minutes
   - Vercel will show "Valid Configuration" when ready
   - SSL certificate is automatically provisioned

4. **Update Railway Environment:**
   - Go back to Railway
   - Update `FRONTEND_URL` to: `https://learnium.yourdomain.com` (or your actual domain)
   - Redeploy backend if needed

---

## 🗄️ Step 3: Setup MongoDB Atlas

### 3.1 Create Atlas Cluster
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for free account
3. Create free cluster (M0 tier)
4. Choose region closest to Railway's servers

### 3.2 Configure Database Access
1. Go to "Security" → "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Username: `learnium_admin` (or your choice)
5. Password: Generate secure password (save it!)
6. Database User Privileges: "Atlas admin" (or "Read and write to any database")

### 3.3 Configure Network Access
1. Go to "Security" → "Network Access"
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (or add Railway's IP ranges)
   - This allows Railway to connect
   - For production, you can restrict to Railway IPs later

### 3.4 Get Connection String
1. Go to "Clusters" → Click "Connect"
2. Choose "Connect your application"
3. Driver: Python, Version: 3.6 or later
4. Copy connection string
5. Replace `<password>` with your database user password
6. Replace `<dbname>` with `learnium_prod` (or your choice)
7. Format: `mongodb+srv://learnium_admin:yourpassword@cluster0.xxxxx.mongodb.net/learnium_prod?retryWrites=true&w=majority`

### 3.5 Add to Railway
- Add as `MONGO_URI` environment variable in Railway

---

## 🔧 Step 4: Update Configuration

### 4.1 Update Frontend API URL
In Vercel, make sure `VITE_API_URL` points to your Railway backend:
```
VITE_API_URL=https://your-app.up.railway.app/api
```

### 4.2 Verify Backend CORS
Railway should have:
```
FRONTEND_URL=https://learnium.yourdomain.com
```

The backend will automatically configure CORS to allow only your domain.

---

## ✅ Step 5: Verify Deployment

### 5.1 Test Your Domain
1. Visit: `https://learnium.yourdomain.com`
2. Try signing up a new account
3. Test login
4. Test creating a course
5. Test AI Study Buddy

### 5.2 Check HTTPS
- Verify SSL certificate is active (padlock icon)
- Should show "Secure" in browser

### 5.3 Monitor Logs
- **Railway:** Dashboard → Your Service → "Deployments" → View logs
- **Vercel:** Dashboard → Your Project → "Deployments" → View logs

---

## 🔒 Security Checklist

- [x] Strong JWT_SECRET_KEY (32+ characters)
- [x] MongoDB Atlas with password
- [x] CORS restricted to your domain
- [x] HTTPS enabled (automatic)
- [x] Security headers enabled (automatic in production)
- [x] Environment variables set (not in code)
- [x] Error messages don't expose internals

---

## 📊 Monitoring & Maintenance

### Railway Monitoring
- View logs in Railway dashboard
- Set up alerts for errors
- Monitor resource usage

### Vercel Monitoring
- View analytics in Vercel dashboard
- Monitor build times
- Check deployment status

### MongoDB Atlas
- Monitor database usage
- Set up alerts for high usage
- Regular backups (paid plans) or manual exports

---

## 💰 Cost Estimate

**Free Tier:**
- Railway: $5/month free credit (usually enough for small-medium apps)
- Vercel: Free (up to 100GB bandwidth/month)
- MongoDB Atlas: Free (512MB storage, shared cluster)
- Domain: ~$10-15/year (one-time cost per year)

**Monthly Cost (Small App):**
- ~$0-5/month (if staying within free tiers)
- OpenAI API: Pay per use (~$0.001 per request)

**Monthly Cost (Medium App):**
- Railway: $5-20/month
- Vercel: Free or $20/month (Pro)
- MongoDB Atlas: Free or $9/month
- OpenAI: Variable based on usage

---

## 🐛 Troubleshooting

### Domain Not Working
1. Check DNS records are correct
2. Wait for DNS propagation (can take up to 48 hours)
3. Verify in Vercel dashboard that domain shows "Valid Configuration"
4. Try: `dig yourdomain.com` or `nslookup yourdomain.com`

### CORS Errors
1. Verify `FRONTEND_URL` in Railway matches your exact domain
2. Check no trailing slashes or protocol mismatches
3. Clear browser cache
4. Check browser console for exact error

### Backend Connection Issues
1. Verify `VITE_API_URL` in Vercel is correct
2. Check Railway logs for errors
3. Verify MongoDB connection string is correct
4. Check MongoDB network access allows Railway IPs

### Build Failures
1. Check build logs in Vercel
2. Verify all dependencies in `package.json`
3. Check Node.js version compatibility
4. Clear Vercel build cache and rebuild

---

## 🚀 Alternative: Single Platform Deployment

If you prefer one platform:

### Option 1: Render (Full-Stack)
- Deploy both frontend and backend
- Supports custom domains
- Free tier available
- URL: https://render.com

### Option 2: Fly.io
- Great for full-stack apps
- Custom domains
- Free tier available
- URL: https://fly.io

### Option 3: DigitalOcean App Platform
- Simple deployment
- Custom domains
- $5/month minimum
- URL: https://www.digitalocean.com/products/app-platform

---

## 📝 Final Notes

1. **Keep secrets secure:** Never commit `.env` files
2. **Monitor costs:** Set up billing alerts
3. **Regular backups:** Export MongoDB data periodically
4. **Update dependencies:** Keep packages up to date
5. **Monitor logs:** Check for errors regularly

Your app is now production-ready with a custom domain! 🎉
