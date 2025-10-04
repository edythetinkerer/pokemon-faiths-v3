#!/usr/bin/env python3
"""
Test script for battle system and veteran mechanics
Tests the vertical slice: Pokemon creation → Battle → Injury → Battle Log
"""

import sys
from core.pokemon import Pokemon
from core.moves import get_move_database, get_type_chart

def test_pokemon_creation():
    """Test Pokemon creation with descriptive states"""
    print("=== Testing Pokemon Creation ===")
    pokemon = Pokemon(species="Charmander", nickname="Blaze", age_years=1)
    print(f"Created: {pokemon}")
    print(f"State: {pokemon.get_descriptive_state()}")
    print(f"Veteran Score: {pokemon.get_effective_veteran_score()}")
    print()
    return pokemon

def test_moves():
    """Test move database"""
    print("=== Testing Move System ===")
    move_db = get_move_database()
    print(f"Loaded {len(move_db.moves)} moves")

    tackle = move_db.get_move("tackle")
    print(f"Move: {tackle.name}, Type: {tackle.move_type}, Power: {tackle.base_power}")
    print()

def test_battle_simulation():
    """Simulate a battle without pygame"""
    print("=== Testing Battle Simulation ===")

    # Create combatants
    player_pokemon = Pokemon(species="Charmander", nickname="Blaze", age_years=1)
    enemy_pokemon = Pokemon(species="Rattata", nickname="Wild Rat", age_years=2)

    move_db = get_move_database()
    type_chart = get_type_chart()

    print(f"Player: {player_pokemon.nickname} - {player_pokemon.get_descriptive_state()}")
    print(f"Enemy: {enemy_pokemon.nickname} - {enemy_pokemon.get_descriptive_state()}")
    print()

    # Simulate 3 rounds of combat
    tackle = move_db.get_move("tackle")
    bite = move_db.get_move("bite")

    for round_num in range(1, 4):
        print(f"--- Round {round_num} ---")

        # Player attacks
        result = tackle.execute(player_pokemon, enemy_pokemon, type_chart)
        print(f"Player uses {tackle.name}: {result['narrative']}")
        print(f"Enemy state: {enemy_pokemon.get_descriptive_state()}")

        if not enemy_pokemon.is_conscious:
            print("Enemy defeated!")
            break

        # Enemy attacks
        result = bite.execute(enemy_pokemon, player_pokemon, type_chart)
        print(f"Enemy uses {bite.name}: {result['narrative']}")
        print(f"Player state: {player_pokemon.get_descriptive_state()}")

        # Check for injury
        if result.get('injury_occurred'):
            print(f"INJURY! {result['injury_description']}")

        if not player_pokemon.is_conscious:
            print("Player defeated!")
            break

        print()

    return player_pokemon, enemy_pokemon

def test_battle_log():
    """Test battle logging system"""
    print("\n=== Testing Battle Log System ===")

    pokemon = Pokemon(species="Charmander", nickname="Blaze", age_years=1)

    # Simulate several battles
    battle_outcomes = ['win', 'win', 'retreat', 'faint', 'win']

    for i, outcome in enumerate(battle_outcomes):
        log_entry = {
            'opponent_id': f'Enemy_{i}',
            'opponent_veterancy': 1.0 + (i * 0.2),
            'moves_used': [
                {'move': 'Tackle', 'effective': True},
                {'move': 'Ember', 'effective': False}
            ],
            'damage_taken': {
                'amount': 15.0 + (i * 5),
                'type': 'physical',
                'location': 'body'
            },
            'damage_dealt': 30.0 + (i * 3),
            'status_events': [],
            'outcome': outcome,
            'player_tactics': ['aggressive'],
            'environment': ['forest']
        }

        pokemon.add_battle_entry(log_entry)
        print(f"Battle {i+1}: {outcome} - Veteran Score: {pokemon.get_effective_veteran_score():.1f}")

    print(f"\nTotal battles: {pokemon.total_battles}")
    print(f"Combat Experience: {pokemon.combat_experience:.1f}")
    print(f"Adaptation Score: {pokemon.adaptation_score:.1f}")
    print(f"Trauma Score: {pokemon.trauma_score:.1f}")
    print(f"Final Veteran Score: {pokemon.get_effective_veteran_score():.1f}")

def test_injury_system():
    """Test injury triggering and effects"""
    print("\n=== Testing Injury System ===")

    pokemon = Pokemon(species="Charmander", nickname="Blaze", age_years=1)
    print(f"Initial state: {pokemon.get_descriptive_state()}")

    # Take moderate damage (should not injure)
    print("\n1. Moderate damage (50):")
    result = pokemon.take_damage(50, 'physical', 'body')
    print(f"State: {pokemon.get_descriptive_state()}")
    print(f"Injuries: {len(pokemon.permanent_injuries)}")

    # Take major damage (should trigger injury)
    print("\n2. Major damage (85):")
    result = pokemon.take_damage(85, 'fire', 'left_leg')
    print(f"State: {pokemon.get_descriptive_state()}")
    if result.get('injury'):
        print(f"INJURY TRIGGERED: {result['injury']['type']} - {result['injury']['description']}")
    print(f"Total injuries: {len(pokemon.permanent_injuries)}")

    # Check injury modifiers
    modifiers = pokemon.apply_injury_modifiers()
    print(f"\nStat modifiers from injuries:")
    for stat, value in modifiers.items():
        if value != 0:
            print(f"  {stat}: {value:+d}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("POKEMON FAITHS - BATTLE SYSTEM TEST")
    print("=" * 60)
    print()

    try:
        test_pokemon_creation()
        test_moves()
        player, enemy = test_battle_simulation()
        test_battle_log()
        test_injury_system()

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n!!! TEST FAILED !!!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
