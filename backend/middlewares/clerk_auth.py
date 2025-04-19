import requests
import json
import jwt
import base64
import logging
from django.conf import settings
from django.http import JsonResponse

def safe_b64decode(s):
    """
    Safely decode a base64 string by adding padding if necessary
    """
    # Add padding '=' characters if the length is not a multiple of 4
    s_padded = s + "=" * (4 - len(s) % 4) if len(s) % 4 else s
    return base64.b64decode(s_padded)

class ClerkAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Inside Clerk Middleware")
        
        # Skip auth for health check endpoint
        if request.path == '/api/health_check':
            return self.get_response(request)

        # Development mode bypass
        if settings.DEBUG and getattr(settings, 'BYPASS_CLERK_AUTH', False):
            print("DEBUG: Using development user data")
            request.clerk_user = {"data": {"first_name": "Dev User", "image_url": "https://example.com/avatar.png"}}
            return self.get_response(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            # No authentication provided
            request.clerk_user = None
            return self.get_response(request)
            
        token = auth_header.split(' ')[1]
        
        try:
            # In development, we'll skip the verification
            if settings.DEBUG:
                print("DEBUG: Skipping JWT verification")
                # Just decode without verification for development
                decoded_token = jwt.decode(token, options={"verify_signature": False})
                request.clerk_user = {"data": {"first_name": "Dev User", "image_url": "https://example.com/avatar.png"}}
            else:
                # Production verification logic here
                # This would include proper JWT verification
                pass
                
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            if settings.DEBUG:
                print(f"DEBUG: Auth error, using fallback user: {str(e)}")
                request.clerk_user = {"data": {"first_name": "Dev User", "image_url": "https://example.com/avatar.png"}}
            else:
                request.clerk_user = None
                
        return self.get_response(request)