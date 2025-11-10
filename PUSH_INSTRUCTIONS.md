# 🚀 Quick Push Instructions

## Option 1: Use the Script (Easiest)

Double-click `push_to_github.bat` and follow the prompts.

The script will:
1. ✅ Initialize git if needed
2. ✅ Check for sensitive files
3. ✅ Remove .env if accidentally tracked
4. ✅ Show you what will be committed
5. ✅ Ask for confirmation
6. ✅ Commit your changes

Then follow the on-screen instructions to push to GitHub.

---

## Option 2: Manual Commands

### Step 1: Initialize Git

```bash
git init
```

### Step 2: Verify .env is Excluded

```bash
# This should show nothing
git status | findstr ".env"
```

If `.env` appears:
```bash
git rm --cached .env
```

### Step 3: Add and Commit

```bash
git add .
git commit -m "Initial commit: Convie RAG Chatbot"
```

### Step 4: Create GitHub Repository

1. Go to https://github.com/new
2. Name: `convie-chatbot`
3. Click "Create repository"

### Step 5: Push to GitHub

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/convie-chatbot.git
git branch -M main
git push -u origin main
```

---

## ⚠️ IMPORTANT: Security Check

After pushing, visit your GitHub repository and verify:

- ✅ `.env` file is NOT visible
- ✅ `backend/.env.example` IS visible (this is safe)
- ✅ All your code is there

If you see `.env` on GitHub:
1. **Immediately** regenerate your API keys:
   - Pinecone: https://app.pinecone.io
   - Gemini: https://aistudio.google.com/app/apikey
2. Remove `.env` from git:
   ```bash
   git rm --cached .env
   git commit -m "Remove .env"
   git push
   ```

---

## 🎯 What Gets Pushed?

### ✅ Safe to Push:
- All code files
- Documentation
- Configuration templates (.env.example)
- .gitignore

### ❌ Won't Be Pushed (Protected):
- .env (your API keys)
- scraped_data/ (large files)
- node_modules/ (dependencies)
- __pycache__/ (cache)

---

## 📞 Need Help?

Read the complete guide: `GITHUB_PUSH_GUIDE.md`

---

**Ready? Run `push_to_github.bat` or follow the manual commands above!**
