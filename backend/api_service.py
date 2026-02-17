"""Service wrapper for ZenBot to use in API"""
import sys
import os
from typing import Dict
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Explicitly ensure LangSmith env vars are set in os.environ
# This is needed because LangChain looks for them in os.environ
if not os.environ.get("LANGSMITH_API_KEY"):
    from dotenv import dotenv_values
    env_vars = dotenv_values(env_path)
    if "LANGSMITH_API_KEY" in env_vars:
        os.environ["LANGSMITH_API_KEY"] = env_vars["LANGSMITH_API_KEY"]
    if "LANGSMITH_PROJECT" in env_vars:
        os.environ["LANGSMITH_PROJECT"] = env_vars["LANGSMITH_PROJECT"]

# Add parent directory to import zenbot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from zenbot import build_documents, run_query
    from evaluators import spec_accuracy_evaluator, pricing_evaluator, hallucination_detector
    from langchain_core.tracers.langchain import LangChainTracer
    from langsmith import Client as LangSmithClient
except ImportError as e:
    print(f"Warning: Could not import zenbot modules: {e}")
    build_documents = None
    run_query = None
    LangChainTracer = None
    LangSmithClient = None


class ZenBotService:
    """Wrapper service for ZenBot to use in API context"""
    
    def __init__(self):
        """Initialize ZenBot with document knowledge base and LangSmith tracer"""
        self.documents = build_documents() if build_documents else {}
        self.initialized = run_query is not None
        
        # Initialize LangSmith tracer
        self.tracer = None
        if LangChainTracer is not None and LangSmithClient is not None:
            try:
                # Check if LANGSMITH_API_KEY is available
                langsmith_key = os.environ.get("LANGSMITH_API_KEY")
                project = os.environ.get("LANGSMITH_PROJECT", "Zen_Project")
                
                if langsmith_key:
                    # Create LangSmith client explicitly with API key
                    client = LangSmithClient(api_key=langsmith_key)
                    # Create tracer with explicit client
                    self.tracer = LangChainTracer(project_name=project, client=client)
                    print(f"✅ LangSmith tracer initialized for project: {project}")
                else:
                    print("⚠️  Warning: LANGSMITH_API_KEY not found in environment")
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize LangSmith tracer: {e}")
        
        if self.initialized:
            print("✅ ZenBot service initialized successfully")
        else:
            print("⚠️  Warning: ZenBot modules not available")
    
    def get_response(self, query: str, mode: str = "fixed") -> str:
        """
        Get response from ZenBot
        
        Args:
            query: User question
            mode: "fixed" for current docs, "buggy" for outdated docs
        
        Returns:
            Bot response string
        """
        if not self.initialized or not run_query:
            return "ZenBot is currently unavailable. Please check configuration and ensure GEMINI_API_KEY is set."
        
        try:
            # Use zenbot's run_query function with tracer for LangSmith integration
            result = run_query(query, version=mode, tracer=self.tracer)
            return result.get("answer", "No response generated")
            
        except Exception as e:
            print(f"Error getting response: {e}")
            return f"I encountered an error processing your request: {str(e)}"
    
    def is_ready(self) -> bool:
        """Check if ZenBot is ready to serve requests"""
        return self.initialized


def evaluate_response(query: str, response: str, expected: str = None) -> Dict[str, float]:
    """
    Evaluate a response using the three evaluators
    
    Args:
        query: Original user query
        response: Bot's response
        expected: Expected answer (optional, for training data)
    
    Returns:
        Dictionary with evaluation scores
    """
    # For API usage without ground truth, we do heuristic evaluation
    # In production, you'd have test cases with expected answers
    
    # Use response as baseline for evaluation (self-evaluation mode)
    eval_target = expected if expected else response
    
    try:
        spec_result = spec_accuracy_evaluator(response, eval_target)
        pricing_result = pricing_evaluator(response, eval_target)
        hallucination_result = hallucination_detector(response, eval_target)
        
        # Calculate overall score
        overall = (
            spec_result["score"] * 0.4 +  # 40% weight
            pricing_result["score"] * 0.3 +  # 30% weight
            hallucination_result["score"] * 0.3  # 30% weight
        )
        
        return {
            "spec_accuracy": round(spec_result["score"], 2),
            "pricing_accuracy": round(pricing_result["score"], 2),
            "hallucination_check": round(hallucination_result["score"], 2),
            "overall_score": round(overall, 2),
            "details": {
                "spec_comment": spec_result["comment"],
                "pricing_comment": pricing_result["comment"],
                "hallucination_comment": hallucination_result["comment"]
            }
        }
    except Exception as e:
        print(f"Error in evaluation: {e}")
        return {
            "spec_accuracy": 0.0,
            "pricing_accuracy": 0.0,
            "hallucination_check": 0.0,
            "overall_score": 0.0,
            "details": {"error": str(e)}
        }
