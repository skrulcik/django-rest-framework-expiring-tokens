"""Utility views for Expiring Tokens.

Classes:
    ObtainExpiringAuthToken: View to provide tokens to clients.
"""
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from drf_expiring_tokens.models import ExpiringToken
from drf_expiring_tokens.settings import token_settings


class ObtainExpiringAuthToken(ObtainAuthToken):

    """View enabling username/password exchange for expiring token."""

    model = ExpiringToken
    serializer_class = AuthTokenSerializer

    def post(self, request):
        """Respond to POSTed username/password with token."""
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, _ = self.model.objects.get_or_create(user=user)

        if token.expired() or token_settings.ALWAYS_RESET_TOKEN:
            # If the token is expired, generate a new one.
            token.delete()
            token = self.model.objects.create(user=user)

        return Response({'token': token.key})


obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()
