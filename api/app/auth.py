# api/app/auth.py
from fastapi import HTTPException
import aiohttp
import base64
from datetime import datetime, timedelta
import json
from .config import settings, logger
import asyncio
from typing import Optional, Dict

class WarcraftLogsAuth:
    def __init__(self):
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._lock = asyncio.Lock()
        
    @property
    def auth_header(self) -> str:
        """Generate basic auth header for token requests"""
        credentials = f"{settings.CLIENT_ID}:{settings.CLIENT_SECRET}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    async def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        async with self._lock:
            if not self._is_token_valid():
                await self._refresh_token()
            return self._access_token

    def _is_token_valid(self) -> bool:
        """Check if current token is valid"""
        if not self._access_token or not self._token_expiry:
            return False
        return datetime.utcnow() < self._token_expiry - timedelta(minutes=5)

    async def _refresh_token(self) -> None:
        """Refresh the access token"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.WARCRAFT_LOGS_TOKEN_URL,
                    headers={
                        "Authorization": self.auth_header,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={"grant_type": "client_credentials"}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token refresh failed: {error_text}")
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to refresh access token"
                        )
                    
                    data = await response.json()
                    self._access_token = data["access_token"]
                    self._token_expiry = datetime.utcnow() + timedelta(seconds=data["expires_in"])
                    logger.info("Successfully refreshed access token")
                    
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Token refresh error: {str(e)}"
            )

    async def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests including valid token"""
        token = await self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def verify_auth(self) -> bool:
        """Verify authentication is working"""
        try:
            await self.get_access_token()
            return True
        except Exception as e:
            logger.error(f"Auth verification failed: {str(e)}")
            return False
