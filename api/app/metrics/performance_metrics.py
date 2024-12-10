# api/app/metrics/performance_metrics.py

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PerformanceEvent:
    timestamp: int
    fight_id: str
    player_id: str
    event_type: str  # 'cast', 'buff', 'damage', 'healing'
    ability_id: int
    ability_name: str
    target_id: Optional[str]
    value: int  # damage/healing amount or cooldown duration

class PerformanceAnalyzer:
    def __init__(self, fights_data: List[Dict], player_class: str, player_spec: str):
        self.fights_data = fights_data
        self.player_class = player_class
        self.player_spec = player_spec
        self.role = self._determine_role()
        
    def analyze_performance(self, player_events: List[Dict]) -> Dict[str, Any]:
        """Analyze overall player performance"""
        events = self._process_events(player_events)
        
        return {
            "fight_execution": self._analyze_fight_execution(events),
            "role_performance": self._analyze_role_performance(events)
        }
        
    def _determine_role(self) -> str:
        """Determine player's role based on class and spec"""
        tanks = ["Protection", "Blood", "Guardian", "Brewmaster", "Vengeance"]
        healers = ["Holy", "Discipline", "Restoration", "Mistweaver", "Preservation"]
        
        if self.player_spec in tanks:
            return "tank"
        elif self.player_spec in healers:
            return "healer"
        else:
            return "dps"

    def _process_events(self, events: List[Dict]) -> List[PerformanceEvent]:
        """Convert raw events into structured PerformanceEvents"""
        processed_events = []
        
        for event in events:
            if event.get('type') in ['cast', 'buff', 'damage', 'healing']:
                processed_event = PerformanceEvent(
                    timestamp=event.get('timestamp', 0),
                    fight_id=event.get('fight_id', ''),
                    player_id=event.get('source', {}).get('id', ''),
                    event_type=event.get('type', ''),
                    ability_id=event.get('ability', {}).get('id', 0),
                    ability_name=event.get('ability', {}).get('name', ''),
                    target_id=event.get('target', {}).get('id', ''),
                    value=event.get('amount', 0)
                )
                processed_events.append(processed_event)
                
        return processed_events

    def _analyze_fight_execution(self, events: List[PerformanceEvent]) -> Dict[str, Any]:
        """Analyze fight execution metrics"""
        return {
            "mechanic_success": self._calculate_mechanic_success(events),
            "cooldown_usage": self._analyze_cooldown_usage(events)
        }

    def _calculate_mechanic_success(self, events: List[PerformanceEvent]) -> Dict[str, Any]:
        """Calculate success rate of handling fight mechanics"""
        mechanic_events = [e for e in events if self._is_mechanic_related(e)]
        total_mechanics = len(mechanic_events)
        successful_mechanics = len([e for e in mechanic_events if self._was_successful(e)])
        
        if total_mechanics == 0:
            return {
                "success_rate": 0,
                "odds": (0, 0)
            }
            
        success_rate = successful_mechanics / total_mechanics
        return {
            "success_rate": success_rate,
            "total_mechanics": total_mechanics,
            "successful": successful_mechanics,
            "odds": calculate_american_odds(success_rate)
        }

    def _analyze_cooldown_usage(self, events: List[PerformanceEvent]) -> Dict[str, Any]:
        """Analyze cooldown usage efficiency"""
        cooldown_events = [e for e in events if self._is_cooldown(e)]
        total_opportunities = self._calculate_cooldown_opportunities()
        used_opportunities = len(cooldown_events)
        
        efficiency = used_opportunities / total_opportunities if total_opportunities > 0 else 0
        
        return {
            "efficiency": efficiency,
            "total_possible": total_opportunities,
            "total_used": used_opportunities,
            "odds": calculate_american_odds(efficiency)
        }

    def _analyze_role_performance(self, events: List[PerformanceEvent]) -> Dict[str, Any]:
        """Analyze role-specific performance metrics"""
        if self.role == "dps":
            return self._analyze_dps_performance(events)
        elif self.role == "healer":
            return self._analyze_healer_performance(events)
        elif self.role == "tank":
            return self._analyze_tank_performance(events)
        return {}

    def _analyze_dps_performance(self, events: List[PerformanceEvent]) -> Dict[str, Any]:
        """Analyze DPS performance metrics"""
        damage_events = [e for e in events if e.event_type == 'damage']
        total_damage = sum(e.value for e in damage_events)
        total_time = self._calculate_total_fight_time()
        
        if total_time == 0:
            return {"dps_uptime": 0, "odds": (0, 0)}
            
        combat_time = self._calculate_active_combat_time(events)
        uptime = combat_time / total_time if total_time > 0 else 0
        
        return {
            "dps_uptime": uptime,
            "odds": calculate_american_odds(uptime)
        }

    def _analyze_healer_performance(self, events: List[PerformanceEvent]) -> Dict[str, Any]:
        """Analyze healer performance metrics"""
        healing_events = [e for e in events if e.event_type == 'healing']
        total_healing = sum(e.value for e in healing_events)
        total_time = self._calculate_total_fight_time()
        
        if total_time == 0:
            return {"healing_efficiency": 0, "odds": (0, 0)}
            
        effective_healing = self._calculate_effective_healing(healing_events)
        efficiency = effective_healing / total_healing if total_healing > 0 else 0
        
        return {
            "healing_efficiency": efficiency,
            "odds": calculate_american_odds(efficiency)
        }

    def _analyze_tank_performance(self, events: List[PerformanceEvent]) -> Dict[str, Any]:
        """Analyze tank performance metrics"""
        total_fights = len(self.fights_data)
        survivable_hits = self._count_survivable_hits(events)
        
        if total_fights == 0:
            return {"survival_rate": 0, "odds": (0, 0)}
            
        survival_rate = survivable_hits / total_fights
        
        return {
            "survival_rate": survival_rate,
            "odds": calculate_american_odds(survival_rate)
        }

    def _is_mechanic_related(self, event: PerformanceEvent) -> bool:
        """Determine if event is related to fight mechanics"""
        # Check if ability is in boss mechanics list
        fight = next((f for f in self.fights_data if f.get('id') == event.fight_id), None)
        if not fight:
            return False
            
        boss_mechanics = self._get_boss_mechanics(fight.get('boss_id', 0))
        return event.ability_id in boss_mechanics.get('mechanic_abilities', [])

    def _was_successful(self, event: PerformanceEvent) -> bool:
        """Determine if mechanic was handled successfully"""
        # Success criteria varies by mechanic type
        if event.event_type == 'cast':
            return True  # Successfully cast ability
        elif event.event_type == 'damage':
            return event.value == 0  # Successfully avoided damage
        return False

    def _is_cooldown(self, event: PerformanceEvent) -> bool:
        """Determine if ability is a major cooldown"""
        # Could be expanded with class-specific cooldown lists
        return event.event_type == 'cast' and event.ability_id in self._get_major_cooldowns()

    def _calculate_cooldown_opportunities(self) -> int:
        """Calculate how many times cooldowns could have been used"""
        total_time = self._calculate_total_fight_time()
        average_cooldown = 180  # 3 minutes in seconds
        return max(1, total_time // average_cooldown)

    def _calculate_total_fight_time(self) -> int:
        """Calculate total time spent in fights"""
        return sum((f.get('endTime', 0) - f.get('startTime', 0)) for f in self.fights_data)

    def _calculate_active_combat_time(self, events: List[PerformanceEvent]) -> int:
        """Calculate time actively participating in combat"""
        if not events:
            return 0
            
        active_threshold = 2500  # 2.5 seconds between events to be considered "active"
        total_active_time = 0
        last_event_time = events[0].timestamp
        
        for event in events[1:]:
            time_diff = event.timestamp - last_event_time
            if time_diff <= active_threshold:
                total_active_time += time_diff
            last_event_time = event.timestamp
            
        return total_active_time

    def _calculate_effective_healing(self, healing_events: List[PerformanceEvent]) -> int:
        """Calculate amount of effective healing (excluding overhealing)"""
        return sum(e.value for e in healing_events if not self._is_overhealing(e))

    def _count_survivable_hits(self, events: List[PerformanceEvent]) -> int:
        """Count number of survivable hits taken"""
        damage_events = [e for e in events if e.event_type == 'damage']
        return len([e for e in damage_events if e.value < self._get_lethal_threshold()])

    def _is_overhealing(self, event: PerformanceEvent) -> bool:
        """Determine if healing event was overhealing"""
        # Overhealing logic would be implemented here
        return False

    def _get_lethal_threshold(self) -> int:
        """Get threshold for lethal damage"""
        return 100000  # Example threshold

    def _get_major_cooldowns(self) -> List[int]:
        """Get list of major cooldown ability IDs for player's class"""
        # Would be implemented with actual cooldown IDs
        return []

    def _get_boss_mechanics(self, boss_id: int) -> Dict[str, Any]:
        """Get mechanics for specific boss"""
        # Would be implemented with actual boss mechanics
        return {"mechanic_abilities": []}

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
