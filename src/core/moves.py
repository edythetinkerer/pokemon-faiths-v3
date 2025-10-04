"""
Move System for Pokemon Faiths
Moves affect descriptive states, not visible HP numbers
"""

import random
from typing import Dict, List
from core.logger import get_logger

logger = get_logger('Moves')

class Move:
    """
    Represents a Pokemon move
    Damage is hidden from player - they see descriptive results instead
    """

    def __init__(self, name: str, move_type: str, category: str,
                 base_power: int, accuracy: float = 1.0,
                 description: str = ""):
        self.name = name
        self.move_type = move_type  # fire, water, physical, etc.
        self.category = category    # 'physical', 'special', 'status'
        self.base_power = base_power  # Hidden from player
        self.accuracy = accuracy
        self.description = description

        # Narrative feedback for hits
        self.hit_descriptions = [
            f"A solid {name}!",
            f"{name} connects!",
            f"The {name} strikes true!"
        ]

        self.miss_descriptions = [
            f"The {name} misses!",
            f"{name} goes wide!",
            f"They dodge the {name}!"
        ]

    def calculate_damage(self, attacker_stat: int, defender_stat: int,
                        type_effectiveness: float = 1.0) -> float:
        """
        Calculate damage amount (hidden from player)
        Returns damage as percentage of HP
        """
        if self.category == 'status':
            return 0

        # Base damage calculation
        damage = (self.base_power * (attacker_stat / defender_stat) * 0.4)

        # Type effectiveness multiplier
        damage *= type_effectiveness

        # Random variance (0.85 to 1.0)
        damage *= random.uniform(0.85, 1.0)

        return damage

    def get_effectiveness_description(self, effectiveness: float) -> str:
        """
        Convert type effectiveness to narrative description
        NO NUMBERS shown to player
        """
        if effectiveness >= 2.0:
            return "It's devastatingly effective!"
        elif effectiveness >= 1.5:
            return "It's very effective!"
        elif effectiveness == 1.0:
            return ""
        elif effectiveness >= 0.5:
            return "It doesn't seem very effective..."
        else:
            return "It barely has any effect..."

    def execute(self, attacker, defender, type_chart) -> Dict:
        """
        Execute the move in battle
        Returns dict with narrative results (no numbers shown to player)
        """
        result = {
            'move_name': self.name,
            'hit': False,
            'effectiveness': 1.0,
            'damage': 0,
            'narrative': "",
            'descriptive_result': ""
        }

        # Check for hit
        hit_roll = random.random()
        if hit_roll > self.accuracy:
            result['narrative'] = random.choice(self.miss_descriptions)
            result['descriptive_result'] = "The attack missed!"
            return result

        result['hit'] = True

        # Calculate type effectiveness
        effectiveness = type_chart.get_effectiveness(self.move_type,
                                                    defender.species)
        result['effectiveness'] = effectiveness

        # Calculate damage (hidden from player)
        if self.category == 'physical':
            attacker_stat = attacker.base_attack
            defender_stat = defender.base_defense
        elif self.category == 'special':
            attacker_stat = attacker.base_attack  # Simplified for now
            defender_stat = defender.base_defense
        else:
            attacker_stat = 50
            defender_stat = 50

        damage = self.calculate_damage(attacker_stat, defender_stat, effectiveness)
        result['damage'] = damage

        # Apply damage to defender
        damage_result = defender.take_damage(damage, self.move_type, 'body')

        # Build narrative description (what player sees)
        narrative = random.choice(self.hit_descriptions)
        effectiveness_text = self.get_effectiveness_description(effectiveness)

        if effectiveness_text:
            narrative += f" {effectiveness_text}"

        result['narrative'] = narrative
        result['descriptive_result'] = damage_result['new_state']

        # Note if injury occurred
        if damage_result.get('injury'):
            injury = damage_result['injury']
            result['injury_occurred'] = True
            result['injury_description'] = injury['description']
            logger.warning(f"Move {self.name} caused injury: {injury['type']}")

        return result

    def __str__(self):
        return f"{self.name} ({self.move_type})"


