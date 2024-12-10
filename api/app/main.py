# api/app/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from .routes import player_metrics
from .services.warcraft_logs import WarcraftLogsClient
from .config import Settings, get_settings

app = FastAPI(
    title="WoW Odds Calculator",
    description="Calculate performance odds based on Warcraft Logs data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection for Warcraft Logs client
async def get_logs_client(settings: Settings = Depends(get_settings)) -> WarcraftLogsClient:
    return WarcraftLogsClient(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET
    )

# Include routers
app.include_router(
    player_metrics.router,
    prefix="/api/v1",
    tags=["player"]
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "WoW Odds Calculator API",
        "version": "1.0.0",
        "status": "operational"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status": "error",
        "code": exc.status_code,
        "message": exc.detail
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {
        "status": "error",
        "code": 500,
        "message": "Internal server error"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
