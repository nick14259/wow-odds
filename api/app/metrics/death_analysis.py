# api/app/metrics/death_analysis.py

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DeathEvent:
    timestamp: int
    player_id: str
    fight_id: str
    cause: str
    ability_id: Optional[int]
    source_id: Optional[str]
    phase: Optional[int]
    raid_health: float  # Raid health percentage at time of death
    related_deaths: List[str]  # Other deaths within 5 seconds

class DeathCauseAnalyzer:
    def __init__(self, fights_data: List[Dict], boss_mechanics: Dict):
        self.fights_data = fights_data
        self.boss_mechanics = boss_mechanics
        self.mechanic_deaths: Dict[str, List[DeathEvent]] = {}
        self.environmental_deaths: List[DeathEvent] = []
        self.chain_deaths: List[List[DeathEvent]] = []

    def analyze_death_causes(self, player_deaths: List[Dict]) -> Dict[str, Any]:
        """Analyze and categorize death causes"""
        death_events = self._process_death_events(player_deaths)
        
        mechanic_deaths = self._categorize_mechanic_deaths(death_events)
        environment_deaths = self._identify_environmental_deaths(death_events)
        chain_deaths = self._identify_chain_deaths(death_events)
        unavoidable_deaths = self._identify_unavoidable_deaths(death_events)

        return {
            "mechanic_deaths": {
                "total": len(mechanic_deaths),
                "by_mechanic": self._group_mechanic_deaths(mechanic_deaths),
                "odds": calculate_american_odds(len(mechanic_deaths) / len(death_events) if death_events else 0),
                "description": "Deaths caused by failing specific boss mechanics"
            },
            "environment_deaths": {
                "total": len(environment_deaths),
                "details": self._summarize_environmental_deaths(environment_deaths),
                "odds": calculate_american_odds(len(environment_deaths) / len(death_events) if death_events else 0),
                "description": "Deaths from environmental effects (fire, void zones, etc.)"
            },
            "chain_deaths": {
                "total": len(chain_deaths),
                "patterns": self._analyze_chain_patterns(chain_deaths),
                "odds": calculate_american_odds(len(chain_deaths) / len(death_events) if death_events else 0),
                "description": "Deaths occurring in quick succession with other deaths"
            },
            "unavoidable_deaths": {
                "total": len(unavoidable_deaths),
                "details": self._summarize_unavoidable_deaths(unavoidable_deaths),
                "odds": calculate_american_odds(len(unavoidable_deaths) / len(death_events) if death_events else 0),
                "description": "Deaths from unavoidable raid damage or mechanics"
            }
        }

    def analyze_death_recovery(self, player_deaths: List[Dict]) -> Dict[str, Any]:
        """Analyze recovery patterns after deaths"""
        return {
            "battle_res_priority": self._calculate_bres_priority(player_deaths),
            "raid_impact": self._analyze_raid_impact(player_deaths),
            "wipe_correlation": self._calculate_wipe_correlation(player_deaths)
        }

    def _process_death_events(self, deaths: List[Dict]) -> List[DeathEvent]:
        """Convert raw death data into structured DeathEvent objects"""
        events = []
        for death in deaths:
            event = DeathEvent(
                timestamp=death.get('timestamp', 0),
                player_id=death.get('player', ''),
                fight_id=death.get('fight_id', ''),
                cause=death.get('cause', 'unknown'),
                ability_id=death.get('ability_id'),
                source_id=death.get('source_id'),
                phase=self._determine_fight_phase(death),
                raid_health=self._get_raid_health_at_death(death),
                related_deaths=self._find_related_deaths(death)
            )
            events.append(event)
        return events

    def _calculate_bres_priority(self, deaths: List[Dict]) -> Dict[str, Any]:
        """Calculate battle resurrection priority metrics"""
        total_bres = sum(1 for d in deaths if d.get('was_resurrected', False))
        
        return {
            "bres_received": {
                "total": total_bres,
                "percentage": total_bres / len(deaths) if deaths else 0,
                "odds": calculate_american_odds(total_bres / len(deaths) if deaths else 0),
                "description": "How often selected for battle resurrection"
            },
            "bres_timing": self._analyze_bres_timing(deaths),
            "bres_success_rate": self._calculate_bres_success(deaths)
        }

    def _analyze_raid_impact(self, deaths: List[Dict]) -> Dict[str, Any]:
        """Analyze how deaths impact raid performance"""
        wipes_after_death = 0
        recovery_kills = 0
        
        for death in deaths:
            fight_data = next((f for f in self.fights_data if f.get('id') == death.get('fight_id')), None)
            if fight_data:
                if not fight_data.get('kill', False):
                    wipes_after_death += 1
                elif death.get('timestamp', 0) < fight_data.get('endTime', 0):
                    recovery_kills += 1

        return {
            "wipe_rate": {
                "value": wipes_after_death / len(deaths) if deaths else 0,
                "odds": calculate_american_odds(wipes_after_death / len(deaths) if deaths else 0),
                "description": "Rate at which deaths lead to wipes"
            },
            "recovery_rate": {
                "value": recovery_kills / len(deaths) if deaths else 0,
                "odds": calculate_american_odds(recovery_kills / len(deaths) if deaths else 0),
                "description": "Rate at which raid recovers from deaths"
            }
        }

    def _calculate_wipe_correlation(self, deaths: List[Dict]) -> Dict[str, Any]:
        """Calculate correlation between deaths and wipes"""
        early_wipe_threshold = 30000  # 30 seconds
        critical_phase_deaths = 0
        
        for death in deaths:
            if self._is_critical_phase_death(death):
                critical_phase_deaths += 1

        return {
            "critical_phase_impact": {
                "value": critical_phase_deaths / len(deaths) if deaths else 0,
                "odds": calculate_american_odds(critical_phase_deaths / len(deaths) if deaths else 0),
                "description": "Impact of deaths during critical fight phases"
            }
        }

    # Continue from previous file...

    def _determine_fight_phase(self, death: Dict) -> Optional[int]:
        """Determine which phase of the fight the death occurred in"""
        fight = next((f for f in self.fights_data if f.get('id') == death.get('fight_id')), None)
        if not fight:
            return None
            
        death_time = death.get('timestamp', 0) - fight.get('startTime', 0)
        fight_duration = fight.get('endTime', 0) - fight.get('startTime', 0)
        
        # Phase thresholds based on boss health percentages or specific mechanics
        if 'phase_transitions' in self.boss_mechanics:
            for phase, threshold in enumerate(self.boss_mechanics['phase_transitions'], 1):
                if death_time <= threshold * fight_duration:
                    return phase
        
        # Default to time-based phases if no specific transitions defined
        if death_time < fight_duration * 0.3:
            return 1
        elif death_time < fight_duration * 0.7:
            return 2
        return 3

    def _get_raid_health_at_death(self, death: Dict) -> float:
        """Get the raid's average health percentage when death occurred"""
        fight = next((f for f in self.fights_data if f.get('id') == death.get('fight_id')), None)
        if not fight or 'raidHealth' not in fight:
            return 100.0
            
        death_time = death.get('timestamp', 0)
        health_entries = fight['raidHealth']
        
        # Find closest health entry to death time
        closest_entry = min(health_entries, 
                          key=lambda x: abs(x.get('timestamp', 0) - death_time))
        return closest_entry.get('percentage', 100.0)

    def _find_related_deaths(self, death: Dict, time_window: int = 5000) -> List[str]:
        """Find other deaths that occurred within time_window ms of this death"""
        death_time = death.get('timestamp', 0)
        fight = next((f for f in self.fights_data if f.get('id') == death.get('fight_id')), None)
        
        if not fight:
            return []
            
        related = []
        for other_death in fight.get('deaths', []):
            if (other_death.get('player') != death.get('player') and
                abs(other_death.get('timestamp', 0) - death_time) <= time_window):
                related.append(other_death.get('player'))
                
        return related

    def _is_critical_phase_death(self, death: Dict) -> bool:
        """Determine if death occurred during a critical fight phase"""
        fight = next((f for f in self.fights_data if f.get('id') == death.get('fight_id')), None)
        if not fight:
            return False
            
        # Check if death occurred during defined critical phases
        phase = self._determine_fight_phase(death)
        if phase in self.boss_mechanics.get('critical_phases', []):
            return True
            
        # Check if death occurred during low boss health
        boss_health = fight.get('bossHealth', 100)
        if boss_health <= 30:  # Consider sub-30% as critical
            return True
            
        return False

    def _analyze_bres_timing(self, deaths: List[Dict]) -> Dict[str, Any]:
        """Analyze timing and effectiveness of battle resurrections"""
        bres_timings = []
        
        for death in deaths:
            if death.get('was_resurrected', False):
                fight = next((f for f in self.fights_data if f.get('id') == death.get('fight_id')), None)
                if fight:
                    death_time = death.get('timestamp', 0) - fight.get('startTime', 0)
                    res_time = death.get('resurrection_time', 0) - fight.get('startTime', 0)
                    bres_timings.append({
                        'time_to_res': res_time - death_time,
                        'fight_phase': self._determine_fight_phase(death),
                        'was_successful': fight.get('kill', False)
                    })
        
        if not bres_timings:
            return {
                "average_time": 0,
                "phase_distribution": {},
                "success_rate": 0
            }
            
        return {
            "average_time": sum(t['time_to_res'] for t in bres_timings) / len(bres_timings),
            "phase_distribution": {
                phase: len([t for t in bres_timings if t['fight_phase'] == phase])
                for phase in set(t['fight_phase'] for t in bres_timings)
            },
            "success_rate": len([t for t in bres_timings if t['was_successful']]) / len(bres_timings)
        }

    def _calculate_bres_success(self, deaths: List[Dict]) -> Dict[str, Any]:
        """Calculate success rate of fights after battle resurrection"""
        bres_fights = set()
        successful_bres_fights = set()
        
        for death in deaths:
            if death.get('was_resurrected', False):
                fight_id = death.get('fight_id')
                bres_fights.add(fight_id)
                
                fight = next((f for f in self.fights_data if f.get('id') == fight_id), None)
                if fight and fight.get('kill', False):
                    successful_bres_fights.add(fight_id)
        
        success_rate = len(successful_bres_fights) / len(bres_fights) if bres_fights else 0
        
        return {
            "total_bres_fights": len(bres_fights),
            "successful_bres_fights": len(successful_bres_fights),
            "success_rate": success_rate,
            "odds": calculate_american_odds(success_rate)
        }
