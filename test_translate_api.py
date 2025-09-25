#!/usr/bin/env python3
"""
Test script for the /api/translate endpoint
"""

import requests
import json

# Configuration
API_BASE_URL = "https://i18n-l10n-app-696678025487.europe-north1.run.app"

def test_translate_api():
    """Test the translation API endpoint"""
    
    print("=== Testing Translation API ===\n")
    
    # Test data
    test_cases = [
        {
            "text": "Hello World",
            "src": "en-US",
            "dst": "es-ES",
            "context": "Main greeting message",
            "key": "hello.world"
        },
        {
            "text": "Welcome to our application",
            "src": "en-US", 
            "dst": "fr-FR",
            "context": "Welcome message on homepage",
            "key": "welcome.message"
        },
        {
            "text": "Click here to continue",
            "src": "en-US",
            "dst": "de-DE", 
            "context": "Button text",
            "key": "button.continue"
        }
    ]
    
    # Test valid requests
    print("--- Testing Valid Requests ---")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['text']} ({test_case['src']} -> {test_case['dst']})")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/translate",
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result['translation']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Test invalid source language
    print("\n--- Testing Invalid Source Language ---")
    invalid_request = {
        "text": "Hello",
        "src": "es-ES",  # Invalid - only en-US supported
        "dst": "en-US",
        "context": "Test",
        "key": "test.invalid"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/translate",
            json=invalid_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print(f"✅ Correctly rejected: {response.json()['detail']}")
        else:
            print(f"❌ Unexpected response: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test invalid destination language
    print("\n--- Testing Invalid Destination Language ---")
    invalid_dst_request = {
        "text": "Hello",
        "src": "en-US",
        "dst": "invalid-lang",  # Invalid language code
        "context": "Test",
        "key": "test.invalid.dst"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/translate",
            json=invalid_dst_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print(f"✅ Correctly rejected: {response.json()['detail']}")
        else:
            print(f"❌ Unexpected response: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n=== API Test Complete ===")

def test_with_curl():
    """Show curl examples for testing the API"""
    
    print("\n=== Curl Examples ===\n")
    
    print("1. Valid translation request:")
    print(f"""curl -X POST "{API_BASE_URL}/api/translate" \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "Hello World", "src": "en-US", "dst": "es-ES", "context": "Main greeting", "key": "hello.world"}}'""")
    
    print("\n2. Invalid source language:")
    print(f"""curl -X POST "{API_BASE_URL}/api/translate" \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "Hello", "src": "es-ES", "dst": "en-US", "context": "Test", "key": "test"}}'""")
    
    print("\n3. Invalid destination language:")
    print(f"""curl -X POST "{API_BASE_URL}/api/translate" \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "Hello", "src": "en-US", "dst": "invalid", "context": "Test", "key": "test"}}'""")

if __name__ == "__main__":
    test_translate_api()
    test_with_curl()
