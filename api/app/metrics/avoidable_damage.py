# api/app/metrics/avoidable_damage.py

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DamageEvent:
    timestamp: int
    ability_id: int
    ability_name: str
    damage: int
    avoidable: bool
    mechanic_type: str  # 'fire', 'void', 'cleave', etc.
    fight_id: str
    player_id: str

class AvoidableDamageAnalyzer:
    def __init__(self, fights_data: List[Dict], boss_mechanics: Dict):
        self.fights_data = fights_data
        self.boss_mechanics = boss_mechanics
        self.avoidable_types = {
            'fire': ['fire', 'flame', 'burn', 'blaze'],
            'void': ['void', 'shadow', 'darkness'],
            'aoe': ['cleave', 'explosion', 'blast', 'wave'],
            'mechanic': ['beam', 'bolt', 'strike']
        }

    def analyze_avoidable_damage(self, player_events: List[Dict]) -> Dict[str, Any]:
        """Analyze all avoidable damage taken by player"""
        damage_events = self._process_damage_events(player_events)
        
        return {
            "standing_in_bad": self._analyze_environmental_damage(damage_events),
            "mechanic_execution": self._analyze_mechanic_damage(damage_events),
            "overall_avoidance": self._calculate_overall_avoidance(damage_events)
        }

    def _process_damage_events(self, events: List[Dict]) -> List[DamageEvent]:
        """Convert raw damage events into structured DamageEvent objects"""
        damage_events = []
        
        for event in events:
            if event.get('type') == 'damage':
                ability_name = event.get('ability', {}).get('name', '').lower()
                
                # Determine if damage was avoidable
                avoidable = self._is_damage_avoidable(ability_name, event)
                
                if avoidable:
                    damage_event = DamageEvent(
                        timestamp=event.get('timestamp', 0),
                        ability_id=event.get('ability', {}).get('id', 0),
                        ability_name=ability_name,
                        damage=event.get('amount', 0),
                        avoidable=True,
                        mechanic_type=self._determine_damage_type(ability_name),
                        fight_id=event.get('fight_id', ''),
                        player_id=event.get('target', {}).get('id', '')
                    )
                    damage_events.append(damage_event)
        
        return damage_events

    def _is_damage_avoidable(self, ability_name: str, event: Dict) -> bool:
        """Determine if damage was avoidable"""
        # Check against known avoidable mechanics
        if any(term in ability_name for terms in self.avoidable_types.values() for term in terms):
            return True
            
        # Check boss-specific mechanics
        fight = next((f for f in self.fights_data if f.get('id') == event.get('fight_id')), None)
        if fight and fight.get('boss_id') in self.boss_mechanics:
            avoidable_abilities = self.boss_mechanics[fight['boss_id']].get('avoidable_abilities', [])
            return event.get('ability', {}).get('id', 0) in avoidable_abilities
            
        return False

    def _determine_damage_type(self, ability_name: str) -> str:
        """Categorize the type of avoidable damage"""
        for damage_type, terms in self.avoidable_types.items():
            if any(term in ability_name for term in terms):
                return damage_type
        return 'other'

    def _analyze_environmental_damage(self, events: List[DamageEvent]) -> Dict[str, Any]:
        """Analyze damage taken from environmental effects"""
        total_damage = sum(e.damage for e in events)
        damage_by_type = {}
        
        for event in events:
            if event.mechanic_type not in damage_by_type:
                damage_by_type[event.mechanic_type] = 0
            damage_by_type[event.mechanic_type] += event.damage

        return {
            "total_damage": {
                "value": total_damage,
                "per_minute": self._calculate_dpm(total_damage),
                "description": "Total avoidable damage taken"
            },
            "damage_breakdown": {
                mechanic: {
                    "total": amount,
                    "percentage": (amount / total_damage * 100) if total_damage else 0,
                    "odds": calculate_american_odds(amount / total_damage if total_damage else 0)
                }
                for mechanic, amount in damage_by_type.items()
            }
        }

    def _analyze_mechanic_damage(self, events: List[DamageEvent]) -> Dict[str, Any]:
        """Analyze damage taken from specific mechanics"""
        total_mechanics = len(self._get_unique_mechanics())
        failed_mechanics = len(set(e.ability_id for e in events))
        
        mechanic_failures = {}
        for event in events:
            key = f"{event.ability_name}_{event.fight_id}"
            if key not in mechanic_failures:
                mechanic_failures[key] = 0
            mechanic_failures[key] += 1

        return {
            "mechanic_failure_rate": {
                "value": failed_mechanics / total_mechanics if total_mechanics else 0,
                "odds": calculate_american_odds(failed_mechanics / total_mechanics if total_mechanics else 0),
                "description": "Rate of failing avoidable mechanics"
            },
            "repeated_failures": {
                mechanic: {
                    "count": count,
                    "odds": calculate_american_odds(count / len(events) if events else 0)
                }
                for mechanic, count in mechanic_failures.items()
                if count > 1  # Only show repeated failures
            }
        }

    def _calculate_overall_avoidance(self, events: List[DamageEvent]) -> Dict[str, Any]:
        """Calculate overall avoidance performance"""
        total_mechanics = self._get_total_mechanic_opportunities()
        avoided_mechanics = total_mechanics - len(events)
        avoidance_rate = avoided_mechanics / total_mechanics if total_mechanics else 0

        return {
            "avoidance_rate": {
                "value": avoidance_rate,
                "odds": calculate_american_odds(avoidance_rate),
                "description": "Success rate at avoiding mechanics"
            },
            "improvement_trend": self._calculate_avoidance_trend(events)
        }

    def _get_unique_mechanics(self) -> List[Dict]:
        """Get list of all unique avoidable mechanics in the fights"""
        mechanics = set()
        for fight in self.fights_data:
            if fight.get('boss_id') in self.boss_mechanics:
                mechanics.update(self.boss_mechanics[fight['boss_id']].get('avoidable_abilities', []))
        return list(mechanics)

    def _calculate_dpm(self, total_damage: int) -> float:
        """Calculate damage per minute"""
        total_minutes = sum((f.get('endTime', 0) - f.get('startTime', 0)) 
                          for f in self.fights_data) / (1000 * 60)
        return total_damage / total_minutes if total_minutes else 0

    def _calculate_avoidance_trend(self, events: List[DamageEvent]) -> Dict[str, Any]:
        """Calculate if player's avoidance is improving over time"""
        if not events:
            return {"trend": "neutral", "confidence": 0}

        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda x: x.timestamp)
        early_failures = len([e for e in sorted_events[:len(sorted_events)//2]])
        late_failures = len([e for e in sorted_events[len(sorted_events)//2:]])
        
        if early_failures > late_failures:
            trend = "improving"
        elif early_failures < late_failures:
            trend = "declining"
        else:
            trend = "stable"
            
        return {
            "trend": trend,
            "confidence": abs(early_failures - late_failures) / len(events),
            "early_vs_late": f"{early_failures}/{late_failures}"
        }

    def _get_total_mechanic_opportunities(self) -> int:
        """Calculate total number of opportunities to avoid mechanics"""
        total = 0
        for fight in self.fights_data:
            if fight.get('boss_id') in self.boss_mechanics:
                mechanics = self.boss_mechanics[fight['boss_id']].get('avoidable_abilities', [])
                total += len(mechanics)
        return total

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
