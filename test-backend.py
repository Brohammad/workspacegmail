#!/usr/bin/env python3
"""
Quick test script to verify the POC setup
Run this after starting the backend to test endpoints
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print("\n🔍 Testing chat endpoint...")
    try:
        payload = {
            "message": "What is Fe 550D?",
            "mode": "fixed"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            print("✅ Chat endpoint working!")
            data = response.json()
            print(f"   Response length: {len(data.get('response', ''))} chars")
            print(f"   Evaluation: {data.get('evaluation')}")
            return True
        else:
            print(f"❌ Chat endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")
        return False

def test_metrics():
    """Test metrics endpoint"""
    print("\n🔍 Testing metrics endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/metrics", timeout=5)
        if response.status_code == 200:
            print("✅ Metrics endpoint working!")
            data = response.json()
            print(f"   Total queries: {data.get('total_queries')}")
            print(f"   Avg overall score: {data.get('avg_overall_score')}")
            return True
        else:
            print(f"❌ Metrics endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Metrics endpoint failed: {e}")
        return False

def main():
    print("=" * 50)
    print("🤖 ZenBot POC - Backend Test Suite")
    print("=" * 50)
    
    # Check if backend is running
    print("\n📡 Checking if backend is running on localhost:8000...")
    try:
        requests.get(BASE_URL, timeout=2)
    except:
        print("\n❌ ERROR: Backend is not running!")
        print("   Please start the backend first:")
        print("   $ cd backend && python main.py")
        sys.exit(1)
    
    print("✅ Backend is running!")
    
    # Run tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Chat Endpoint", test_chat()))
    results.append(("Metrics Endpoint", test_metrics()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your POC is ready!")
        print("👉 Now start the frontend: cd frontend && npm run dev")
        print("👉 Then open: http://localhost:3000")
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
