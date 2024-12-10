# api/app/routes/__init__.py

from fastapi import APIRouter
from .player_metrics import router as player_router

__all__ = ["player_router"]
