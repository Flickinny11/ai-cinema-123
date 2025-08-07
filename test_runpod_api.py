#!/usr/bin/env python3
"""
Test RunPod API with correct schema
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RUNPOD_API_KEY")
API_BASE = "https://api.runpod.io/graphql"

def test_api_call(query, description):
    """Test a specific API call"""
    print(f"\n🧪 Testing: {description}")
    print("-" * 50)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {"query": query}
    
    try:
        response = requests.post(API_BASE, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "errors" in result:
                print(f"❌ GraphQL Errors: {json.dumps(result['errors'], indent=2)}")
            else:
                print(f"✅ Success: {json.dumps(result.get('data', {}), indent=2)}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request Failed: {e}")

def main():
    print("🔍 RunPod API Schema Testing")
    print("=" * 60)
    
    if not API_KEY:
        print("❌ No API key found in .env file")
        return
    
    print(f"API Key: {API_KEY[:10]}...")
    
    # Test 1: Simple user query
    test_api_call("""
    query {
        myself {
            id
        }
    }
    """, "Basic user info")
    
    # Test 2: User with different fields
    test_api_call("""
    query {
        myself {
            id
            email
        }
    }
    """, "User with email")
    
    # Test 3: Templates query
    test_api_call("""
    query {
        myself {
            templates {
                id
                name
            }
        }
    }
    """, "User templates")
    
    # Test 4: Serverless endpoints
    test_api_call("""
    query {
        myself {
            serverlessEndpoints {
                id
                name
            }
        }
    }
    """, "Serverless endpoints")
    
    # Test 5: Public templates search
    test_api_call("""
    query {
        templates {
            id
            name
        }
    }
    """, "Public templates")

if __name__ == "__main__":
    main()