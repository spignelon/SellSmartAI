# Include this in your existing clerk_auth.py file

# Add this at the top of the file
import logging
from django.conf import settings

# Then replace the JWT verification part with this code:
try:
    # Only do verification in production
    if not settings.DEBUG:
        # Original verification code
        decoded_token = jwt.decode(token, key=base64decoded_key, algorithms=['RS256', ])
    else:
        # In development, skip verification
        decoded_token = jwt.decode(token, options={"verify_signature": False})
    
    # Continue with the rest of your middleware code...
    
except Exception as e:
    logging.error(f"JWT verification failed: {str(e)}")
    if settings.DEBUG:
        # In development, use fake user data
        request.clerk_user = {"data": {"first_name": "Test User", "image_url": "https://example.com/avatar.jpg"}}
        return self.get_response(request)
    else:
        # In production, return unauthorized
        return JsonResponse({"error": "Authentication failed"}, status=401)
