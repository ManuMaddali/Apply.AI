import httpx
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

from config.security import get_security_settings

logger = logging.getLogger(__name__)

class SocialAuthService:
    """Service for handling social authentication with Google and GitHub"""
    
    def __init__(self):
        self.settings = get_security_settings()
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def verify_google_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth2 token and get user info"""
        try:
            print(f"Verifying Google token: {access_token[:10]}...")
            
            # Get user info from Google API
            response = await self.client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            print(f"Google userinfo response status: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"Google user data: {user_data}")
                
                # Ensure we have the required fields
                if not user_data.get('email'):
                    print("Google user data missing email")
                    return None
                
                # Return standardized user data
                return {
                    'provider': 'google',
                    'provider_id': user_data.get('id'),
                    'email': user_data.get('email'),
                    'full_name': user_data.get('name'),
                    'first_name': user_data.get('given_name'),
                    'last_name': user_data.get('family_name'),
                    'profile_image': user_data.get('picture'),
                    'email_verified': user_data.get('verified_email', False),
                    'locale': user_data.get('locale'),
                    'access_token': access_token,
                    'token_expires': (datetime.utcnow() + timedelta(hours=1)).isoformat()  # Default 1 hour expiration
                }
            else:
                print(f"Google API error: {response.status_code}")
                print(f"Response content: {response.text}")
                logger.error(f"Google user info request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Google token verification error: {e}")
            return None
    

    
    async def verify_github_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Verify GitHub OAuth2 token and get user info"""
        try:
            print(f"Verifying GitHub token: {access_token[:10]}...")
            
            # Get user info from GitHub API
            response = await self.client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "ApplyAI-App"
                }
            )
            
            print(f"GitHub user info response status: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Get user email (it might be private)
                email_response = await self.client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "ApplyAI-App"
                    }
                )
                
                email = user_data.get('email')
                email_verified = False
                
                if email_response.status_code == 200:
                    emails = email_response.json()
                    # Find primary email
                    for email_obj in emails:
                        if email_obj.get('primary', False):
                            email = email_obj.get('email')
                            email_verified = email_obj.get('verified', False)
                            break
                
                # Parse name
                full_name = user_data.get('name', '')
                name_parts = full_name.split(' ', 1) if full_name else []
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                return {
                    'provider': 'github',
                    'provider_id': str(user_data.get('id')),
                    'email': email,
                    'full_name': full_name,
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': user_data.get('login'),
                    'profile_image': user_data.get('avatar_url'),
                    'email_verified': email_verified,
                    'bio': user_data.get('bio'),
                    'location': user_data.get('location'),
                    'access_token': access_token,
                    'token_expires': (datetime.utcnow() + timedelta(hours=1)).isoformat()  # Default 1 hour
                }
            else:
                logger.error(f"GitHub user info request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"GitHub token verification error: {e}")
            return None
    
    async def verify_social_token(self, provider: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Verify social token for any supported provider"""
        provider = provider.lower()
        
        if provider == 'google':
            return await self.verify_google_token(access_token)
        elif provider == 'github':
            return await self.verify_github_token(access_token)
        else:
            logger.error(f"Unsupported social provider: {provider}")
            return None
    
    def get_oauth_urls(self) -> Dict[str, str]:
        """Get OAuth authorization URLs for supported providers"""
        # HARDCODE the frontend URL to localhost:3000 for development
        # This ensures it matches exactly what's configured in OAuth providers
        frontend_url = "http://localhost:3000"
        
        print(f"Using hardcoded frontend URL for OAuth: {frontend_url}")
        
        urls = {}
        
        # Google OAuth URL
        if self.settings.google_client_id:
            # Build redirect URI based on environment
            google_redirect_uri = f"{frontend_url}/auth/callback/google"
            print(f"Using Google redirect URI: {google_redirect_uri}")
            
            google_params = {
                'client_id': self.settings.google_client_id,
                'redirect_uri': google_redirect_uri,
                'response_type': 'code',
                'scope': 'openid email profile',
                'access_type': 'offline',
                'prompt': 'consent'
            }
            
            # Build the URL with proper encoding
            from urllib.parse import urlencode
            google_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(google_params)
            urls['google'] = google_url
            
            print(f"Generated Google OAuth URL with redirect_uri: {google_redirect_uri}")
        
        # GitHub OAuth URL
        if self.settings.github_client_id:
            # Build redirect URI based on environment
            github_redirect_uri = f"{frontend_url}/auth/callback/github"
            print(f"Using GitHub redirect URI: {github_redirect_uri}")
            
            github_params = {
                'client_id': self.settings.github_client_id,
                'redirect_uri': github_redirect_uri,
                'scope': 'user:email',
                'state': 'github_oauth_state'
            }
            
            # Build the URL with proper encoding
            from urllib.parse import urlencode
            github_url = "https://github.com/login/oauth/authorize?" + urlencode(github_params)
            urls['github'] = github_url
            
            print(f"Generated GitHub OAuth URL with redirect_uri: {github_redirect_uri}")
        
        return urls
    
    async def exchange_code_for_token(self, provider: str, code: str, redirect_uri: str = None) -> Optional[str]:
        """Exchange OAuth code for access token"""
        provider = provider.lower()
        
        try:
            print(f"🔄 Exchanging code for token - Provider: {provider}")
            print(f"📝 Code length: {len(code)} characters")
            print(f"🔗 Redirect URI provided: {redirect_uri}")
            
            # Use the provided redirect_uri if available, otherwise use the hardcoded one
            # This ensures we use the exact same redirect URI that was used for the initial authorization
            if provider == 'google':
                # Use provided redirect URI if available, otherwise use hardcoded one
                effective_redirect_uri = redirect_uri if redirect_uri else "http://localhost:3000/auth/callback/google"
                print(f"Using Google redirect URI: {effective_redirect_uri}")
                
                if not self.settings.google_client_id or not self.settings.google_client_secret:
                    logger.error("Google OAuth credentials not configured")
                    return None
                
                print(f"Google OAuth exchange - Client ID: {self.settings.google_client_id[:10]}...")
                
                # For Google, we need to include the redirect_uri in the token exchange
                data = {
                    'client_id': self.settings.google_client_id,
                    'client_secret': self.settings.google_client_secret,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': effective_redirect_uri
                }
                print(f"Google OAuth request data: {data}")
                
                # Use form data instead of JSON for Google
                response = await self.client.post(
                    "https://oauth2.googleapis.com/token",
                    data=data
                )
                
            elif provider == 'github':
                # Use provided redirect URI if available, otherwise use hardcoded one
                effective_redirect_uri = redirect_uri if redirect_uri else "http://localhost:3000/auth/callback/github"
                print(f"Using GitHub redirect URI: {effective_redirect_uri}")
                
                if not self.settings.github_client_id or not self.settings.github_client_secret:
                    logger.error("GitHub OAuth credentials not configured")
                    return None
                
                print(f"GitHub OAuth exchange - Client ID: {self.settings.github_client_id}")
                
                data = {
                    'client_id': self.settings.github_client_id,
                    'client_secret': self.settings.github_client_secret,
                    'code': code,
                    'redirect_uri': effective_redirect_uri
                }
                print(f"GitHub OAuth request data: {data}")
                
                response = await self.client.post(
                    "https://github.com/login/oauth/access_token",
                    data=data,
                    headers={'Accept': 'application/json'}
                )
                
            else:
                logger.error(f"Unsupported provider: {provider}")
                return None
            
            print(f"OAuth response status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print(f"OAuth response data: {token_data}")
                
                if 'error' in token_data:
                    print(f"OAuth error: {token_data.get('error')}")
                    print(f"OAuth error description: {token_data.get('error_description')}")
                    return None
                    
                return token_data.get('access_token')
            else:
                logger.error(f"Token exchange failed for {provider}: {response.status_code}")
                print(f"Response content: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Token exchange error for {provider}: {e}")
            return None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

# Singleton instance
_social_auth_service = None

def get_social_auth_service() -> SocialAuthService:
    """Get social auth service instance"""
    global _social_auth_service
    # Force recreation to ensure latest changes are loaded
    _social_auth_service = SocialAuthService()
    return _social_auth_service 