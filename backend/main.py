"""FastAPI backend for ZenBot POC with streaming support"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import asyncio
from datetime import datetime
import sys
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory .env file FIRST
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Explicitly ensure critical env vars are in os.environ
# This is needed because some libraries check os.environ directly
if not os.environ.get("LANGSMITH_API_KEY"):
    from dotenv import dotenv_values
    env_vars = dotenv_values(env_path)
    for key in ["LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGCHAIN_TRACING_V2", "GEMINI_API_KEY", "GOOGLE_API_KEY"]:
        if key in env_vars and not os.environ.get(key):
            os.environ[key] = env_vars[key]

# Add parent directory to path to import zenbot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_service import ZenBotService, evaluate_response
from evaluators import spec_accuracy_evaluator, pricing_evaluator, hallucination_detector

app = FastAPI(title="ZenBot API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ZenBot service
zenbot = ZenBotService()

# In-memory storage for demo (use DB in production)
conversation_history: List[Dict] = []
metrics_history: List[Dict] = []


class ChatRequest(BaseModel):
    message: str
    mode: str = "fixed"  # "fixed" or "buggy"


class EvaluationResponse(BaseModel):
    spec_accuracy: float
    pricing_accuracy: float
    hallucination_check: float
    overall_score: float
    timestamp: str


@app.get("/")
async def root():
    return {
        "service": "ZenBot API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/api/chat",
            "/api/chat/stream",
            "/api/evaluate",
            "/api/metrics",
            "/api/history"
        ]
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Non-streaming chat endpoint"""
    try:
        response = zenbot.get_response(request.message, mode=request.mode)
        
        # Evaluate the response
        evaluation = evaluate_response(request.message, response)
        
        # Store in history
        entry = {
            "id": len(conversation_history) + 1,
            "timestamp": datetime.now().isoformat(),
            "query": request.message,
            "response": response,
            "mode": request.mode,
            "evaluation": evaluation
        }
        conversation_history.append(entry)
        metrics_history.append({
            "timestamp": entry["timestamp"],
            **evaluation
        })
        
        return {
            "response": response,
            "evaluation": evaluation,
            "conversation_id": entry["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint with Server-Sent Events"""
    
    async def event_generator():
        try:
            # Stream the response token by token
            full_response = ""
            response_text = zenbot.get_response(request.message, mode=request.mode)
            
            # Simulate streaming by splitting into words
            words = response_text.split()
            for i, word in enumerate(words):
                full_response += word + " "
                
                # Send each word as a chunk
                yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                await asyncio.sleep(0.05)  # Small delay for visual effect
            
            # Evaluate the full response
            evaluation = evaluate_response(request.message, full_response.strip())
            
            # Send evaluation
            yield f"data: {json.dumps({'type': 'evaluation', 'content': evaluation})}\n\n"
            
            # Store in history
            entry = {
                "id": len(conversation_history) + 1,
                "timestamp": datetime.now().isoformat(),
                "query": request.message,
                "response": full_response.strip(),
                "mode": request.mode,
                "evaluation": evaluation
            }
            conversation_history.append(entry)
            metrics_history.append({
                "timestamp": entry["timestamp"],
                **evaluation
            })
            
            # Send completion
            yield f"data: {json.dumps({'type': 'done', 'conversation_id': entry['id']})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/api/metrics")
async def get_metrics():
    """Get aggregated metrics"""
    if not metrics_history:
        return {
            "total_queries": 0,
            "avg_spec_accuracy": 0,
            "avg_pricing_accuracy": 0,
            "avg_hallucination_check": 0,
            "avg_overall_score": 0,
            "recent_metrics": []
        }
    
    # Calculate averages
    total = len(metrics_history)
    avg_spec = sum(m["spec_accuracy"] for m in metrics_history) / total
    avg_pricing = sum(m["pricing_accuracy"] for m in metrics_history) / total
    avg_hallucination = sum(m["hallucination_check"] for m in metrics_history) / total
    avg_overall = sum(m["overall_score"] for m in metrics_history) / total
    
    return {
        "total_queries": total,
        "avg_spec_accuracy": round(avg_spec, 2),
        "avg_pricing_accuracy": round(avg_pricing, 2),
        "avg_hallucination_check": round(avg_hallucination, 2),
        "avg_overall_score": round(avg_overall, 2),
        "recent_metrics": metrics_history[-10:]  # Last 10 queries
    }


@app.get("/api/history")
async def get_history(limit: int = 10):
    """Get conversation history"""
    return {
        "total": len(conversation_history),
        "conversations": conversation_history[-limit:]
    }


@app.delete("/api/history")
async def clear_history():
    """Clear conversation history"""
    conversation_history.clear()
    metrics_history.clear()
    return {"message": "History cleared successfully"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "zenbot_ready": zenbot.is_ready()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
