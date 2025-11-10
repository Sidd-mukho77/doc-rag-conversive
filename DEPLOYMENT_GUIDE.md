# 🚀 Deployment Guide for Convie RAG Chatbot

This guide will help you deploy your Convie chatbot to Render for your interview presentation.

## 📋 Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Render Account** - Sign up at https://render.com (free tier available)
3. **API Keys Ready**:
   - Pinecone API Key
   - Google Gemini API Key

---

## 🎯 Deployment Strategy

You'll deploy **TWO services** on Render:

1. **Backend (FastAPI)** - Python web service
2. **Frontend (React + Vite)** - Static site

---

## 📦 Step 1: Prepare Your Repository

### 1.1 Create a GitHub Repository

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Convie RAG Chatbot"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/convie-chatbot.git
git branch -M main
git push -u origin main
```

### 1.2 Important Files to Check

**✅ Files to Include:**
- `backend/api.py`
- `backend/config.py`
- `backend/requirements.txt`
- `frontend/` (entire folder)
- `.gitignore`

**❌ Files to EXCLUDE (add to .gitignore):**
- `.env` (contains secrets!)
- `scraped_data/` (not needed for deployment)
- `__pycache__/`
- `node_modules/`
- `*.pyc`
- `.vscode/`
- `.kiro/`

### 1.3 Update .gitignore

Make sure your `.gitignore` includes:

```
# Environment variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Node
node_modules/
dist/
.vite/

# Data
scraped_data/

# IDE
.vscode/
.kiro/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## 🔧 Step 2: Deploy Backend (FastAPI)

### 2.1 Go to Render Dashboard

1. Visit https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**

### 2.2 Connect Your Repository

1. Connect your GitHub account
2. Select your `convie-chatbot` repository
3. Click **"Connect"**

### 2.3 Configure Backend Service

**Basic Settings:**
- **Name:** `convie-backend` (or any name you prefer)
- **Region:** Choose closest to you
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **"Free"** (sufficient for demo)

### 2.4 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value |
|-----|-------|
| `PINECONE_API_KEY` | Your Pinecone API key |
| `GEMINI_API_KEY` | Your Gemini API key |
| `PYTHON_VERSION` | `3.11.0` |

### 2.5 Deploy Backend

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Once deployed, you'll get a URL like: `https://convie-backend-xxxx.onrender.com`
4. **SAVE THIS URL** - you'll need it for the frontend!

### 2.6 Test Backend

Visit: `https://your-backend-url.onrender.com/api/health`

You should see: `{"status":"ok"}`

---

## 🎨 Step 3: Deploy Frontend (React)

### 3.1 Update Frontend API URL

**Option A: Environment Variable (Recommended)**

1. Create/update `frontend/.env.production`:

```env
VITE_API_URL=https://your-backend-url.onrender.com
```

2. Update `frontend/src/components/ChatInterface.tsx`:

Replace all instances of `http://localhost:8000` with:

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Then use it like:
const response = await fetch(`${API_URL}/api/chat`, {
  // ...
});
```

**Option B: Direct Replacement (Quick)**

Simply find and replace in `ChatInterface.tsx`:
- Find: `http://localhost:8000`
- Replace: `https://your-actual-backend-url.onrender.com`

### 3.2 Create Frontend Service on Render

1. Go back to Render Dashboard
2. Click **"New +"** → **"Static Site"**

### 3.3 Configure Frontend Service

**Basic Settings:**
- **Name:** `convie-frontend`
- **Region:** Same as backend
- **Branch:** `main`
- **Root Directory:** `frontend`

**Build & Deploy:**
- **Build Command:** `npm install && npm run build`
- **Publish Directory:** `dist`

**Environment Variables:**
Add this if using Option A above:
- `VITE_API_URL` = `https://your-backend-url.onrender.com`

### 3.4 Deploy Frontend

1. Click **"Create Static Site"**
2. Wait 5-10 minutes for deployment
3. You'll get a URL like: `https://convie-frontend-xxxx.onrender.com`

---

## 🔐 Step 4: Update CORS Settings

After deploying frontend, update your backend CORS settings:

1. Go to your backend code (`backend/api.py`)
2. Update the CORS origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "https://convie-frontend-xxxx.onrender.com",  # Add your frontend URL
        "https://your-custom-domain.com"  # If you have one
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Commit and push:

```bash
git add backend/api.py
git commit -m "Update CORS for production"
git push
```

4. Render will automatically redeploy your backend

---

## ✅ Step 5: Test Your Deployment

### 5.1 Test Backend

Visit: `https://your-backend-url.onrender.com/docs`

