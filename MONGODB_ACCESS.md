# 🔧 MongoDB Database Access Guide

This guide shows you how to access and manage your Study Coach MongoDB database.

---

## 🎯 Quick Access Methods

### 1. **MongoDB Compass** (Recommended - GUI Tool)
The easiest way to view and manage your database with a visual interface.

#### Installation:
```bash
# macOS
brew install --cask mongodb-compass

# Or download from: https://www.mongodb.com/try/download/compass
```

#### Connection:
1. Open MongoDB Compass
2. Use connection string:
   ```
   mongodb://localhost:27017/
   ```
   Or for production/Atlas:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/
   ```
3. Click "Connect"
4. Navigate to `study_coach` database
5. Browse collections: `users`, `courses`, `materials`, `study_tasks`

---

### 2. **MongoDB Shell (mongosh)** (Command Line)
Powerful command-line interface for database operations.

#### Installation:
```bash
# macOS
brew install mongosh

# Or download from: https://www.mongodb.com/try/download/shell
```

#### Usage:
```bash
# Connect to local MongoDB
mongosh

# Or connect to specific database
mongosh mongodb://localhost:27017/study_coach

# List all databases
show dbs

# Switch to study_coach database
use study_coach

# List collections
show collections

# View all users
db.users.find().pretty()

# View all courses
db.courses.find().pretty()

# View all materials
db.materials.find().pretty()

# View all study tasks
db.study_tasks.find().pretty()

# Count documents
db.users.countDocuments()
db.courses.countDocuments()

# Find specific user by email
db.users.findOne({ email: "user@example.com" })

# Find courses for a specific user
db.courses.find({ user_id: ObjectId("...") }).pretty()

# Delete a user (be careful!)
db.users.deleteOne({ email: "user@example.com" })

# Exit
exit
```

---

### 3. **MongoDB Atlas** (Cloud - If Using)
If you're using MongoDB Atlas (cloud), you can:

1. **Web Interface:**
   - Go to https://cloud.mongodb.com
   - Log in to your account
   - Navigate to your cluster
   - Click "Browse Collections" to view data

2. **Connection String:**
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/study_coach
   ```
   Replace with your actual credentials from Atlas dashboard.

---

## 📊 Common Management Tasks

### View All Data
```javascript
// In mongosh or Compass query bar:

// All users
db.users.find().pretty()

// All courses with user names
db.courses.aggregate([
  {
    $lookup: {
      from: "users",
      localField: "user_id",
      foreignField: "_id",
      as: "user"
    }
  }
]).pretty()

// All materials with course names
db.materials.aggregate([
  {
    $lookup: {
      from: "courses",
      localField: "course_id",
      foreignField: "_id",
      as: "course"
    }
  }
]).pretty()

// All study tasks
db.study_tasks.find().pretty()
```

### Search Operations
```javascript
// Find user by email
db.users.findOne({ email: "user@example.com" })

// Find courses by user
const user = db.users.findOne({ email: "user@example.com" })
db.courses.find({ user_id: user._id }).pretty()

// Find materials by course
const course = db.courses.findOne({ name: "CSE 316" })
db.materials.find({ course_id: course._id }).pretty()
```

### Backup Database
```bash
# Export all collections
mongodump --uri="mongodb://localhost:27017/" --db=study_coach --out=/path/to/backup

# Or specific collection
mongodump --uri="mongodb://localhost:27017/" --db=study_coach --collection=users --out=/path/to/backup
```

### Restore Database
```bash
# Restore from backup
mongorestore --uri="mongodb://localhost:27017/" /path/to/backup/study_coach
```

### Clear Data (Be Careful!)
```javascript
// Delete all data in a collection
db.users.deleteMany({})
db.courses.deleteMany({})
db.materials.deleteMany({})
db.study_tasks.deleteMany({})

// Delete specific user and all their data
const user = db.users.findOne({ email: "user@example.com" })
db.courses.deleteMany({ user_id: user._id })
db.users.deleteOne({ _id: user._id })
```

---

## 🔍 Useful Queries

### Get User Statistics
```javascript
// Count users
db.users.countDocuments()

// Count courses per user
db.courses.aggregate([
  {
    $group: {
      _id: "$user_id",
      courseCount: { $sum: 1 }
    }
  },
  {
    $lookup: {
      from: "users",
      localField: "_id",
      foreignField: "_id",
      as: "user"
    }
  }
]).pretty()
```

### Get Course with Materials
```javascript
db.courses.aggregate([
  {
    $match: { name: "CSE 316" }
  },
  {
    $lookup: {
      from: "materials",
      localField: "_id",
      foreignField: "course_id",
      as: "materials"
    }
  },
  {
    $lookup: {
      from: "study_tasks",
      localField: "_id",
      foreignField: "course_id",
      as: "study_tasks"
    }
  }
]).pretty()
```

---

## 🔐 Security Notes

1. **Production:**
   - Always use authentication in production
   - Use connection strings with credentials
   - Enable SSL/TLS for remote connections

2. **Local Development:**
   - Default connection: `mongodb://localhost:27017/`
   - No authentication required by default

3. **Backup Regularly:**
   - Use `mongodump` for backups
   - Store backups securely

---

## 🛠️ Troubleshooting

### MongoDB Not Running
```bash
# macOS (Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Check status
brew services list  # macOS
sudo systemctl status mongod  # Linux
```

### Connection Issues
- Check if MongoDB is running: `ps aux | grep mongod`
- Check port: Default is `27017`
- Check firewall settings
- Verify connection string format

### Reset Database
```bash
# Stop app, then:
mongosh
use study_coach
db.dropDatabase()
```

---

## 📚 Additional Resources

- **MongoDB Compass Docs:** https://www.mongodb.com/docs/compass/
- **MongoDB Shell Docs:** https://www.mongodb.com/docs/mongodb-shell/
- **MongoDB Atlas:** https://cloud.mongodb.com

---

## 🚀 Quick Start Commands

```bash
# 1. Start MongoDB (if local)
brew services start mongodb-community

# 2. Connect with Compass (GUI)
# Open MongoDB Compass and connect to: mongodb://localhost:27017/

# 3. Or connect with shell
mongosh mongodb://localhost:27017/study_coach

# 4. In shell, view collections
show collections

# 5. View data
db.users.find().pretty()
db.courses.find().pretty()
```
