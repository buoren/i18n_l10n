"""
Example usage of the API key system
"""

import secrets
from datetime import datetime, timedelta
from .database import db_manager

def generate_api_key():
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def example_api_key_usage():
    """Example of how to use the API key system"""
    
    print("=== API Key Management Example ===\n")
    
    # Generate a new API key
    api_key = generate_api_key()
    print(f"Generated API key: {api_key}")
    
    # Create an API key
    key_id = db_manager.create_api_key(
        key=api_key,
        application="i18n-l10n-app",
        description="Example API key for testing",
        user_id=1,
        expires_at=datetime.utcnow() + timedelta(days=30)  # Expires in 30 days
    )
    
    if key_id:
        print(f"✅ API key created with ID: {key_id}")
    else:
        print("❌ Failed to create API key")
        return
    
    # Validate the API key
    print("\n--- Validating API Key ---")
    is_valid = db_manager.validate_api_key(api_key)
    if is_valid:
        print("✅ API key is valid")
    else:
        print("❌ API key is invalid or expired")
    
    # Get API key details
    print("\n--- API Key Details ---")
    api_key_obj = db_manager.get_api_key(api_key)
    if api_key_obj:
        print(f"Key: {api_key_obj.key}")
        print(f"Application: {api_key_obj.application}")
        print(f"Description: {api_key_obj.description}")
        print(f"User ID: {api_key_obj.user_id}")
        print(f"Created: {api_key_obj.created_at}")
        print(f"Expires: {api_key_obj.expires_at}")
        print(f"Last Used: {api_key_obj.last_used_at}")
        print(f"Active: {api_key_obj.is_active}")
    
    # Get user's API keys
    print("\n--- User API Keys ---")
    user_keys = db_manager.get_user_api_keys(1)
    print(f"User 1 has {len(user_keys)} API keys:")
    for key in user_keys:
        print(f"  - {key.key[:10]}... ({key.application}) - {key.description}")
    
    # Get application's API keys
    print("\n--- Application API Keys ---")
    app_keys = db_manager.get_application_api_keys("i18n-l10n-app")
    print(f"Application has {len(app_keys)} API keys:")
    for key in app_keys:
        print(f"  - {key.key[:10]}... (User {key.user_id}) - {key.description}")
    
    # Test validation again (should update last_used_at)
    print("\n--- Testing Validation Again ---")
    is_valid = db_manager.validate_api_key(api_key)
    if is_valid:
        print("✅ API key is still valid")
        # Check if last_used_at was updated
        updated_key = db_manager.get_api_key(api_key)
        if updated_key and updated_key.last_used_at:
            print(f"Last used updated to: {updated_key.last_used_at}")
    
    # Deactivate the API key
    print("\n--- Deactivating API Key ---")
    success = db_manager.deactivate_api_key(api_key)
    if success:
        print("✅ API key deactivated")
    else:
        print("❌ Failed to deactivate API key")
    
    # Test validation after deactivation
    print("\n--- Testing Validation After Deactivation ---")
    is_valid = db_manager.validate_api_key(api_key)
    if is_valid:
        print("❌ API key should be invalid now")
    else:
        print("✅ API key correctly invalidated")
    
    print("\n=== Example Complete ===")

def create_sample_api_keys():
    """Create some sample API keys for testing"""
    
    print("Creating sample API keys...")
    
    # Create API keys for different applications
    applications = [
        ("i18n-l10n-app", "Main application API key"),
        ("i18n-l10n-admin", "Admin panel API key"),
        ("i18n-l10n-api", "Public API key"),
    ]
    
    for app, description in applications:
        api_key = generate_api_key()
        key_id = db_manager.create_api_key(
            key=api_key,
            application=app,
            description=description,
            expires_at=datetime.utcnow() + timedelta(days=90)
        )
        
        if key_id:
            print(f"✅ Created {app}: {api_key[:10]}...")
        else:
            print(f"❌ Failed to create {app}")

if __name__ == "__main__":
    example_api_key_usage()
    print("\n" + "="*50 + "\n")
    create_sample_api_keys()