You should see the FastAPI Swagger documentation.

### 5.2 Test Frontend

1. Visit: `https://your-frontend-url.onrender.com`
2. You should see the Convie interface with:
   - Logo in top-left
   - Animated "What can I help you with?" text
   - Purple gradient input box
   - Suggested questions

### 5.3 Test Full Flow

1. Ask a question: "How do I create a campaign?"
2. Check that you get a response
3. Try the "Dive Deeper" button
4. Test conversation history in the menu

---

## 🎤 For Your Interview

### Demo Script

1. **Introduction (30 seconds)**
   - "I built Convie, an AI-powered chatbot for SMS Magic documentation"
   - "It uses RAG (Retrieval-Augmented Generation) with Pinecone and Gemini"

2. **Show the UI (1 minute)**
   - Point out the clean, modern interface
   - Mention the animated text and smooth transitions
   - Show the conversation menu

3. **Demonstrate Features (2 minutes)**
   - Ask a question and show the response
   - Click "Dive Deeper" to show web search
   - Show related queries and suggestions
   - Open conversation history

4. **Technical Highlights (1 minute)**
   - "Backend: FastAPI with Pinecone vector database"
   - "Frontend: React + TypeScript with Framer Motion"
   - "AI: Google Gemini with search grounding"
   - "Deployed on Render with CI/CD from GitHub"

### Talking Points

**Architecture:**
- Vector database for semantic search
- Gemini embeddings for document retrieval
- Google Search grounding for web fallback
- Conversation memory for context

**Features:**
- Clean, professional UI with animations
- Smart "Dive Deeper" that searches web when needed
- Organized suggestions (related + general)
- Conversation history management
- Source attribution

**Tech Stack:**
- Backend: FastAPI, Pinecone, Google Gemini
- Frontend: React, TypeScript, Tailwind CSS, Framer Motion
- Deployment: Render (auto-deploy from GitHub)

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Backend won't start
- Check logs in Render dashboard
- Verify environment variables are set
- Check Python version (should be 3.11)

**Problem:** API calls fail
- Check CORS settings
- Verify Pinecone index exists
- Check API keys are valid

### Frontend Issues

**Problem:** White screen
- Check browser console for errors
- Verify API URL is correct
- Check network tab for failed requests

**Problem:** API calls fail
- Verify backend URL in frontend code
- Check CORS settings in backend
- Ensure backend is running

### Performance Issues

**Problem:** Slow responses
- Render free tier has cold starts (first request takes ~30s)
- Keep backend warm by pinging `/api/health` every 10 minutes
- Consider upgrading to paid tier for production

---

## 💡 Pro Tips

1. **Keep Backend Warm:**
   - Use a service like UptimeRobot to ping your backend every 10 minutes
   - This prevents cold starts during your demo

2. **Custom Domain:**
   - Render allows custom domains on free tier
   - Makes it look more professional: `convie.yourdomain.com`

3. **Environment Variables:**
   - Never commit `.env` files
   - Use Render's environment variable management
   - Keep a backup of your keys securely

4. **Monitoring:**
   - Check Render logs before your interview
   - Test all features 30 minutes before
   - Have a backup plan (local demo) just in case

5. **GitHub README:**
   - Add screenshots of your UI
   - Include architecture diagram
   - Document the tech stack clearly

---

## 📊 Cost Breakdown

**Free Tier (Sufficient for Demo):**
- Backend: Free (750 hours/month)
- Frontend: Free (100 GB bandwidth/month)
- Pinecone: Free tier (1 index, 100K vectors)
- Gemini: Free tier (60 requests/minute)

**Total Cost: $0** ✅

---

## 🎓 Interview Questions You Might Get

**Q: Why did you choose this tech stack?**
A: FastAPI for fast Python API development, Pinecone for scalable vector search, Gemini for state-of-the-art embeddings and generation, React for modern UI with great developer experience.

**Q: How does the RAG system work?**
A: User query → Gemini embeddings → Pinecone similarity search → Context retrieval → Gemini generation with context → Response with sources.

**Q: What about scaling?**
A: Pinecone handles vector search at scale, FastAPI is async for concurrent requests, React frontend is static and CDN-ready, can add Redis for caching.

**Q: How do you handle errors?**
A: Try-catch blocks, fallback to web search, user-friendly error messages, logging for debugging.

**Q: What would you improve?**
A: Add user authentication, implement caching, add analytics, improve conversation persistence, add more data sources.

---

## 🚀 Ready to Deploy!

Follow the steps above, and you'll have a production-ready demo for your interview. Good luck! 🎉

**Need Help?**
- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Pinecone Docs: https://docs.pinecone.io
