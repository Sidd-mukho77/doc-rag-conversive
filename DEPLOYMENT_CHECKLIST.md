# ✅ Pre-Deployment Checklist

Use this checklist before your interview to ensure everything is ready!

## 📋 Before You Start

- [ ] GitHub account created
- [ ] Render account created (https://render.com)
- [ ] Pinecone API key ready
- [ ] Gemini API key ready
- [ ] Code tested locally and working

## 🔧 Code Preparation

### Backend
- [ ] `backend/requirements.txt` exists
- [ ] `backend/api.py` has correct CORS settings
- [ ] `backend/config.py` uses environment variables
- [ ] No hardcoded API keys in code
- [ ] `.env` file is in `.gitignore`

### Frontend
- [ ] API URL uses environment variable (`API_URL`)
- [ ] All `localhost:8000` replaced with `${API_URL}`
- [ ] `frontend/.env.production` created
- [ ] Build command works: `npm run build`
- [ ] No console errors in production build

## 📦 Git Repository

- [ ] Repository created on GitHub
- [ ] `.gitignore` properly configured
- [ ] All code committed
- [ ] Pushed to `main` branch
- [ ] No `.env` files in repository
- [ ] No `scraped_data/` in repository

## 🚀 Render Deployment

### Backend Service
- [ ] Web Service created on Render
- [ ] Connected to GitHub repository
- [ ] Root directory set to `backend`
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- [ ] Environment variables added:
  - [ ] `PINECONE_API_KEY`
  - [ ] `GEMINI_API_KEY`
  - [ ] `PYTHON_VERSION` = `3.11.0`
- [ ] Service deployed successfully
- [ ] Backend URL saved: `_______________________`
- [ ] Health check works: `/api/health` returns `{"status":"ok"}`

### Frontend Service
- [ ] Static Site created on Render
- [ ] Connected to GitHub repository
- [ ] Root directory set to `frontend`
- [ ] Build command: `npm install && npm run build`
- [ ] Publish directory: `dist`
- [ ] Environment variable added:
  - [ ] `VITE_API_URL` = `https://your-backend-url.onrender.com`
- [ ] Service deployed successfully
- [ ] Frontend URL saved: `_______________________`

### CORS Update
- [ ] Backend CORS updated with frontend URL
- [ ] Code committed and pushed
- [ ] Backend redeployed automatically

## 🧪 Testing

### Backend Tests
- [ ] Visit `/docs` - Swagger UI loads
- [ ] Visit `/api/health` - Returns OK
- [ ] Test `/api/chat` endpoint in Swagger

### Frontend Tests
- [ ] Homepage loads correctly
- [ ] Logo appears in top-left
- [ ] "What can I help you with?" animates
- [ ] Input box works
- [ ] Can send a message
- [ ] Response appears correctly
- [ ] Sources show up
- [ ] "Dive Deeper" button works
- [ ] Related queries appear
- [ ] Suggestions work
- [ ] Conversation menu opens
- [ ] "New Chat" works
- [ ] Can switch between conversations

### Full Integration Tests
- [ ] Ask: "How do I create a campaign?"
- [ ] Response received with sources
- [ ] Click "Dive Deeper"
- [ ] Web search message appears
- [ ] Web results returned
- [ ] Click a related query
- [ ] New response received
- [ ] Open conversation menu
- [ ] See conversation history
- [ ] Click "New Chat"
- [ ] Start fresh conversation

## 🎤 Interview Preparation

### Demo URLs
- Frontend: `_______________________`
- Backend: `_______________________`
- GitHub: `_______________________`

### Keep Backend Warm
- [ ] Set up UptimeRobot or similar (optional)
- [ ] Ping `/api/health` every 10 minutes
- [ ] Or manually visit 30 minutes before interview

### Backup Plan
- [ ] Local version tested and ready
- [ ] Can run locally if deployment fails
- [ ] Screenshots of working app saved

### Talking Points Ready
- [ ] Can explain RAG architecture
- [ ] Can discuss tech stack choices
- [ ] Can demo all features
- [ ] Can explain deployment process
- [ ] Can discuss scaling considerations

## 📱 Day of Interview

### 30 Minutes Before
- [ ] Visit frontend URL - check it loads
- [ ] Send a test message - verify it works
- [ ] Test "Dive Deeper" feature
- [ ] Check conversation history
- [ ] Clear browser cache if needed
- [ ] Have GitHub repo open in tab
- [ ] Have Render dashboard open in tab

### During Demo
- [ ] Share screen with frontend URL
- [ ] Walk through features confidently
- [ ] Show conversation history
- [ ] Demonstrate "Dive Deeper"
- [ ] Mention tech stack
- [ ] Be ready to show code if asked

## 🐛 Emergency Fixes

### If Backend is Down
1. Check Render logs
2. Verify environment variables
3. Restart service manually
4. Fall back to local demo

### If Frontend is Down
1. Check build logs
2. Verify API URL is correct
3. Clear cache and redeploy
4. Fall back to local demo

### If API Calls Fail
1. Check CORS settings
2. Verify backend is running
3. Check network tab in browser
4. Test backend `/docs` endpoint

## ✨ Final Check (5 Minutes Before)

- [ ] Frontend loads ✅
- [ ] Can send message ✅
- [ ] Response received ✅
- [ ] "Dive Deeper" works ✅
- [ ] Menu works ✅
- [ ] Confident and ready! 🚀

---

## 📞 Support Resources

- **Render Status**: https://status.render.com
- **Render Docs**: https://render.com/docs
- **Your Backend Logs**: Render Dashboard → Your Service → Logs
- **Your Frontend Logs**: Render Dashboard → Your Site → Logs

---

**Good luck with your interview! You've got this! 🎉**
