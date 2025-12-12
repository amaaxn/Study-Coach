# ⚡ Quick Start: Accessing Your MongoDB Database

## 🎯 Easiest Way: MongoDB Compass (GUI)

1. **Install MongoDB Compass:**
   ```bash
   brew install --cask mongodb-compass
   ```
   Or download: https://www.mongodb.com/try/download/compass

2. **Connect:**
   - Open MongoDB Compass
   - Paste this connection string: `mongodb://localhost:27017/`
   - Click "Connect"

3. **Navigate:**
   - Click on `study_coach` database
   - Browse collections: `users`, `courses`, `materials`, `study_tasks`

**That's it!** You can now view, edit, and manage all your data visually.

---

## 💻 Command Line: MongoDB Shell

1. **Install:**
   ```bash
   brew install mongosh
   ```

2. **Connect:**
   ```bash
   mongosh mongodb://localhost:27017/study_coach
   ```

3. **Quick Commands:**
   ```javascript
   // List collections
   show collections
   
   // View all users
   db.users.find().pretty()
   
   // View all courses
   db.courses.find().pretty()
   
   // Count documents
   db.users.countDocuments()
   ```

---

## 🐍 Python Script (Included)

Use the provided utility script:

```bash
cd backend
python3 scripts/mongodb_utils.py stats
python3 scripts/mongodb_utils.py list-users
python3 scripts/mongodb_utils.py list-courses
```

---

## 📍 Default Connection Info

- **Local MongoDB:** `mongodb://localhost:27017/`
- **Database Name:** `study_coach`
- **Collections:** `users`, `courses`, `materials`, `study_tasks`

---

## ⚠️ If MongoDB Isn't Running

```bash
# Start MongoDB (macOS)
brew services start mongodb-community

# Check if running
brew services list
```
