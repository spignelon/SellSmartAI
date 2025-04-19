from rest_framework.permissions import BasePermission
from django.conf import settings

class ClerkAuthenticated(BasePermission):
    """
    Permission class that checks if the user is authenticated via Clerk
    """
    def has_permission(self, request, view):
        # Always allow in development mode if BYPASS_CLERK_AUTH is enabled
        if settings.DEBUG and getattr(settings, 'BYPASS_CLERK_AUTH', False):
            return True
            
        # Check if the clerk_user is set on the request
        if hasattr(request, 'clerk_user') and request.clerk_user:
            # In production, ensure it has the correct structure
            if not settings.DEBUG:
                return 'data' in request.clerk_user
            return True
            
        return False