# 🤖 ZenBot Web Interface POC

> **A modern, real-time AI chat interface with streaming responses and live quality metrics**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Google Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=flat&logo=google)](https://deepmind.google/technologies/gemini/)

---

## ✨ What's This?

This is a **production-ready POC** that transforms ZenBot (your LangSmith-traced AI assistant) into a beautiful web application with:

- 🔥 **Real-time streaming responses** (like ChatGPT)
- 📊 **Live quality metrics** dashboard
- 🎨 **Modern glassmorphism UI** with animations
- ⚡ **FastAPI backend** with async streaming
- ⚛️ **React + TypeScript** frontend
- 🐳 **Docker-ready** deployment

---

## 🎬 Demo Features

### 1️⃣ Streaming Chat Interface
- Type questions and watch AI respond word-by-word
- See quality scores appear after each response
- Switch between "Current Docs" and "Outdated Docs" modes

### 2️⃣ Real-Time Metrics Dashboard
- **Spec Accuracy**: Technical specification correctness
- **Pricing Accuracy**: Pricing information accuracy
- **Hallucination Check**: Safety against false information
- Beautiful animated score cards with color-coded indicators

### 3️⃣ Professional UI/UX
- Dark theme with gradient effects
- Glassmorphism design
- Smooth animations and transitions
- Responsive layout (mobile-friendly)
- Typing indicators and loading states

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Gemini API key
- LangSmith API key (optional)

### Automated Setup

```bash
./setup-poc.sh
```

This will:
1. Check dependencies
2. Set up Python virtual environment
3. Install backend dependencies
4. Install frontend dependencies
5. Guide you through starting the app

### Manual Setup

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Then open:** http://localhost:3000 🎉

---

## 🐳 Docker Compose

```bash
docker-compose --profile web up --build
```

This starts both backend (port 8000) and frontend (port 3000).

Access at: **http://localhost:3000**

---

## 📸 Screenshots

### Chat Interface
```
┌─────────────────────────────────────────────┐
│  🤖 ZenBot                                   │
│  AI-Powered Steel Specifications Assistant  │
├─────────────────────────────────────────────┤
│                                             │
│  👤 User: What's the yield strength of     │
│           Fe 550D 16mm?                     │
│                                             │
│  🤖 Bot: According to IS 1786:2008, the    │
│         yield strength of Fe 550D 16mm is  │
│         565 N/mm²...                       │
│                                             │
│  📊 Spec: 95% | 💰 Price: 100% | ✨ Safe  │
└─────────────────────────────────────────────┘
```

### Metrics Dashboard
```
┌─────────────────────────────┐
│ 📊 Quality Metrics          │
├─────────────────────────────┤
│ 💬 Total Queries: 12        │
│ 🎯 Overall Score: 92%       │
├─────────────────────────────┤
│ 📊 Spec Accuracy            │
│    🌟 95%                   │
│    ████████████████░░░      │
├─────────────────────────────┤
│ 💰 Pricing Accuracy         │
│    ✅ 100%                  │
│    ████████████████████     │
├─────────────────────────────┤
│ ✨ Hallucination Check      │
│    ✅ 88%                   │
│    █████████████████░       │
└─────────────────────────────┘
```

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────┐
│                   Browser                         │
│  ┌─────────────────────────────────────────────┐ │
│  │  React Frontend (TypeScript + Vite)         │ │
│  │  • ChatInterface.tsx (streaming SSE)        │ │
│  │  • MetricsDashboard.tsx (real-time)         │ │
│  │  • Modern CSS with animations               │ │
│  └──────────────────┬──────────────────────────┘ │
└─────────────────────┼────────────────────────────┘
                      │ HTTP + Server-Sent Events
                      ↓
┌───────────────────────────────────────────────────┐
│              FastAPI Backend (Python)             │
│  ┌─────────────────────────────────────────────┐ │
│  │  • /api/chat/stream (SSE streaming)         │ │
│  │  • /api/metrics (aggregate scores)          │ │
│  │  • /api/history (conversation log)          │ │
│  │  • CORS enabled for localhost               │ │
│  └──────────────────┬──────────────────────────┘ │
└─────────────────────┼────────────────────────────┘
                      │
                      ↓
┌───────────────────────────────────────────────────┐
│              ZenBot Core Services                 │
│  ┌─────────────────────────────────────────────┐ │
│  │  • Google Gemini 2.0 Flash (LLM)           │ │
│  │  • LangSmith Tracing (observability)       │ │
│  │  • Quality Evaluators (3 metrics)          │ │
│  │  • Document Knowledge Base                 │ │
│  └─────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints

### Backend API (port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and status |
| POST | `/api/chat` | Non-streaming chat |
| POST | `/api/chat/stream` | **Streaming chat (SSE)** |
| GET | `/api/metrics` | Aggregate quality metrics |
| GET | `/api/history` | Conversation history |
| DELETE | `/api/history` | Clear history |
| GET | `/api/health` | Health check |

**FastAPI Docs:** http://localhost:8000/docs (auto-generated!)

### Example API Call

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the yield strength of Fe 550D?",
    "mode": "fixed"
  }'