class MoveDatabase:
    """
    Central repository of all moves
    Start with basic moves, expand later
    """

    def __init__(self):
        self.moves = {}
        self._initialize_basic_moves()

    def _initialize_basic_moves(self):
        """Initialize starter move set"""

        # Physical moves
        self.add_move(Move(
            name="Tackle",
            move_type="normal",
            category="physical",
            base_power=40,
            accuracy=0.95,
            description="A straightforward physical attack"
        ))

        self.add_move(Move(
            name="Scratch",
            move_type="normal",
            category="physical",
            base_power=35,
            accuracy=1.0,
            description="Rakes claws across the opponent"
        ))

        self.add_move(Move(
            name="Bite",
            move_type="dark",
            category="physical",
            base_power=60,
            accuracy=0.90,
            description="Vicious bite that can cause flinching"
        ))

        # Special moves
        self.add_move(Move(
            name="Ember",
            move_type="fire",
            category="special",
            base_power=40,
            accuracy=0.95,
            description="Small flames that can burn"
        ))

        self.add_move(Move(
            name="Water Gun",
            move_type="water",
            category="special",
            base_power=40,
            accuracy=0.95,
            description="Sprays water at the opponent"
        ))

        # Strong moves (for veteran Pokemon)
        self.add_move(Move(
            name="Body Slam",
            move_type="normal",
            category="physical",
            base_power=85,
            accuracy=0.85,
            description="Full-body tackle with tremendous force"
        ))

        self.add_move(Move(
            name="Flamethrower",
            move_type="fire",
            category="special",
            base_power=90,
            accuracy=0.90,
            description="Intense flames that can severely burn"
        ))

        logger.info(f"Move database initialized with {len(self.moves)} moves")

    def add_move(self, move: Move):
        """Add a move to the database"""
        self.moves[move.name.lower()] = move

    def get_move(self, name: str) -> Move:
        """Get a move by name"""
        return self.moves.get(name.lower())

    def get_random_moves(self, count: int = 4) -> List[Move]:
        """Get random moves for a Pokemon"""
        move_list = list(self.moves.values())
        if len(move_list) <= count:
            return move_list
        return random.sample(move_list, count)


class TypeChart:
    """
    Type effectiveness chart
    Simplified for initial implementation
    """

    def __init__(self):
        # Type effectiveness multipliers
        # Format: effectiveness[move_type][defender_type] = multiplier
        self.effectiveness = {
            'normal': {
                'default': 1.0
            },
            'fire': {
                'grass': 2.0,
                'water': 0.5,
                'fire': 0.5,
                'default': 1.0
            },
            'water': {
                'fire': 2.0,
                'grass': 0.5,
                'water': 0.5,
                'default': 1.0
            },
            'grass': {
                'water': 2.0,
                'fire': 0.5,
                'grass': 0.5,
                'default': 1.0
            },
            'dark': {
                'psychic': 2.0,
                'dark': 0.5,
                'default': 1.0
            }
        }

    def get_effectiveness(self, move_type: str, defender_species: str) -> float:
        """
        Get type effectiveness multiplier
        For now, simplified - just use move type vs defender type
        """
        # TODO: Map species to types (for now use simple mapping)
        defender_type = self._get_species_type(defender_species)

        if move_type not in self.effectiveness:
            return 1.0

        type_matchups = self.effectiveness[move_type]
        return type_matchups.get(defender_type, type_matchups.get('default', 1.0))

    def _get_species_type(self, species: str) -> str:
        """
        Map species to primary type
        Temporary simple mapping - expand later
        """
        species_lower = species.lower()

        if 'fire' in species_lower or species_lower in ['charmander', 'vulpix']:
            return 'fire'
        elif 'water' in species_lower or species_lower in ['squirtle', 'psyduck']:
            return 'water'
        elif 'grass' in species_lower or species_lower in ['bulbasaur', 'oddish']:
            return 'grass'
        else:
            return 'normal'


# Global instances
_move_database = None
_type_chart = None


def get_move_database() -> MoveDatabase:
    """Get global move database instance"""
    global _move_database
    if _move_database is None:
        _move_database = MoveDatabase()
    return _move_database


def get_type_chart() -> TypeChart:
    """Get global type chart instance"""
    global _type_chart
    if _type_chart is None:
        _type_chart = TypeChart()
    return _type_chart
