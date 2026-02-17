# ZenBot - Quick Start Commands

## 🚀 Start Backend + Frontend

### Terminal 1 - Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm install
npm run dev
```

Then open: **http://localhost:3000**

---

## 🐳 Using Docker

```bash
docker-compose --profile web up --build
```

Then open: **http://localhost:3000**

---

## 🧪 Test API Directly

```bash
# Health check
curl http://localhost:8000/api/health

# Chat request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Fe 550D yield strength?", "mode": "fixed"}'

# Get metrics
curl http://localhost:8000/api/metrics
```

---

## 📝 Sample Questions

1. What's the yield strength of Fe 550D 16mm?
2. What's the current price of TMT 12mm?
3. What's the delivery time to Ranchi?
4. What's the difference between Fe 500 and Fe 550D?

---

## 🔧 Troubleshooting

Kill ports if needed:
```bash
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```
