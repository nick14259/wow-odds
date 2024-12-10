# api/app/utils.py
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from datetime import datetime
from .config import logger

class SimpleCache:
    """Simple in-memory cache implementation"""
    def __init__(self, expiration_seconds: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._expiration = expiration_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if it exists and hasn't expired"""
        if key in self._cache:
            item = self._cache[key]
            if datetime.utcnow().timestamp() - item['timestamp'] < self._expiration:
                return item['data']
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache with current timestamp"""
        self._cache[key] = {
            'data': value,
            'timestamp': datetime.utcnow().timestamp()
        }
    
    def clear(self) -> None:
        """Clear all cached items"""
        self._cache.clear()

def calculate_american_odds(probability: float) -> Tuple[int, int]:
    """
    Convert probability to American odds format
    Returns tuple of (over_odds, under_odds)
    """
    try:
        if not 0 <= probability <= 1:
            raise ValueError("Probability must be between 0 and 1")
        
        if probability > 0.5:
            odds = -100 * probability / (1 - probability)
            opposite_odds = 100 * (1 - probability) / probability
        else:
            odds = 100 * (1 - probability) / probability
            opposite_odds = -100 * probability / (1 - probability)
        
        return (int(round(odds)), int(round(opposite_odds)))
    except Exception as e:
        logger.error(f"Error calculating odds: {str(e)}")
        return (0, 0)

def process_fight_data(fights: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process raw fight data into useful metrics"""
    try:
        if not fights:
            return {}
        
        # Extract basic metrics
        deaths = [fight.get('deaths', 0) for fight in fights]
        durations = [(fight.get('endTime', 0) - fight.get('startTime', 0))/1000 for fight in fights]
        wipes = len([f for f in fights if f.get('fightPercentage', 0) > 0])
        
        # Calculate death probabilities
        death_probs = {
            i: len([d for d in deaths if d <= i]) / len(deaths)
            for i in range(4)  # 0-3 deaths
        }
        
        # Calculate fight metrics
        metrics = {
            'avg_deaths': np.mean(deaths),
            'max_deaths': max(deaths),
            'min_deaths': min(deaths),
            'death_std': np.std(deaths),
            'avg_duration': np.mean(durations),
            'wipe_rate': wipes / len(fights),
            'total_fights': len(fights),
            'death_probabilities': death_probs
        }
        
        return metrics
    except Exception as e:
        logger.error(f"Error processing fight data: {str(e)}")
        return {}

def calculate_confidence_score(data_points: int, min_required: int = 5) -> float:
    """
    Calculate confidence score based on amount of data
    Returns score between 0-1
    """
    try:
        return min(1.0, data_points / min_required)
    except Exception as e:
        logger.error(f"Error calculating confidence score: {str(e)}")
        return 0.0

def format_odds_response(metrics: Dict[str, Any], confidence: float) -> Dict[str, Any]:
    """Format processed metrics into odds response"""
    try:
        death_odds = {}
        for threshold, prob in metrics.get('death_probabilities', {}).items():
            death_odds[str(threshold)] = calculate_american_odds(prob)
        
        wipe_odds = calculate_american_odds(metrics.get('wipe_rate', 0.5))
        
        return {
            "odds": {
                "deaths": death_odds,
                "wipe": {
                    "chance": wipe_odds
                }
            },
            "metrics": {
                "average_deaths": round(metrics.get('avg_deaths', 0), 2),
                "max_deaths": metrics.get('max_deaths', 0),
                "total_fights": metrics.get('total_fights', 0),
                "wipe_rate": round(metrics.get('wipe_rate', 0) * 100, 2)
            },
            "confidence_score": confidence
        }
    except Exception as e:
        logger.error(f"Error formatting odds response: {str(e)}")
        return {}

def validate_input(character: str, server: str, region: str) -> bool:
    """Validate input parameters"""
    valid_regions = {'us', 'eu', 'kr', 'tw', 'cn'}
    try:
        if not character or not server or not region:
            return False
        if region.lower() not in valid_regions:
            return False
        if len(character) < 2 or len(server) < 2:
            return False
        return True
    except Exception as e:
        logger.error(f"Error validating input: {str(e)}")
        return False
