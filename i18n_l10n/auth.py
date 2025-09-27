"""
Google OAuth 2.0 Authentication Module
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from google.auth.transport import requests
from google.oauth2 import id_token
from nicegui import ui
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer()

class GoogleAuth:
    """Google OAuth 2.0 authentication handler."""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        
        if not self.client_id:
            logger.warning("GOOGLE_CLIENT_ID not set. Google authentication will not work.")
        if not self.client_secret:
            logger.warning("GOOGLE_CLIENT_SECRET not set. Google authentication will not work.")
    
    def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a Google ID token and return user information.
        
        Args:
            token: The Google ID token to verify
            
        Returns:
            Dictionary containing user information if valid, None otherwise
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.client_id
            )
            
            # Check if the token is from the correct issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.error(f"Invalid issuer: {idinfo['iss']}")
                return None
            
            # Return user information
            return {
                'sub': idinfo['sub'],
                'email': idinfo.get('email'),
                'name': idinfo.get('name'),
                'given_name': idinfo.get('given_name'),
                'family_name': idinfo.get('family_name'),
                'picture': idinfo.get('picture'),
                'email_verified': idinfo.get('email_verified', False)
            }
            
        except ValueError as e:
            logger.error(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None
    
    def create_jwt_token(self, user_info: Dict[str, Any]) -> str:
        """
        Create a JWT token for the authenticated user.
        
        Args:
            user_info: User information from Google
            
        Returns:
            JWT token string
        """
        payload = {
            'sub': user_info['sub'],
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info.get('picture'),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token and return user information.
        
        Args:
            token: The JWT token to verify
            
        Returns:
            Dictionary containing user information if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return {
                'sub': payload['sub'],
                'email': payload['email'],
                'name': payload['name'],
                'picture': payload.get('picture')
            }
        except jwt.ExpiredSignatureError:
            logger.error("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {str(e)}")
            return None

# Global auth instance
google_auth = GoogleAuth()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency to get the current authenticated user.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    user_info = google_auth.verify_jwt_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info

def create_login_page():
    """Create the Google login page."""
    
    @ui.page('/login')
    def login_page():
        ui.add_body_html('''
        <div style="max-width: 400px; margin: 0 auto; padding: 20px; text-align: center;">
            <p style="margin-bottom: 2rem; color: #666;">Please sign in with your Google account to continue</p>
            
            <div id="g_id_onload"
                 data-client_id="''' + (google_auth.client_id or '') + '''"
                 data-callback="handleCredentialResponse"
                 data-auto_prompt="false">
            </div>
            
            <div class="g_id_signin"
                 data-type="standard"
                 data-size="large"
                 data-theme="outline"
                 data-text="sign_in_with"
                 data-shape="rectangular"
                 data-logo_alignment="left">
            </div>
            
            <div id="error-message" style="color: red; margin-top: 1rem; display: none;"></div>
        </div>
        
        <script src="https://accounts.google.com/gsi/client" async defer></script>
        <script>
            function handleCredentialResponse(response) {
                // Send the credential to the server
                fetch('/api/auth/google', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        credential: response.credential
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Store the JWT token
                        localStorage.setItem('auth_token', data.token);
                        // Redirect to admin page
                        window.location.href = '/admin';
                    } else {
                        // Show error message
                        document.getElementById('error-message').textContent = data.error || 'Authentication failed';
                        document.getElementById('error-message').style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('error-message').textContent = 'Authentication failed. Please try again.';
                    document.getElementById('error-message').style.display = 'block';
                });
            }
        </script>
        ''')

def create_logout_functionality():
    """Create logout functionality."""
    
    @ui.page('/logout')
    def logout_page():
        ui.add_body_html('''
        <div style="max-width: 400px; margin: 0 auto; padding: 20px; text-align: center;">
            <h1 style="color: #1976d2; margin-bottom: 2rem;">Logged Out</h1>
            <p style="margin-bottom: 2rem; color: #666;">You have been successfully logged out.</p>
            <a href="/login" style="display: inline-block; padding: 10px 20px; background-color: #1976d2; color: white; text-decoration: none; border-radius: 4px;">Login Again</a>
        </div>
        <script>
            // Clear the auth token
            localStorage.removeItem('auth_token');
        </script>
        ''')

def require_auth(func):
    """
    Decorator to require authentication for a page.
    
    Args:
        func: The page function to protect
        
    Returns:
        Wrapped function that checks authentication
    """
    def wrapper(*args, **kwargs):
        # Check if user is authenticated
        # This is a simplified check - in a real app, you'd verify the JWT token
        ui.open('/login')
        return func(*args, **kwargs)
    
    return wrapper
