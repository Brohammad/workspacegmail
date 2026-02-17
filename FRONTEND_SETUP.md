# 🚀 ZenBot Frontend POC - Quick Start Guide

This guide will help you run the **ZenBot Web Interface POC** - a modern, real-time chat interface with streaming responses and live quality metrics.

## 🎯 What You Get

- **🤖 Real-time AI Chat**: Chat with ZenBot with streaming responses (like ChatGPT)
- **📊 Live Metrics Dashboard**: See quality scores update in real-time
- **✨ Modern UI**: Beautiful glassmorphism design with animations
- **🔄 Mode Switching**: Toggle between current/outdated docs to compare
- **📈 Quality Tracking**: Spec accuracy, pricing accuracy, hallucination detection

---

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Google Gemini API key
- LangSmith API key (optional, for tracing)

---

## 🚀 Option 1: Quick Start (Recommended)

### Step 1: Set up environment variables

```bash
# Make sure your .env file has these keys:
GEMINI_API_KEY=your_gemini_api_key_here
LANGSMITH_API_KEY=your_langsmith_key_here  # Optional
LANGSMITH_PROJECT=Zen_Project
```

### Step 2: Run Backend

```bash
# From project root
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the API server
python main.py
```

The backend will start on **http://localhost:8000**

### Step 3: Run Frontend (in a new terminal)

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

The frontend will start on **http://localhost:3000**

### Step 4: Open in Browser

Navigate to **http://localhost:3000** and start chatting! 🎉

---

## 🐳 Option 2: Docker Compose (All-in-One)

```bash
# From project root
docker-compose --profile web up --build
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000

Access the app at **http://localhost:3000**

---

## 🎨 Features Demo

### 1. **Chat Interface**
- Type a question or click a sample question
- Watch the response stream in real-time
- See quality scores appear after each response

### 2. **Quality Metrics**
- Spec Accuracy (📊): Correctness of technical specs
- Pricing Accuracy (💰): Accuracy of pricing info
- Hallucination Check (✨): Safety against false info

### 3. **Mode Switching**
- **✅ Current Docs**: Uses up-to-date knowledge base
- **❌ Outdated Docs**: Uses old docs (for testing)

---

## 🧪 Sample Questions to Try

1. "What's the yield strength of Fe 550D 16mm?"
2. "What's the current price of TMT 12mm?"
3. "What's the delivery time to Ranchi?"
4. "What's the difference between Fe 500 and Fe 550D?"

---

## 📡 API Endpoints

The backend exposes these endpoints:

- **GET** `/` - API info
- **POST** `/api/chat` - Non-streaming chat
- **POST** `/api/chat/stream` - Streaming chat (SSE)
- **GET** `/api/metrics` - Get aggregate metrics
- **GET** `/api/history` - Get conversation history
- **GET** `/api/health` - Health check

### Example API Call

```bash
# Test the backend directly
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Fe 550D?", "mode": "fixed"}'
```

---

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is available
lsof -ti:8000 | xargs kill -9

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Frontend won't start
```bash
# Check if port 3000 is available
lsof -ti:3000 | xargs kill -9

# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API connection errors
- Make sure backend is running on port 8000
- Check browser console for CORS errors
- Verify `.env` file has all required keys

---

## 🎯 Architecture

```
┌─────────────────────────────────────────┐
│         Browser (localhost:3000)        │
│  ┌────────────────────────────────────┐ │
│  │   React Frontend (TypeScript)      │ │
│  │   • ChatInterface                  │ │
│  │   • MetricsDashboard               │ │
│  │   • Streaming SSE Client           │ │
│  └────────────┬───────────────────────┘ │
└───────────────┼─────────────────────────┘
                │ HTTP/SSE
                ↓
┌─────────────────────────────────────────┐
│      FastAPI Backend (port 8000)        │
│  ┌────────────────────────────────────┐ │
│  │   /api/chat/stream                 │ │
│  │   /api/metrics                     │ │
│  │   /api/history                     │ │
│  └────────────┬───────────────────────┘ │
└───────────────┼─────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────┐
│           ZenBot Service                │
│  ┌────────────────────────────────────┐ │
│  │   • Google Gemini 2.0 Flash        │ │
│  │   • LangSmith Tracing              │ │
│  │   • Quality Evaluators             │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 📊 Quality Thresholds

The system evaluates each response on 3 dimensions:

| Metric | Excellent | Good | Needs Work |
|--------|-----------|------|------------|
| Spec Accuracy | ≥80% 🌟 | 50-79% ⚠️ | <50% ❌ |
| Pricing Accuracy | ≥80% 🌟 | 50-79% ⚠️ | <50% ❌ |
| Hallucination Check | ≥80% 🌟 | 50-79% ⚠️ | <50% ❌ |

---

## 🚀 Next Steps

1. **Customize the UI**: Edit `frontend/src/components/*.css` for styling
2. **Add More Evaluators**: Extend `evaluators.py` with new metrics
3. **Connect to Real DB**: Replace in-memory storage in `main.py`
4. **Deploy to Production**: Use Vercel (frontend) + Railway (backend)

---

## 💡 Tips for Impressive Demo

1. **Show Streaming**: Type a complex question and watch it stream
2. **Compare Modes**: Ask the same question in both modes
3. **Point Out Metrics**: Highlight the real-time quality scores
4. **Show Responsiveness**: Resize the browser to show mobile layout
5. **Explain Architecture**: Use the diagram to show the flow

---

## 🎉 You're Ready!

Your ZenBot POC is now running. Open **http://localhost:3000** and start exploring!

**Pro tip**: Open the browser DevTools (F12) → Network tab to see the streaming responses in action! 🔥

---

## 📞 Need Help?

- Check logs: `backend/main.py` prints all requests
- API docs: http://localhost:8000/docs (FastAPI auto-generates this!)
- Frontend console: Browser DevTools → Console tab

Happy chatting! 🤖✨
