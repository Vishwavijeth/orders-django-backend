from django.contrib.auth import get_user_model
from oauth2_provider.models import Application, AccessToken, RefreshToken
from orders_backend.settings import ACCESS_TOKEN_EXPIRE_SECONDS
from oauthlib.common import generate_token
from django.utils import timezone
from datetime import timedelta

class OAuth2TokenHelper:
    ACCESS_TOKEN_EXPIRE_SECONDS = int(ACCESS_TOKEN_EXPIRE_SECONDS)

    def __init__(self):
        self.application = Application.objects.first()

    def generate_token(self, user):
        access_token_str = generate_token()
        refresh_token_str = generate_token()

        expires = timezone.now() + timedelta(seconds=self.ACCESS_TOKEN_EXPIRE_SECONDS)

        access_token = AccessToken.objects.create(
            user=user,
            application=self.application,
            token=access_token_str,
            expires=expires,
            scope="read write"
        )

        RefreshToken.objects.create(
            user=user,
            application=self.application,
            token=refresh_token_str,
            access_token=access_token
        )

        return self._format_response(access_token, refresh_token_str)
    
    def refresh_access_token(self, refresh_token_str):
        refresh_token = self.get_refresh_token(refresh_token_str)

        if not refresh_token:
            raise Exception("invalid refresh token")
        refresh_token.access_token.delete()

        new_access_token_str = generate_token()
        expires = timezone.now() + timedelta(
            seconds=self.ACCESS_TOKEN_EXPIRE_SECONDS
        )

        new_access_token = AccessToken.objects.create(
            user=refresh_token.user,
            application=self.application,
            token=new_access_token_str,
            expires=expires,
            scope="read write"
        )

        refresh_token.access_token = new_access_token
        refresh_token.save()

        return self._format_response(new_access_token, refresh_token.token)
    
    @staticmethod
    def get_refresh_token(refresh_token_str):
        return(
            RefreshToken.objects
            .filter(token=refresh_token_str)
            .select_related("user", "access_token")
            .first()
        )
    
    @staticmethod
    def get_access_token(access_token_str):
        return (
            AccessToken.objects
            .filter(token=access_token_str)
            .select_related("user")
            .first()
        )
    
    def _format_response(self, access_token_obj, refresh_token_str):
        return {
            "access_token" : access_token_obj.token,
            "refresh_token" : refresh_token_str,
            "expires_in" : self.ACCESS_TOKEN_EXPIRE_SECONDS,
            "token_type" : "Bearer"
        }
