# 🤖 Convie - AI-Powered SMS Magic Assistant

A modern, intelligent chatbot built with RAG (Retrieval-Augmented Generation) technology to help users navigate SMS Magic documentation.

![Convie Demo](https://via.placeholder.com/800x400?text=Add+Your+Screenshot+Here)

## ✨ Features

- **🔍 Smart Search**: Semantic search through SMS Magic documentation using Pinecone vector database
- **🌐 Web Fallback**: Automatically searches the web using Google Search when local data is insufficient
- **💬 Conversation Memory**: Maintains context across multiple questions
- **🎨 Beautiful UI**: Modern interface with smooth animations and transitions
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **🔄 Conversation History**: Save and switch between multiple chat sessions

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI    │─────▶│  Pinecone   │
│  Frontend   │      │   Backend    │      │  Vector DB  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Gemini    │
                     │  AI Model    │
                     └──────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pinecone** - Vector database for semantic search
- **Google Gemini** - AI model for embeddings and generation
- **NumPy** - Numerical computations

### Frontend
- **React** - UI library
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Vite** - Build tool

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Pinecone API Key
- Google Gemini API Key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```env
PINECONE_API_KEY=your_pinecone_key
GEMINI_API_KEY=your_gemini_key
```

4. Run the server:
```bash
python api.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:5174`

## 📦 Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions on deploying to Render.

### Quick Deploy to Render

1. Push code to GitHub
2. Connect repository to Render
3. Deploy backend as Web Service
4. Deploy frontend as Static Site
5. Update environment variables

## 🎯 Key Features Explained

### RAG (Retrieval-Augmented Generation)

1. **User Query** → Converted to embeddings using Gemini
2. **Vector Search** → Pinecone finds relevant documentation
3. **Context Building** → Top results combined with conversation history
4. **AI Generation** → Gemini generates response with context
5. **Source Attribution** → Shows which documents were used

### Dive Deeper Feature

When users click "Dive Deeper":
1. System first searches the local database
2. If no good results (relevance < 0.75), waits 2 seconds
3. Shows message: "Searching the web..."
4. Uses Google Search grounding to find current information
5. Returns comprehensive answer with web sources

### Smart Suggestions

- **Related Queries**: Topic-specific follow-up questions
- **General Suggestions**: Explore different features
- **Context-Aware**: Changes based on current conversation

## 📊 Project Structure

```
convie-chatbot/
├── backend/
│   ├── api.py              # FastAPI application
│   ├── config.py           # Configuration management
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── SourceCard.tsx
│   │   │   ├── PixelBlast.tsx
│   │   │   ├── StaggeredMenu.tsx
│   │   │   └── BlurText.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── DEPLOYMENT_GUIDE.md     # Deployment instructions
└── README.md               # This file
```

## 🎨 UI Components

### PixelBlast Background
- Interactive WebGL-powered background
- Responds to mouse movements
- Smooth animations with hardware acceleration

### StaggeredMenu
- Animated conversation history
- Smooth slide-in transitions
- "New Chat" functionality

### BlurText Animation
- Animated text entrance
- Word-by-word blur effect
- Customizable timing and direction

## 🔐 Security

- API keys stored in environment variables
- CORS configured for specific origins
- No sensitive data in frontend code
- `.env` files excluded from git

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :8000   # Windows
```

**Pinecone connection error:**
- Verify API key is correct
- Check index name matches
- Ensure index has data

### Frontend Issues

**White screen:**
- Check browser console for errors
- Verify API URL is correct
- Check network tab for failed requests

**API calls fail:**
- Ensure backend is running
- Check CORS settings
- Verify environment variables

## 📈 Performance

- **Response Time**: ~2-3 seconds for DB search
- **Web Search**: ~5-7 seconds with fallback
- **Vector Search**: Sub-second with Pinecone
- **UI Animations**: 60 FPS with hardware acceleration

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

## 📝 License

MIT License - feel free to use for your own projects

## 👤 Author

Built by [Your Name] as a demonstration of modern RAG architecture and full-stack development skills.

## 🙏 Acknowledgments

- SMS Magic for documentation
- Pinecone for vector database
- Google for Gemini AI
- React community for amazing tools

---

**Live Demo**: [Add your Render URL here]

**Contact**: [Your Email/LinkedIn]
