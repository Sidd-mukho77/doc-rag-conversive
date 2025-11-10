# 🚀 Quick Start Guide

Get Convie running locally in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- Pinecone account with API key
- Google Gemini API key

## Step 1: Clone & Setup (1 minute)

```bash
# If you haven't cloned yet
git clone https://github.com/YOUR_USERNAME/convie-chatbot.git
cd convie-chatbot
```

## Step 2: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
PINECONE_API_KEY=your_pinecone_key_here
GEMINI_API_KEY=your_gemini_key_here
EOF

# Edit .env with your actual keys
# Windows: notepad .env
# Mac/Linux: nano .env

# Start backend
python api.py
```

Backend will run on **http://localhost:8000**

✅ Test: Visit http://localhost:8000/api/health

## Step 3: Frontend Setup (2 minutes)

Open a **new terminal**:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

Frontend will run on **http://localhost:5174**

✅ Test: Visit http://localhost:5174

## Step 4: Test the App (1 minute)

1. Open http://localhost:5174 in your browser
2. You should see:
   - Convie logo in top-left
   - Animated "What can I help you with?" text
   - Purple gradient input box
   - Suggested questions

3. Try asking: **"How do I create a campaign?"**

4. You should get a response with:
   - Answer text
   - Source cards
   - "Dive Deeper" button
   - Related queries
   - Suggestions

## 🎉 You're Ready!

If everything works locally, you're ready to deploy to Render!

Next steps:
1. Read [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
2. Follow [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

## 🐛 Troubleshooting

### Backend won't start

**Error: "No module named 'fastapi'"**
```bash
pip install -r requirements.txt
```

**Error: "PINECONE_API_KEY not found"**
- Make sure `.env` file exists in `backend/` folder
- Check that keys are correct (no quotes needed)

**Error: "Port 8000 already in use"**
```bash
# Kill the process
# Mac/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
# Note the PID, then:
taskkill /PID <PID> /F
```

### Frontend won't start

**Error: "Cannot find module"**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Error: "Port 5174 already in use"**
- Vite will automatically use next available port (5175, 5176, etc.)
- Or kill the process like above

### API calls fail

**Error: "CORS policy"**
- Make sure backend is running
- Check `backend/api.py` CORS settings include `http://localhost:5174`

**Error: "Network request failed"**
- Verify backend is running on port 8000
- Check `frontend/src/components/ChatInterface.tsx` uses correct API_URL

### No responses from AI

**Check Pinecone:**
- Verify your index exists: https://app.pinecone.io
- Index name should be: `sms-magic-gemini`
- Check that index has vectors (should have ~86 documents)

**Check Gemini:**
- Verify API key is valid
- Check quota: https://aistudio.google.com/app/apikey

## 💡 Pro Tips

1. **Keep terminals open**: You need both backend and frontend running
2. **Check logs**: Look at terminal output for errors
3. **Browser console**: Press F12 to see frontend errors
4. **Test incrementally**: Test backend first, then frontend
5. **Clear cache**: If UI looks broken, try Ctrl+Shift+R

## 📝 Environment Variables

### Backend (.env)
```env
PINECONE_API_KEY=pc-xxxxx
GEMINI_API_KEY=AIzaSyxxxxx
```

### Frontend (.env.local) - Optional for local dev
```env
VITE_API_URL=http://localhost:8000
```

## 🔄 Restart Everything

If things get weird:

```bash
# Stop both terminals (Ctrl+C)

# Backend
cd backend
python api.py

# Frontend (new terminal)
cd frontend
npm run dev
```

## ✅ Ready for Deployment?

Once everything works locally:

1. ✅ Backend responds at `/api/health`
2. ✅ Frontend loads and looks good
3. ✅ Can send messages and get responses
4. ✅ "Dive Deeper" works
5. ✅ Conversation menu works

**Next**: Follow [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) to deploy to Render!

---

Need help? Check the main [README.md](./README.md) or [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
