"""
Hello World NiceGUI Application
"""

from nicegui import ui
import asyncio
import uuid
from fastapi import Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from .database import get_db_manager, LanguageCode
from google.cloud import translate_v2 as translate
import logging
from .admin.page import AdminPage
from .auth import google_auth, create_login_page, create_logout_functionality, get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def translate_with_google_cloud(text: str, target_language: str, source_language: str = "en") -> str:
    """
    Translate text using Google Cloud Translation API.
    
    Args:
        text: The text to translate
        target_language: Target language code (e.g., 'es', 'fr', 'de')
        source_language: Source language code (default: 'en')
    
    Returns:
        Translated text
    """
    try:
        # Initialize the translation client
        translate_client = translate.Client()
        
        # Convert our language codes to Google's format (remove region codes)
        # e.g., 'en-US' -> 'en', 'es-ES' -> 'es'
        source_lang = source_language.split('-')[0] if '-' in source_language else source_language
        target_lang = target_language.split('-')[0] if '-' in target_language else target_language
        
        logger.info(f"Translating '{text}' from {source_lang} to {target_lang}")
        
        # Translate the text
        result = translate_client.translate(
            text,
            target_language=target_lang,
            source_language=source_lang
        )
        
        translated_text = result['translatedText']
        logger.info(f"Translation successful: '{translated_text}'")
        
        return translated_text
        
    except Exception as e:
        logger.error(f"Google Cloud Translation failed: {str(e)}")
        # Return original text if translation fails
        return text


# Pydantic models for API
class TranslateRequest(BaseModel):
    text: str
    src: str
    dst: str
    context: Optional[str] = ""
    key: str


class TranslateResponse(BaseModel):
    text: str
    src: str
    dst: str
    context: str
    key: str
    translation: str


class GoogleAuthRequest(BaseModel):
    credential: str


class AuthResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user: Optional[dict] = None
    error: Optional[str] = None


# API endpoint for translation using FastAPI directly
from fastapi import APIRouter

# Create a router for API endpoints
api_router = APIRouter()

@api_router.post('/api/auth/google')
async def google_auth_endpoint(request: GoogleAuthRequest) -> AuthResponse:
    """
    Handle Google OAuth authentication.
    """
    try:
        # Verify the Google token
        user_info = google_auth.verify_google_token(request.credential)
        
        if not user_info:
            return AuthResponse(
                success=False,
                error="Invalid Google token"
            )
        
        # Create JWT token
        jwt_token = google_auth.create_jwt_token(user_info)
        
        return AuthResponse(
            success=True,
            token=jwt_token,
            user=user_info
        )
        
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}")
        return AuthResponse(
            success=False,
            error=f"Authentication failed: {str(e)}"
        )


@api_router.post('/api/translate')
async def translate_text(request: Request) -> dict:
    """
    Translate text from source language to destination language.
    Currently only supports en-US as source language.
    """
    try:
        # Parse JSON from request body
        body = await request.json()
        
        # Extract fields from request
        text = body.get('text', '')
        src = body.get('src', '')
        dst = body.get('dst', '')
        context = body.get('context', '')
        key = body.get('key', '')
        
        # Validate required fields
        if not all([text, src, dst, key]):
            return {
                'error': 'Missing required fields: text, src, dst, key',
                'status': 400
            }
        
        # Validate source language - only en-US supported for now
        if src != "en-US":
            return {
                'error': f"Source language '{src}' not supported. Only 'en-US' is currently supported.",
                'status': 400
            }
        
        # Validate destination language
        try:
            dst_language = LanguageCode(dst)
        except ValueError:
            return {
                'error': f"Invalid destination language '{dst}'. Must be a valid language code.",
                'status': 400
            }
        
        # Create or get translation tag
        tag_id = get_db_manager().create_translation_tag(
            application="api-translate",
            tag=key,
            context=context
        )
        
        if not tag_id:
            return {
                'error': 'Failed to create translation tag',
                'status': 500
            }
        
        # Get translation from database
        translation_text = get_db_manager().get_translation(tag_id, dst_language)
        
        if not translation_text:
            # If no translation exists, use Google Cloud Translation API
            logger.info(f"No translation found in database for key '{key}' and language '{dst}', using Google Cloud Translation")
            translation_text = translate_with_google_cloud(text, dst, src)
            
            # Save the translation to the database for future use
            try:
                success = get_db_manager().save_translation(
                    translation_tag_id=tag_id,
                    language=dst_language,
                    text=translation_text
                )
                if success:
                    logger.info(f"Saved translation to database: '{translation_text}'")
                else:
                    logger.warning("Failed to save translation to database")
            except Exception as e:
                logger.error(f"Error saving translation to database: {str(e)}")
        else:
            logger.info(f"Found existing translation in database: '{translation_text}'")
        
        return {
            'text': text,
            'src': src,
            'dst': dst,
            'context': context,
            'key': key,
            'translation': translation_text,
            'status': 200
        }
        
    except Exception as e:
        return {
            'error': f'Internal server error: {str(e)}',
            'status': 500
        }


