# api/app/services/warcraft_logs.py

import aiohttp
import base64
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException
from ..config import logger, settings

# GraphQL query for character logs
CHARACTER_LOGS_QUERY = """
query ($name: String!, $server: String!, $region: String!) {
    characterData {
        character(name: $name, serverSlug: $server, serverRegion: $region) {
            name
            classID
            recentReports(limit: 50) {
                data {
                    title
                    startTime
                    endTime
                    code
                    zone {
                        id
                        name
                    }
                    fights {
                        id
                        name
                        difficulty
                        kill
                        fightPercentage
                        startTime
                        endTime
                        lastPhase
                    }
                }
            }
        }
    }
}
"""

class WarcraftLogsClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

        # API URLs for different game versions
        self.api_urls = {
            "SoD": "https://sod.warcraftlogs.com/api/v2/client",
            "Classic": "https://classic.warcraftlogs.com/api/v2/client",
            "ClassicFresh": "https://classic.warcraftlogs.com/api/v2/client",
            "Retail": "https://www.warcraftlogs.com/api/v2/client",
            "Cata": "https://classic.warcraftlogs.com/api/v2/client"
        }

    async def fetch_player_logs(
        self,
        character: str,
        server: str,
        region: str,
        version: str
    ) -> Dict[str, Any]:
        """Fetch player logs from Warcraft Logs"""
        try:
            # Format server name: remove spaces, convert to lowercase
            formatted_server = server.lower().replace(" ", "-").replace("'", "")
            formatted_character = character.lower()  # Character names are case insensitive
            
            api_url = self.api_urls.get(version)
            if not api_url:
                return {
                    "character": {"name": character, "server": server, "region": region},
                    "error": f"Unsupported game version: {version}"
                }

            logger.info(f"Fetching logs for {formatted_character} on {formatted_server}-{region} ({version}) from {api_url}")

            headers = await self._get_auth_headers()

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url,
                    headers=headers,
                    json={
                        "query": CHARACTER_LOGS_QUERY,
                        "variables": {
                            "name": formatted_character,
                            "server": formatted_server,
                            "region": region
                        }
                    }
                ) as response:
                    response_text = await response.text()
                    logger.info(f"Raw API response: {response_text}")
                    
                    if response.status != 200:
                        logger.error(f"API request failed with status {response.status}: {response_text}")
                        return {
                            "character": {
                                "name": character,
                                "server": server,
                                "region": region
                            },
                            "error": f"API request failed: {response_text}"
                        }

                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response: {response_text}")
                        return {
                            "character": {
                                "name": character,
                                "server": server,
                                "region": region
                            },
                            "error": "Invalid response from API"
                        }

                    if 'errors' in data:
                        logger.error(f"GraphQL errors: {data['errors']}")
                        return {
                            "character": {
                                "name": character,
                                "server": server,
                                "region": region
                            },
                            "error": f"GraphQL error: {data['errors'][0].get('message', 'Unknown error')}"
                        }

                    return self._process_logs_response(data)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                "character": {
                    "name": character,
                    "server": server,
                    "region": region
                },
                "error": f"Failed to fetch data: {str(e)}"
            }

    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        if not self._is_token_valid():
            await self._refresh_token()

        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    def _is_token_valid(self) -> bool:
        """Check if current token is valid"""
        if not self._access_token or not self._token_expiry:
            return False
        return datetime.utcnow() < self._token_expiry - timedelta(minutes=5)

    async def _refresh_token(self) -> None:
        """Refresh the OAuth token"""
        try:
            auth_str = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_str.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://www.warcraftlogs.com/oauth/token",
                    headers=headers,
                    data={"grant_type": "client_credentials"}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token refresh failed: {error_text}")
                        raise Exception("Failed to refresh access token")

                    data = await response.json()
                    self._access_token = data["access_token"]
                    self._token_expiry = datetime.utcnow() + timedelta(seconds=data["expires_in"])
                    logger.info("Successfully refreshed access token")

        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise Exception("Failed to authenticate with Warcraft Logs")

    def _process_logs_response(self, data: Dict) -> Dict[str, Any]:
        """Process and structure the API response data"""
        character_data = data.get('data', {}).get('characterData', {}).get('character', {})
        if not character_data:
            return {
                'character': None,
                'reports': [],
                'error': "Character not found"
            }

        reports = character_data.get('recentReports', {}).get('data', [])
        class_name = self._get_class_name(character_data.get('classID'))

        return {
            'character': {
                'name': character_data.get('name'),
                'class': class_name,
                'classID': character_data.get('classID')
            },
            'reports': reports,
            'error': None if reports else "No logs found for character"
        }

    def _get_class_name(self, class_id: int) -> str:
        """Convert class ID to class name"""
        class_names = {
            1: "Warrior",
            2: "Paladin",
            3: "Hunter",
            4: "Rogue",
            5: "Priest",
            6: "Death Knight",
            7: "Shaman",
            8: "Mage",
            9: "Warlock",
            10: "Monk",
            11: "Druid",
            12: "Demon Hunter",
            13: "Evoker"
        }
        return class_names.get(class_id, "Unknown")
