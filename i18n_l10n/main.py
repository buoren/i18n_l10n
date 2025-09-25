"""
Hello World NiceGUI Application
"""

from nicegui import ui
import asyncio
import uuid
from fastapi import Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from .database import db_manager, LanguageCode
from google.cloud import translate_v2 as translate
import logging
from .admin.page import AdminPage

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


# API endpoint for translation using FastAPI directly
from fastapi import APIRouter

# Create a router for API endpoints
api_router = APIRouter()

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
        tag_id = db_manager.create_translation_tag(
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
        translation_text = db_manager.get_translation(tag_id, dst_language)
        
        if not translation_text:
            # If no translation exists, use Google Cloud Translation API
            logger.info(f"No translation found in database for key '{key}' and language '{dst}', using Google Cloud Translation")
            translation_text = translate_with_google_cloud(text, dst, src)
            
            # Save the translation to the database for future use
            try:
                success = db_manager.save_translation(
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


def create_hello_world_app():
    """Create the main Hello World NiceGUI application."""
    
    # Generate a unique session ID for this user
    session_id = str(uuid.uuid4())
    
    # Set page title and favicon
    ui.page_title('Hello World - i18n/l10n App')
    
    # Create a container with some styling
    with ui.column().classes('items-center gap-4 p-8'):
        # Main heading
        ui.html('<h1 style="color: #1976d2; font-size: 3rem; margin-bottom: 1rem;">🌍 Hello World!</h1>')
        
        # Subtitle
        ui.html('<h2 style="color: #666; font-size: 1.5rem; margin-bottom: 2rem;">Welcome to the i18n/l10n Testing App</h2>')
        
        # Interactive elements
        with ui.row().classes('gap-4 items-center'):
            name_input = ui.input('Your Name', placeholder='Enter your name here...').classes('w-64')
            greet_button = ui.button('Say Hello', icon='waving_hand')
        
        # Display area
        greeting_display = ui.html('<div style="font-size: 1.2rem; color: #1976d2; margin-top: 1rem;"></div>')
        
        # Counter section
        ui.html('<h3 style="color: #333; margin: 2rem 0 1rem 0;">Click Counter</h3>')
        with ui.row().classes('gap-4 items-center'):
            counter_display = ui.html('<span style="font-size: 1.5rem; font-weight: bold; color: #1976d2;">0</span>')
            increment_button = ui.button('+', icon='add')
            decrement_button = ui.button('-', icon='remove')
            reset_button = ui.button('Reset', icon='refresh')
        
        # Counter state - simple in-memory counter
        counter_value = {'value': 0}
        
        def update_greeting():
            name = name_input.value.strip()
            if name:
                greeting_text = f"Hello, {name}! 👋"
                greeting_display.content = f'<div style="font-size: 1.2rem; color: #1976d2; margin-top: 1rem;">{greeting_text}</div>'
                # Greeting displayed (no database storage)
            else:
                greeting_text = "Hello, World! 🌍"
                greeting_display.content = f'<div style="font-size: 1.2rem; color: #1976d2; margin-top: 1rem;">{greeting_text}</div>'
                # Greeting displayed (no database storage)
        
        def update_counter():
            counter_display.content = f'<span style="font-size: 1.5rem; font-weight: bold; color: #1976d2;">{counter_value["value"]}</span>'
        
        def increment():
            counter_value['value'] += 1
            update_counter()
        
        def decrement():
            counter_value['value'] -= 1
            update_counter()
        
        def reset():
            counter_value['value'] = 0
            update_counter()
        
        # Connect button events
        greet_button.on_click(update_greeting)
        increment_button.on_click(increment)
        decrement_button.on_click(decrement)
        reset_button.on_click(reset)
        
        # Initialize counter display
        update_counter()
        
        # Simple status message
        ui.html('<div style="margin-top: 2rem; padding: 1rem; background: #e8f5e8; border-radius: 4px; font-size: 0.9rem; color: #2e7d32;">✅ Application running successfully</div>')
        
        # Language selection (for future i18n implementation)
        ui.html('<h3 style="color: #333; margin: 2rem 0 1rem 0;">Language Selection (Coming Soon)</h3>')
        with ui.row().classes('gap-2'):
            ui.button('English', icon='flag').classes('opacity-50')
            ui.button('Español', icon='flag').classes('opacity-50')
            ui.button('Français', icon='flag').classes('opacity-50')
            ui.button('中文', icon='flag').classes('opacity-50')
        
        # Application status
        ui.html('<div style="margin-top: 2rem; padding: 1rem; background: #e8f5e8; border-radius: 4px; font-size: 0.9rem; color: #2e7d32;">✅ Translation API ready</div>')
        
        # Footer
        ui.html('<div style="margin-top: 3rem; color: #999; font-size: 0.9rem;">Built with ❤️ using NiceGUI + Google Cloud Translation</div>')


def main():
    """Main entry point for the application."""
    AdminPage().render_page()
    create_hello_world_app()
    
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
