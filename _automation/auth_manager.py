#!/usr/bin/env python3
"""
Authentication Manager — wraps CredentialResolver for OAuth token management.
Personal services: Gmail, Todoist, Amplenote.
"""

import json
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests

from credential_resolver import CredentialResolver

logger = logging.getLogger(__name__)

GMAIL_TOKEN_PATH = Path(r'G:\My Drive\03_Areas\Keys\Environments\Gmail\token.json')


class AuthManager:
    """Manages OAuth tokens with automatic refresh via CredentialResolver."""

    def __init__(self):
        self._resolver = CredentialResolver()
        self._gmail_creds = None
        self._todoist_token = None
        self._amplenote_token = None
        logger.info("AuthManager initialized (providers: %s)", self._resolver.providers())

    async def get_gmail_credentials(self) -> Credentials:
        """Get Gmail credentials from token.json, refreshing if expired."""
        if self._gmail_creds and not self._gmail_creds.expired:
            return self._gmail_creds

        if GMAIL_TOKEN_PATH.exists():
            token_data = json.loads(GMAIL_TOKEN_PATH.read_text())
            self._gmail_creds = Credentials(
                token=token_data['token'],
                refresh_token=token_data['refresh_token'],
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=token_data['scopes']
            )
            if self._gmail_creds.expired and self._gmail_creds.refresh_token:
                logger.info("Refreshing Gmail token")
                self._gmail_creds.refresh(Request())
                token_data['token'] = self._gmail_creds.token
                GMAIL_TOKEN_PATH.write_text(json.dumps(token_data, indent=2))
                logger.info("Gmail token refreshed and saved")

        return self._gmail_creds

    async def get_todoist_token(self) -> str:
        """Get Todoist API token."""
        if not self._todoist_token:
            self._todoist_token = self._resolver.get("todoist", "credentials.apiToken")
        return self._todoist_token

    async def get_openrouter_key(self) -> str:
        """Get OpenRouter API key."""
        return self._resolver.get("openrouter", "credentials.apiKey")

    async def get_amplenote_token(self) -> str:
        """Get Amplenote access token."""
        if not self._amplenote_token:
            self._amplenote_token = self._resolver.get("amplenote", "oauth.accessToken")
        return self._amplenote_token

    async def refresh_amplenote_token(self) -> str:
        """Refresh Amplenote access token and persist via resolver."""
        client_id     = self._resolver.get("amplenote", "oauth.clientId")
        refresh_token = self._resolver.get("amplenote", "oauth.refreshToken")

        logger.info("Refreshing Amplenote access token...")
        response = requests.post(
            'https://api.amplenote.com/oauth/token',
            json={
                'grant_type':    'refresh_token',
                'refresh_token': refresh_token,
                'client_id':     client_id
            },
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            token_data = response.json()
            self._amplenote_token = token_data['access_token']
            self._resolver.put("amplenote", "oauth.accessToken", token_data['access_token'])
            if 'refresh_token' in token_data:
                self._resolver.put("amplenote", "oauth.refreshToken", token_data['refresh_token'])
            logger.info("Amplenote token refreshed (expires in %s s)", token_data.get('expires_in', '?'))
            return self._amplenote_token
        else:
            raise Exception(f"Amplenote token refresh failed: {response.status_code} {response.text}")

    async def refresh_all_tokens(self):
        """Refresh all tokens that need refreshing."""
        logger.info("Checking all tokens for refresh")
        try:
            await self.get_gmail_credentials()
            logger.info("Gmail token checked/refreshed")
        except Exception as e:
            logger.error("Error refreshing Gmail token: %s", e)
        logger.info("Token refresh check complete")
