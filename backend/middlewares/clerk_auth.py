from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
import jwt
import environ
import time
import base64
import backend.settings as settings
import requests

env = environ.Env()
environ.Env.read_env()

class ClerkAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def fetch_user_data_from_clerk(self, user_id):
        CLERK_API_URL = "https://api.clerk.com/v1"
        response = requests.get(
            f"{CLERK_API_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"},
        )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

    def __call__(self, request):

        print("Inside Clerk Middleware")

        # Get the authentication header from the request
        auth_header = get_authorization_header(request).split()

        user = {}

        # Check if the authentication header is present and valid
        if not auth_header or len(auth_header) != 2:
            user['is_authenticated'] = False
            request.clerk_user = user
            return self.get_response(request)

        # Verify the authentication token with Clerk
        token = auth_header[1].decode()

        base64encoded_key = env('CLERK_PEM_PUBLIC_KEY')
        base64encoded_key = base64encoded_key.encode()
        base64decoded_key = base64.b64decode(base64encoded_key)

        decoded_token = jwt.decode(token, key=base64decoded_key, algorithms=['RS256', ])
        print(decoded_token)

        if not decoded_token.get('azp',None) in settings.ALLOWED_PARTIES:
            raise AuthenticationFailed('Unknown source')

        current_unix_time = int(time.time())
        exp_time = decoded_token.get('exp', None)
        nbf_time = decoded_token.get('nbf', None)
        user_id = decoded_token.get('sub', None)
        if exp_time and nbf_time and user_id:
            if current_unix_time > exp_time:
                raise AuthenticationFailed("The token has expired. Login again.")
            if current_unix_time < nbf_time:
                raise AuthenticationFailed('Invalid authentication token')
        else:
            raise AuthenticationFailed('Invalid authentication token')

        user['is_authenticated'] = True
        user['id'] = user_id

        # Fetch the user data from Clerk
        user_data = self.fetch_user_data_from_clerk(user_id)
        if user_data:
            user['data'] = user_data
        else:
            user['data'] = None

        if not user:
            raise AuthenticationFailed('Invalid authentication token')

        # Add the user details to the request object
        request.clerk_user = user

        return self.get_response(request)