```

---

## 📁 Project Structure

```
langshmith/
├── backend/
│   ├── main.py                 # FastAPI app with streaming
│   ├── api_service.py          # ZenBot wrapper service
│   └── requirements.txt        # Backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main app component
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx      # Chat UI with streaming
│   │   │   ├── ChatInterface.css      # Chat styling
│   │   │   ├── MetricsDashboard.tsx   # Metrics UI
│   │   │   └── MetricsDashboard.css   # Metrics styling
│   │   ├── App.css            # Main app styles
│   │   └── index.css          # Global styles
│   ├── package.json           # Frontend dependencies
│   ├── vite.config.ts         # Vite configuration
│   └── tsconfig.json          # TypeScript config
│
├── zenbot.py                  # Core ZenBot implementation
├── evaluators.py              # Quality evaluators
├── docker-compose.yml         # Docker orchestration
├── setup-poc.sh              # Automated setup script
├── FRONTEND_SETUP.md         # Detailed setup guide
├── QUICKSTART.md             # Quick reference
└── README_POC.md             # This file
```

---

## 🎯 Quality Metrics

The system evaluates each response on **3 dimensions**:

| Metric | Weight | Description |
|--------|--------|-------------|
| **Spec Accuracy** | 40% | Correctness of technical specifications (IS 1786, etc.) |
| **Pricing Accuracy** | 30% | Accuracy of pricing and cost information |
| **Hallucination Check** | 30% | Detection of false or made-up information |

### Score Interpretation

| Score | Badge | Meaning |
|-------|-------|---------|
| ≥ 80% | 🌟 | Excellent - High quality response |
| 50-79% | ⚠️ | Good - Minor issues present |
| < 50% | ❌ | Needs Improvement - Significant issues |

---

## 🧪 Sample Questions

Try these to test the system:

1. **Specifications:**
   - "What's the yield strength of Fe 550D 16mm?"
   - "What's the tensile strength of Fe 550D?"
   - "What's the difference between Fe 500 and Fe 550D?"

2. **Pricing:**
   - "What's the current price of TMT 12mm?"
   - "What's the price of TMT 16mm?"
   - "What's the delivery cost to Ranchi?"

3. **Logistics:**
   - "What's the delivery time to Ranchi?"
   - "Is Fe 500D 25mm available in stock?"

4. **Compare Modes:**
   - Ask the same question in "Current Docs" vs "Outdated Docs"
   - Watch the quality scores change!

---

## 🎨 Customization

### Change Theme Colors

Edit `frontend/src/index.css`:

```css
:root {
  --primary-color: #6366f1;  /* Change this */
  --success-color: #10b981;  /* And this */
  /* ... */
}
```

### Add New Evaluators

Edit `evaluators.py` and add your function:

```python
def my_custom_evaluator(prediction: str, expected: str):
    # Your logic here
    return {
        "key": "my_metric",
        "score": 0.95,
        "comment": "Looks good!"
    }
```

Then update `api_service.py` to include it.

---

## 🚀 Deployment

### Backend (Railway / Render / Fly.io)

1. Push to GitHub
2. Connect your repo
3. Set environment variables: `GEMINI_API_KEY`, `LANGSMITH_API_KEY`
4. Deploy!

### Frontend (Vercel / Netlify)

1. Build: `npm run build`
2. Deploy `dist/` folder
3. Set `VITE_API_URL` environment variable

---

## 🛠️ Troubleshooting

### Port already in use
```bash
# Kill port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

### CORS errors
- Backend must be running on port 8000
- Frontend proxy is configured in `vite.config.ts`
- Check browser console for details

### Dependencies won't install
```bash
# Backend
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 💡 Pro Tips for Demo

1. **Show the Streaming**: Open DevTools → Network → Filter by "stream" to see SSE in action
2. **Compare Modes**: Ask same question in both modes, show quality difference
3. **Point Out Metrics**: Highlight the real-time updating scores
4. **Show Responsive**: Resize browser to show mobile layout
5. **Explain Architecture**: Use the ASCII diagram above

---

## 🎓 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [LangSmith Tracing](https://docs.smith.langchain.com/)

---

## 📄 License

This is a POC project for demonstration purposes.

---

## 🤝 Contributing

This is a POC, but feel free to:
- Add more evaluators
- Improve the UI/UX
- Add authentication
- Connect to a real database
- Deploy to production

---

## 🎉 You're All Set!

Run `./setup-poc.sh` and start exploring your ZenBot web interface!

**Questions?** Check `FRONTEND_SETUP.md` for detailed instructions.

**Need quick commands?** See `QUICKSTART.md`.

Happy coding! 🚀✨
