# 🔌 Railway Port Configuration

## When Generating Domain - What Port to Enter

### Answer: Leave it blank OR use Railway's default

When Railway asks "what port the app is listening to" during domain generation:

**Option 1 (Recommended): Leave it blank**
- Railway will automatically detect the port from your service configuration
- Your app uses `$PORT` which Railway sets automatically

**Option 2: Use the default port**
- Enter: `5000` (Railway's default)
- Or check what `$PORT` is set to in your Railway Variables

---

## How Your App Handles Ports

### Backend Configuration:
- Your `Procfile` uses: `gunicorn ... --bind 0.0.0.0:$PORT`
- Your `app.py` reads: `port = int(os.getenv("PORT", 5001))`
- Railway automatically sets `$PORT` environment variable
- The app listens on whatever port Railway assigns (usually 3000 or 5000)

### Railway's Behavior:
- Railway assigns a port automatically via `$PORT` env var
- When you generate a domain, Railway routes HTTP/HTTPS (80/443) → your app's `$PORT`
- You don't need to manually configure this

---

## Quick Answer

**Just leave it blank** when Railway asks for the port.

Railway will automatically:
1. Set `$PORT` environment variable
2. Your app listens on `$PORT`
3. Railway routes public domain traffic to that port

---

## Verify Port Configuration

After generating the domain, check:

1. **In Railway Variables:**
   - Go to Settings → Variables
   - Look for `PORT` variable (Railway sets this automatically)
   - Note the value (usually `5000` or `3000`)

2. **In Your App Logs:**
   - Check deployment logs
   - Should show: "Listening on port 5000" or similar

3. **Test the Domain:**
   - Visit: `https://your-domain.up.railway.app/api/health`
   - Should work without specifying a port

---

## Troubleshooting

**If domain doesn't work:**
- Make sure your service is running (check logs)
- Verify `$PORT` is set in environment variables
- Check that your app actually listens on `0.0.0.0:$PORT` (not `127.0.0.1`)

**If Railway insists on a port number:**
- Enter: `5000` (Railway's common default)
- Or check what port is in your Railway Variables
