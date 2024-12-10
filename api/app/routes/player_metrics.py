# api/app/routes/player_metrics.py

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional
from datetime import datetime
from enum import Enum
from ..config import logger, settings
from ..services.warcraft_logs import WarcraftLogsClient

class GameVersion(str, Enum):
    RETAIL = "Retail"
    CATA = "Cata"
    CLASSIC_FRESH = "ClassicFresh"
    SOD = "SoD"
    CLASSIC = "Classic"

router = APIRouter()

@router.get("/player/{region}/{server}/{character}")
async def get_player_metrics(
    region: str,
    server: str,
    character: str,
    version: GameVersion = Query(..., description="Game version"),
    timeframe: Optional[str] = Query("recent", description="Timeframe for analysis (recent, all)")
) -> Dict:
    try:
        logger.info(f"Processing request for {character} on {server}-{region} ({version})")

        # Initialize Warcraft Logs client
        logs_client = WarcraftLogsClient(settings.CLIENT_ID, settings.CLIENT_SECRET)

        # Fetch player logs
        logs_data = await logs_client.fetch_player_logs(
            character=character,
            server=server,
            region=region.lower(),
            version=version.value
        )

        # Check for errors in the response
        if logs_data.get('error'):
            logger.error(f"Error fetching logs: {logs_data['error']}")
            return {
                "character": logs_data['character'],
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "status": logs_data['error']
                }
            }

        # Extract reports
        reports = logs_data.get('reports', [])
        character_info = logs_data.get('character', {})

        metrics = {}
        if reports:
            total_fights = sum(len(report.get('fights', [])) for report in reports)
            total_kills = sum(
                sum(1 for fight in report.get('fights', []) if fight.get('kill', False))
                for report in reports
            )

            metrics = {
                "overview": {
                    "total_reports": len(reports),
                    "total_fights": total_fights,
                    "total_kills": total_kills,
                    "kill_rate": round(total_kills / total_fights * 100, 2) if total_fights > 0 else 0
                },
                "reports": [{
                    "title": report.get('title', 'Unknown'),
                    "date": datetime.fromtimestamp(report.get('startTime', 0)/1000).isoformat(),
                    "zone": report.get('zone', {}).get('name', 'Unknown'),
                    "total_fights": len(report.get('fights', [])),
                    "kills": sum(1 for fight in report.get('fights', []) if fight.get('kill', False))
                } for report in reports[:5]]  # Show last 5 reports
            }
        else:
            metrics = {
                "status": "No logs found for this character",
                "overview": {
                    "total_reports": 0,
                    "total_fights": 0,
                    "total_kills": 0,
                    "kill_rate": 0
                }
            }

        return {
            "character": {
                "name": character_info.get('name', character),
                "server": server,
                "region": region,
                "version": version.value,
                "class": character_info.get('class', 'Unknown')
            },
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }

    except Exception as e:
        logger.error(f"Unexpected error processing request: {str(e)}")
        return {
            "character": {
                "name": character,
                "server": server,
                "region": region,
                "version": version.value
            },
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "status": f"Error processing request: {str(e)}"
            }
        }
