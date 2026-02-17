#!/usr/bin/env python3
"""Simple test script to verify Gemini API key"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
print(f"🔑 API Key loaded: {api_key[:20]}..." if api_key else "❌ No API key found")

if not api_key:
    print("Please set GOOGLE_API_KEY or GEMINI_API_KEY in .env file")
    exit(1)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    # Try different Gemini models
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-2.0-flash-exp",
    ]
    
    print("\n📡 Testing Gemini API with different models...")
    
    success = False
    working_model = None
    
    for model_name in models_to_try:
        try:
            print(f"\n🔄 Trying model: {model_name}")
            
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key
            )
            
            # Test with a simple query
            response = llm.invoke([("human", "Hello, what is 2+2?")])
            
            print(f"✅ SUCCESS with {model_name}!")
            print(f"📝 Response: {response.content[:150]}...")
            
            success = True
            working_model = model_name
            break
            
        except Exception as e:
            print(f"❌ Failed with {model_name}: {str(e)[:100]}...")
            continue
    
    if success:
        print(f"\n🎉 WORKING MODEL FOUND: {working_model}")
        print(f"✅ Your API key is valid!")
        print(f"\nUpdate your code to use: model='{working_model}'")
    else:
        print(f"\n❌ No working model found with this API key")
        print("\nThis usually means:")
        print("1. API key is invalid or expired")
        print("2. API key doesn't have proper permissions")
        print("3. Gemini API service issue")
        print("\nGet a new API key from: https://aistudio.google.com/apikey")
    
except ImportError as e:
    print(f"\n❌ Import ERROR: {str(e)}")
    print("Install required package: pip install langchain-google-genai")
except Exception as e:
    print(f"\n❌ Unexpected ERROR: {str(e)}")
