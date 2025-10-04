"""
Pokemon Class for Pokemon Faiths
Implements the Veteran System with battle logging and descriptive states
"""

import time
import math
from collections import deque
from typing import List, Dict, Optional
from core.logger import get_logger

logger = get_logger('Pokemon')

class Pokemon:
    """
    Pokemon with Veteran System progression
    No traditional XP/leveling - growth based on battle history
    """

    # Battle log constants
    MAX_BATTLE_LOG_SIZE = 200
    RECENT_BATTLES_WEIGHT = 50  # Recent battles have primary influence

    # Injury thresholds
    INJURY_THRESHOLD_MINOR = 60  # Single hit damage threshold
    INJURY_THRESHOLD_MAJOR = 80
    INJURY_THRESHOLD_CATASTROPHIC = 95

    def __init__(self, species: str, nickname: str = None, age_years: int = 0):
        # Basic info
        self.species = species
        self.nickname = nickname or species
        self.age_years = age_years  # Age when caught (wild Pokemon can be 100+ years)
        self.pokeball_age = 0  # Years since capture (max 100 unless caught old)

        # Battle history (circular buffer)
        self.battle_log = deque(maxlen=self.MAX_BATTLE_LOG_SIZE)
        self.total_battles = 0

        # Permanent injuries (never decay)
        self.permanent_injuries = []

        # Special status
        self.has_vos = False  # Will of the Struggler
        self.prosthetics = []

        # Base stats (hidden from player, used for calculations)
        self.base_attack = 50
        self.base_defense = 50
        self.base_speed = 50

        # Current descriptive state (what player sees)
        self.current_hp_percent = 100  # Internal tracking only
        self.state_description = "Standing strong, ready for battle"
        self.is_alive = True
        self.is_conscious = True

        # Veteran System scores (calculated from battle log)
        self.combat_experience = 0
        self.adaptation_score = 0
        self.trauma_score = 0
        self.injury_severity = 0

        logger.debug(f"Created Pokemon: {self.nickname} ({self.species}), Age: {self.age_years}")

    def get_descriptive_state(self) -> str:
        """
        Return text description of Pokemon's state instead of HP bar
        This is what the player sees - NO NUMBERS
        """
        if not self.is_alive:
            return "Lifeless... they won't get back up"

        if not self.is_conscious:
            return "Unconscious, barely breathing"

        hp = self.current_hp_percent

        # Determine state based on HP percentage
        if hp >= 90:
            descriptions = [
                "Standing strong, ready for battle",
                "Focused and alert",
                "Breathing steadily, no visible damage"
            ]
        elif hp >= 70:
            descriptions = [
                "Standing strong but breathing hard",
                "A few scratches visible, still determined",
                "Shaking off the hits, still in the fight"
            ]
        elif hp >= 50:
            descriptions = [
                "Favoring one side, visibly hurt",
                "Breathing heavily, blood visible",
                "Struggling but refuses to back down"
            ]
        elif hp >= 30:
            descriptions = [
                "Staggered — switch window opens",
                "Limping badly, barely standing",
                "Eyes unfocused, swaying dangerously"
            ]
        elif hp >= 10:
            descriptions = [
                "On the brink of collapse",
                "One more hit could end this",
                "Clinging to consciousness by sheer will"
            ]
        else:
            descriptions = [
                "About to fall — retreat NOW",
                "Can barely stand, death looms close",
                "Critical — any attack could be fatal"
            ]

        # Add injury modifiers
        injury_notes = self._get_injury_descriptions()
        if injury_notes:
            return f"{descriptions[0]} — {injury_notes}"

        return descriptions[0]

    def _get_injury_descriptions(self) -> str:
        """Get text description of permanent injuries"""
        if not self.permanent_injuries:
            return ""

        injury_texts = []
        for injury in self.permanent_injuries:
            injury_type = injury['type']
            if injury_type == 'deep_scar':
                injury_texts.append("bears deep scars")
            elif injury_type == 'burn_scar':
                injury_texts.append("skin scorched and scarred")
            elif injury_type == 'lost_eye':
                injury_texts.append("one eye clouded and useless")
            elif injury_type == 'broken_limb':
                injury_texts.append("limb crooked from old break")
            elif injury_type == 'lost_limb':
                injury_texts.append("missing a limb")
            elif injury_type == 'emotional_trauma':
                injury_texts.append("eyes haunted by past horrors")

        return ", ".join(injury_texts)

    def add_battle_entry(self, entry: Dict):
        """
        Add entry to battle log (circular buffer)
        Entry format defined in design doc Section 7
        """
        entry['timestamp'] = time.time()
        entry['battle_index'] = self.total_battles
        self.battle_log.append(entry)
        self.total_battles += 1

        # Recalculate veteran scores after each battle
        self.calculate_veteran_score()

        logger.info(f"{self.nickname} battle log updated: {entry['outcome']}")

    def calculate_veteran_score(self):
        """
        Calculate veteran scores from battle log with exponential decay
        Recent battles (last ~50) have primary influence
        Formula: EffectiveVeteranScore = f(CombatExp, Adaptation) - g(Trauma, InjurySeverity)
        """
        if not self.battle_log:
            return

        combat_exp = 0
        adaptation = 0
        trauma = 0

        total_entries = len(self.battle_log)

        for i, entry in enumerate(self.battle_log):
            # Calculate decay weight (recent battles weighted more heavily)
            battles_ago = total_entries - i - 1
            if battles_ago < self.RECENT_BATTLES_WEIGHT:
                weight = 1.0  # Recent battles at full weight
            else:
                # Exponential decay for older battles
                decay_distance = battles_ago - self.RECENT_BATTLES_WEIGHT
                weight = math.exp(-decay_distance / 50.0)  # Decay over ~50 battles

            # Combat Experience factors
            if entry['outcome'] == 'win':
                combat_exp += 10 * weight
            elif entry['outcome'] == 'retreat':
                combat_exp += 3 * weight  # Survival is learning
            elif entry['outcome'] == 'faint':
                combat_exp += 1 * weight  # Still learned something

            # Bonus for varied tactics
            tactics = entry.get('player_tactics', [])
            combat_exp += len(set(tactics)) * 2 * weight

            # Bonus for fighting strong opponents
            opponent_veterancy = entry.get('opponent_veterancy', 1.0)
            combat_exp += (opponent_veterancy - 1.0) * 5 * weight

            # Adaptation Score
            moves_used = entry.get('moves_used', [])
            effective_moves = sum(1 for m in moves_used if m.get('effective', False))
            adaptation += effective_moves * 3 * weight

            # Trauma Score
            damage_taken = entry.get('damage_taken', {}).get('amount', 0)
            trauma += damage_taken * 0.5 * weight

            if entry['outcome'] == 'killed':
                trauma += 100 * weight  # Death trauma (theoretical - Pokemon is dead)
            elif entry['outcome'] == 'faint':
                trauma += 15 * weight

            # Status events contribute to trauma
            status_events = entry.get('status_events', [])
            for event in status_events:
                if event in ['limb_lost', 'blinded']:
                    trauma += 30 * weight
                elif event == 'stagger':
                    trauma += 5 * weight

        # Calculate injury severity from permanent injuries
        injury_severity = 0
        for injury in self.permanent_injuries:
            severity = injury.get('severity', 'minor')
            if severity == 'catastrophic':
                injury_severity += 50
            elif severity == 'major':
                injury_severity += 20
            elif severity == 'minor':
                injury_severity += 5

        # Store calculated scores
        self.combat_experience = max(0, combat_exp)
        self.adaptation_score = max(0, adaptation)
        self.trauma_score = max(0, trauma)
        self.injury_severity = injury_severity

        logger.debug(f"{self.nickname} Veteran Scores - Combat: {self.combat_experience:.1f}, "
                    f"Adaptation: {self.adaptation_score:.1f}, Trauma: {self.trauma_score:.1f}, "
                    f"Injuries: {self.injury_severity}")

    def get_effective_veteran_score(self) -> float:
        """
        Calculate net veteran score
        Returns overall effectiveness rating
        """
        positive = self.combat_experience + self.adaptation_score
        negative = self.trauma_score + self.injury_severity
        return positive - negative

    def check_for_injury(self, damage_amount: float, damage_type: str,
                        body_location: str) -> Optional[Dict]:
        """
        Check if damage should trigger a permanent injury
        Returns injury data if triggered, None otherwise
        """
        # Don't injure dead Pokemon
        if not self.is_alive:
            return None

        # VoS holders largely bypass injury
        if self.has_vos:
            # 90% injury resistance for VoS
            import random
            if random.random() < 0.9:
                logger.info(f"{self.nickname} (VoS) resisted potential injury")
                return None

        injury = None

        # Check for catastrophic injury
        if damage_amount >= self.INJURY_THRESHOLD_CATASTROPHIC:
            injury = {
                'type': 'lost_limb',
                'severity': 'catastrophic',
                'location': body_location,
                'timestamp': time.time(),
                'description': f"Lost {body_location} to catastrophic damage"
            }
        # Check for major injury
        elif damage_amount >= self.INJURY_THRESHOLD_MAJOR:
            # Determine injury type based on damage type
            if damage_type == 'fire':
                injury_type = 'burn_scar'
            elif damage_type == 'physical':
                injury_type = 'deep_scar'
            else:
                injury_type = 'deep_scar'

            injury = {
                'type': injury_type,
                'severity': 'major',
                'location': body_location,
                'timestamp': time.time(),
                'description': self._get_injury_description(injury_type, body_location)
            }

        if injury:
            self.permanent_injuries.append(injury)
            self.calculate_veteran_score()  # Recalculate with new injury
            logger.warning(f"{self.nickname} suffered {injury['severity']} injury: {injury['type']}")

        return injury

    def _get_injury_description(self, injury_type: str, location: str) -> str:
        """Get narrative description of injury"""
        descriptions = {
            'deep_scar': f"Deep scar across {location} — a permanent reminder of near-death",
            'burn_scar': f"Scorched tissue on {location} — the fire's mark remains",
            'lost_eye': f"Eye destroyed — vision gone but instincts sharpen",
            'broken_limb': f"Fractured {location} — movement forever altered",
            'lost_limb': f"{location} severed — they will never be the same",
            'emotional_trauma': f"Something broke inside — the haunted look won't fade"
        }
        return descriptions.get(injury_type, f"Injury to {location}")

    def apply_injury_modifiers(self) -> Dict[str, float]:
        """
        Calculate stat modifiers from permanent injuries
        Returns dict of stat changes
        """
        modifiers = {
            'attack': 0,
            'defense': 0,
            'speed': 0,
            'accuracy': 0,
            'evasion': 0
        }

        for injury in self.permanent_injuries:
            injury_type = injury['type']

            if injury_type == 'deep_scar':
                modifiers['attack'] += 5  # Hardened by pain
                modifiers['speed'] -= 3   # Stiffness
            elif injury_type == 'burn_scar':
                modifiers['attack'] += 3  # Rage
                modifiers['defense'] -= 5  # Damaged tissue
            elif injury_type == 'lost_eye':
                modifiers['evasion'] += 5  # Heightened senses
                modifiers['accuracy'] -= 8  # Depth perception lost
            elif injury_type == 'lost_limb':
                modifiers['speed'] -= 15  # Severe mobility loss
                modifiers['defense'] -= 10

        return modifiers

    def take_damage(self, amount: float, damage_type: str = 'physical',
                   location: str = 'body') -> Dict:
        """
        Apply damage to Pokemon
        Returns dict with damage result info for battle log
        """
        # Apply damage
        self.current_hp_percent = max(0, self.current_hp_percent - amount)

        # Update state
        self.state_description = self.get_descriptive_state()

        # Check for injuries
        injury = self.check_for_injury(amount, damage_type, location)

        # Check for death/faint
        if self.current_hp_percent <= 0:
            # Determine if faint or death (deaths only on massive overkill or player ignoring warnings)
            if amount >= 50 and self.current_hp_percent <= -10:
                self.is_alive = False
                self.is_conscious = False
                self.state_description = "Lifeless... they won't get back up"
                logger.warning(f"{self.nickname} has died in battle")
            else:
                self.is_conscious = False
                self.state_description = "Unconscious, barely breathing"
                logger.info(f"{self.nickname} fainted")

        return {
            'damage_amount': amount,
            'damage_type': damage_type,
            'location': location,
            'injury': injury,
            'new_state': self.state_description
        }

    def heal(self, amount: float):
        """Heal Pokemon (items, rest, etc.)"""
        if not self.is_alive:
            logger.warning(f"Cannot heal {self.nickname} - they are dead")
            return

        self.current_hp_percent = min(100, self.current_hp_percent + amount)

        if self.current_hp_percent > 0:
            self.is_conscious = True

        self.state_description = self.get_descriptive_state()
        logger.info(f"{self.nickname} healed")

    def __str__(self):
        """String representation"""
        status = "Dead" if not self.is_alive else ("Fainted" if not self.is_conscious else "Active")
        return f"{self.nickname} ({self.species}) - {status} - Battles: {self.total_battles}"
