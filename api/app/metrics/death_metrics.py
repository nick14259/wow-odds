# api/app/metrics/death_metrics.py

from typing import Dict, List, Any
from datetime import datetime

class DeathMetricsCalculator:
    def __init__(self, fights_data: List[Dict]):
        self.fights_data = fights_data
        self.total_pulls = len(fights_data)
        self.total_time = sum((f.get('endTime', 0) - f.get('startTime', 0)) for f in fights_data)
        self.hours_raided = self.total_time / (1000 * 60 * 60)  # Convert ms to hours

    def calculate_overall_deaths(self, player_deaths: List[Dict]) -> Dict[str, Any]:
        """Calculate overall death metrics"""
        total_deaths = len(player_deaths)
        successful_kills = sum(1 for f in self.fights_data if f.get('kill', False))

        return {
            "total_deaths": {
                "value": total_deaths,
                "description": "Total number of deaths across all pulls",
                "odds": calculate_american_odds(total_deaths / self.total_pulls)
            },
            "deaths_per_hour": {
                "value": round(total_deaths / max(1, self.hours_raided), 2),
                "description": "Average deaths per hour of raiding",
                "odds": calculate_american_odds(total_deaths / max(1, self.hours_raided) / 2)  # Normalized to expected 2 deaths/hour
            },
            "deaths_per_pull": {
                "value": round(total_deaths / max(1, self.total_pulls), 2),
                "description": "Average deaths per pull attempt",
                "odds": calculate_american_odds(total_deaths / max(1, self.total_pulls))
            },
            "deaths_per_kill": {
                "value": round(total_deaths / max(1, successful_kills), 2) if successful_kills > 0 else 0,
                "description": "Average deaths per successful kill",
                "odds": calculate_american_odds(total_deaths / max(1, successful_kills) / 3)  # Normalized to expected 3 deaths/kill
            }
        }

    def calculate_death_timing(self, player_deaths: List[Dict]) -> Dict[str, Any]:
        """Calculate death timing metrics"""
        early_deaths = sum(1 for death in player_deaths 
                         if (death.get('timestamp', 0) - death.get('fightStart', 0)) < 30000)  # 30 seconds

        death_orders = []
        for fight in self.fights_data:
            if fight.get('deaths', []):
                death_position = next((i for i, d in enumerate(fight['deaths']) 
                                    if d.get('player') == player_deaths[0].get('player')), -1)
                if death_position != -1:
                    death_orders.append(death_position)

        return {
            "time_to_death_avg": {
                "value": self._calculate_average_death_time(player_deaths),
                "description": "Average time survived in fights before death",
                "odds": self._calculate_survival_odds(player_deaths)
            },
            "early_death_rate": {
                "value": early_deaths / len(player_deaths) if player_deaths else 0,
                "description": "Percentage of deaths occurring in first 30 seconds",
                "odds": calculate_american_odds(early_deaths / max(1, len(player_deaths)))
            },
            "death_order": {
                "first_death_rate": sum(1 for x in death_orders if x == 0) / len(death_orders) if death_orders else 0,
                "last_death_rate": sum(1 for x in death_orders if x == len(death_orders) - 1) / len(death_orders) if death_orders else 0,
                "description": "Pattern of death order in raids"
            }
        }

    def _calculate_average_death_time(self, deaths: List[Dict]) -> float:
        if not deaths:
            return 0
        death_times = [(d.get('timestamp', 0) - d.get('fightStart', 0)) / 1000 for d in deaths]
        return sum(death_times) / len(death_times)

    def _calculate_survival_odds(self, deaths: List[Dict]) -> tuple:
        """Calculate odds of surviving based on death timing patterns"""
        if not deaths:
            return (0, 0)
            
        avg_survival_time = self._calculate_average_death_time(deaths)
        fight_duration_avg = self.total_time / (1000 * self.total_pulls)
        survival_rate = avg_survival_time / fight_duration_avg
        
        return calculate_american_odds(survival_rate)

def calculate_american_odds(probability: float) -> tuple:
    """Convert probability to American odds"""
    if probability <= 0 or probability >= 1:
        return (0, 0)
    
    if probability > 0.5:
        over = int(-100 * probability / (1 - probability))
        under = int(100 * (1 - probability) / probability)
    else:
        over = int(100 * (1 - probability) / probability)
        under = int(-100 * probability / (1 - probability))
    
    return (over, under)
