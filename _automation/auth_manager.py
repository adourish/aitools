#!/usr/bin/env python3
"""
Authentication Manager — wraps CredentialResolver for OAuth token management.
Personal services: Gmail, Todoist, Amplenote.
"""

import json
import logging
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests

try:
    from credential_resolver import CredentialResolver
    HAS_RESOLVER = True
except Exception as e:
    HAS_RESOLVER = False
    logger = logging.getLogger(__name__)
    logger.debug(f"CredentialResolver not available: {e}")

logger = logging.getLogger(__name__)

GMAIL_TOKEN_PATH = Path(r'G:\My Drive\Areas\Keys\Gmail\token.json')


class AuthManager:
    """Manages OAuth tokens with automatic refresh via CredentialResolver or environment variables."""

    def __init__(self):
        self._resolver = None
        self._gmail_creds = None
        self._todoist_token = None
        self._amplenote_token = None

        # Try to initialize resolver, fall back to environment variables
        try:
            if HAS_RESOLVER:
                self._resolver = CredentialResolver()
                logger.info("AuthManager initialized (providers: %s)", self._resolver.providers())
            else:
                logger.info("AuthManager initialized (using environment variables)")
        except Exception as e:
            logger.info(f"CredentialResolver failed ({e}), will use environment variables")

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
        """Get Todoist API token from resolver or environment."""
        if not self._todoist_token:
            if self._resolver:
                try:
                    self._todoist_token = self._resolver.get("todoist", "credentials.apiToken")
                except Exception as e:
                    logger.warning(f"Failed to get Todoist token from resolver: {e}")
                    self._todoist_token = os.getenv("TODOIST_TOKEN")
            else:
                self._todoist_token = os.getenv("TODOIST_TOKEN")
        return self._todoist_token

    async def get_openrouter_key(self) -> str:
        """Get OpenRouter API key from resolver or environment."""
        if self._resolver:
            try:
                return self._resolver.get("openrouter", "credentials.apiKey")
            except Exception as e:
                logger.warning(f"Failed to get OpenRouter key from resolver: {e}")
                return os.getenv("OPENROUTER_KEY")
        else:
            return os.getenv("OPENROUTER_KEY")

    async def get_amplenote_token(self) -> str:
        """Get Amplenote access token from resolver or environment."""
        if not self._amplenote_token:
            if self._resolver:
                try:
                    self._amplenote_token = self._resolver.get("amplenote", "oauth.accessToken")
                except Exception as e:
                    logger.warning(f"Failed to get Amplenote token from resolver: {e}")
                    self._amplenote_token = os.getenv("AMPLENOTE_TOKEN")
            else:
                self._amplenote_token = os.getenv("AMPLENOTE_TOKEN")
        return self._amplenote_token

    async def refresh_amplenote_token(self) -> str:
        """Refresh Amplenote access token and persist via resolver."""
        if self._resolver:
            client_id     = self._resolver.get("amplenote", "oauth.clientId")
            refresh_token = self._resolver.get("amplenote", "oauth.refreshToken")
        else:
            client_id = os.getenv("AMPLENOTE_CLIENT_ID")
            refresh_token = os.getenv("AMPLENOTE_REFRESH_TOKEN")

        if not client_id or not refresh_token:
            logger.error("Missing Amplenote credentials for token refresh")
            return None

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
            if self._resolver:
                self._resolver.put("amplenote", "oauth.accessToken", token_data['access_token'])
                if 'refresh_token' in token_data:
                    self._resolver.put("amplenote", "oauth.refreshToken", token_data['refresh_token'])
            else:
                os.environ["AMPLENOTE_TOKEN"] = token_data['access_token']
                if 'refresh_token' in token_data:
                    os.environ["AMPLENOTE_REFRESH_TOKEN"] = token_data['refresh_token']
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
