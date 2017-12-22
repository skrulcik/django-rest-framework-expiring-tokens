"""Tests for Expiring Tokens obtain-token view."""
from datetime import timedelta
from time import sleep

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from drf_expiring_tokens.models import ExpiringToken


class ObtainExpiringTokenViewTestCase(APITestCase):

    """Tests for the Obtain Expiring Token View."""

    def setUp(self):
        """Create a user."""
        self.username = 'test'
        self.email = 'test@test.com'
        self.password = 'test'
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def _obtain_token(self, username=None, password=None):
        """
        Returns the response of a call to obtain-token. The correct username
        and password are used by default, but may be overriden.

        An argument of ``None`` for either parameter is equivalent to not
        giving a paramter. That is, the default value will be used.
        """
        return self.client.post(
            '/obtain-token/',
            {
                'username': self.username if username is None else username,
                'password': self.password if password is None else password
            }
        )

    def test_post(self):
        """Check token can be obtained by posting credentials."""
        token = ExpiringToken.objects.create(user=self.user)

        response = self._obtain_token()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response contains the token key.
        self.assertEqual(token.key, response.data['token'])

    def test_post_create_token(self):
        """Check token is created if none exists."""
        response = self._obtain_token()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check token was created and the response contains the token key.
        token = ExpiringToken.objects.first()
        self.assertEqual(token.user, self.user)
        self.assertEqual(response.data['token'], token.key)

    def test_post_no_credentials(self):
        """Check POST request with no credentials fails."""
        response = self.client.post('/obtain-token/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
                'username': ['This field is required.'],
                'password': ['This field is required.']
            }
        )

    def test_post_no_username(self):
        """Check POST request with no username, but with a password, fails."""
        response = self.client.post('/obtain-token/', {
                'password': self.password
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
                'username': ['This field is required.'],
            }
        )

    def test_post_no_password(self):
        """Check POST request with no password, but with a username, fails."""
        response = self.client.post('/obtain-token/', {
                'username': self.username
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
                'password': ['This field is required.']
            }
        )

    def test_post_wrong_credentials(self):
        """Check POST request with wrong credentials fails."""
        response = self._obtain_token(password='wrong')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
                'non_field_errors': [
                    'Unable to log in with provided credentials.'
                ]
            }
        )

    def test_empty_password(self):
        """
        Check that an empty password does not authenticate (see Intel AMT and
        Apple High Sierra vulns)
        """

        response = self._obtain_token(password='')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
                'password': [
                    'This field may not be blank.'
                ]
            }
        )

    def test_post_expired_token(self):
        """Check that expired tokens are replaced."""
        token = ExpiringToken.objects.create(user=self.user)
        key_1 = token.key

        # Make the first token expire.
        with self.settings(EXPIRING_TOKEN_LIFESPAN=timedelta(milliseconds=1)):
            sleep(0.001)
            response = self._obtain_token()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check token was renewed and the response contains the token key.
        token = ExpiringToken.objects.first()
        key_2 = token.key
        self.assertEqual(token.user, self.user)
        self.assertEqual(response.data['token'], token.key)
        self.assertTrue(key_1 != key_2)

        # Check that the old token was removed, leaving only the new one
        self.assertEqual(len(ExpiringToken.objects.filter(key=key_1)), 0)