class CreateUserRequest(BaseModel):
    name: str
    email: str


@api_router.post('/api/admin/create-user')
async def create_user_endpoint(request: CreateUserRequest, current_user: dict = Depends(get_current_user)):
    """
    Create a new user in the database.
    Requires valid JWT authentication.
    """
    try:
        # Additional security: verify user is authenticated
        if not current_user or 'email' not in current_user:
            return {
                'success': False,
                'error': 'Authentication required'
            }
        
        # Log the user creation attempt for security monitoring
        logger.info(f"User creation attempt by: {current_user.get('email', 'unknown')}")
        
        # Verify admin access
        if not verify_admin_access(current_user):
            logger.warning(f"Unauthorized user creation attempt by: {current_user.get('email', 'unknown')}")
            return {
                'success': False,
                'error': 'Admin access required'
            }
        
        from .database import get_db_manager, User
        from datetime import datetime
        
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            # Check if user already exists
            existing_user = session.query(User).filter(User.email == request.email).first()
            if existing_user:
                return {
                    'success': True,
                    'message': f'User already exists: {existing_user.name} ({existing_user.email})',
                    'user_id': existing_user.id,
                    'created_at': existing_user.created_at.isoformat() if existing_user.created_at else None
                }
            
            # Create new user
            new_user = User(
                name=request.name,
                email=request.email,
                created_at=datetime.utcnow(),
                is_active=True
            )
            
            session.add(new_user)
            session.commit()
            
            return {
                'success': True,
                'message': f'Successfully created user: {new_user.name} ({new_user.email})',
                'user_id': new_user.id,
                'created_at': new_user.created_at.isoformat() if new_user.created_at else None
            }
            
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def verify_admin_access(current_user: dict) -> bool:
    """
    Verify that the current user has admin access.
    Add your admin verification logic here.
    """
    # For now, basic email verification
    # You can extend this with roles, permissions, etc.
    admin_emails = ['buoren@gmail.com']  # Add your admin emails here
    user_email = current_user.get('email', '')
    return user_email in admin_emails


@api_router.get('/api/admin/verify-access')
async def verify_admin_access_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Verify admin access for the current user.
    This endpoint helps the UI verify admin privileges.
    """
    try:
        if not current_user or 'email' not in current_user:
            return {
                'success': False,
                'error': 'Authentication required'
            }
        
        is_admin = verify_admin_access(current_user)
        
        return {
            'success': True,
            'is_admin': is_admin,
            'user_email': current_user.get('email', '')
        }
        
    except Exception as e:
        logger.error(f"Error verifying admin access: {e}")
        return {
            'success': False,
            'error': 'Access verification failed'
        }


def main():
    """Main entry point for the application."""
    # Create authentication pages
    create_login_page()
    create_logout_functionality()
    
    # Create admin page (will be protected by authentication)
    AdminPage().render_page()
    
    # Include the API router in the NiceGUI app
    from nicegui import app
    app.include_router(api_router)
    
    ui.run(
        host='0.0.0.0',
        port=8080,
        title='Hello World - i18n/l10n App',
        favicon='🌍',
        dark=False,
        show=True
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
