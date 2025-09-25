#!/usr/bin/env python3
"""
Test script for Google Cloud Translation API integration
"""

import requests
import json

# Configuration
API_BASE_URL = "https://i18n-l10n-app-696678025487.europe-north1.run.app"

def test_google_translate_integration():
    """Test the Google Cloud Translation API integration"""
    
    print("=== Testing Google Cloud Translation Integration ===\n")
    
    # Test Case 1: Translation that doesn't exist in database (should call Google API)
    print("--- Test Case 1: New Translation (should call Google Cloud API) ---")
    payload_new = {
        "text": "Hello, how are you today?",
        "src": "en-US",
        "dst": "es-ES",
        "context": "Greeting message",
        "key": "greeting.how_are_you"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/translate", json=payload_new)
        response.raise_for_status()
        result = response.json()
        print(f"Request: {json.dumps(payload_new, indent=2)}")
        print(f"Response ({response.status_code}): {json.dumps(result, indent=2)}")
        
        if 'translation' in result and result['translation'] != payload_new['text']:
            print("✅ Translation successful - Google Cloud API was likely called")
        else:
            print("⚠️  Translation may have failed or returned original text")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during request: {e}\n")
    
    # Test Case 2: Same translation again (should use cached database result)
    print("--- Test Case 2: Cached Translation (should use database) ---")
    try:
        response = requests.post(f"{API_BASE_URL}/api/translate", json=payload_new)
        response.raise_for_status()
        result = response.json()
        print(f"Request: {json.dumps(payload_new, indent=2)}")
        print(f"Response ({response.status_code}): {json.dumps(result, indent=2)}")
        
        if 'translation' in result:
            print("✅ Translation retrieved from database cache")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during request: {e}\n")
    
    # Test Case 3: Different language translation
    print("--- Test Case 3: Different Language Translation ---")
    payload_french = {
        "text": "Good morning, have a great day!",
        "src": "en-US",
        "dst": "fr-FR",
        "context": "Morning greeting",
        "key": "greeting.good_morning"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/translate", json=payload_french)
        response.raise_for_status()
        result = response.json()
        print(f"Request: {json.dumps(payload_french, indent=2)}")
        print(f"Response ({response.status_code}): {json.dumps(result, indent=2)}")
        
        if 'translation' in result and result['translation'] != payload_french['text']:
            print("✅ French translation successful")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during request: {e}\n")
    
    # Test Case 4: Unsupported source language (should fail)
    print("--- Test Case 4: Unsupported Source Language ---")
    payload_unsupported = {
        "text": "Bonjour le monde",
        "src": "fr-FR",
        "dst": "en-US",
        "context": "Test message",
        "key": "test.unsupported_src"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/translate", json=payload_unsupported)
        result = response.json()
        print(f"Request: {json.dumps(payload_unsupported, indent=2)}")
        print(f"Response ({response.status_code}): {json.dumps(result, indent=2)}")
        
        if 'error' in result and 'not supported' in result['error']:
            print("✅ Correctly rejected unsupported source language")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during request: {e}\n")

if __name__ == "__main__":
    test_google_translate_integration()
