"""
NYT Pips Game - Core Data Structures
Clean class constructs to represent the game state
"""

from .cell import Cell
from .domino import Domino
from .conditionType import ConditionType
from .condition import Condition
from .region import Region
from .board import Board
from .game import Game


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Create a 4x4 game
    game = Game(4, 4)
    
    # Define regions
    region1 = Region(
        cells=[Cell(0, 0), Cell(0, 1), Cell(1, 0)],
        condition=Condition(ConditionType.SUM, 8),
        region_id=1
    )
    
    region2 = Region(
        cells=[Cell(0, 2), Cell(0, 3), Cell(1, 3)],
        condition=Condition(ConditionType.EQUAL),
        region_id=2
    )
    
    region3 = Region(
        cells=[Cell(1, 1), Cell(1, 2), Cell(2, 1), Cell(2, 2)],
        condition=Condition(ConditionType.LESS_THAN, 12),
        region_id=3
    )
    
    region4 = Region(
        cells=[Cell(2, 0), Cell(3, 0), Cell(3, 1)],
        condition=Condition(ConditionType.SUM, 6),
        region_id=4
    )
    
    region5 = Region(
        cells=[Cell(2, 3), Cell(3, 2), Cell(3, 3)],
        condition=Condition(ConditionType.GREATER_THAN, 8),
        region_id=5
    )
    
    # Add regions to game
    game.add_region(region1)
    game.add_region(region2)
    game.add_region(region3)
    game.add_region(region4)
    game.add_region(region5)
    
    # Add dominoes
    dominoes = [
        Domino(0, 1), Domino(1, 2), Domino(2, 3), Domino(3, 4),
        Domino(4, 5), Domino(5, 6), Domino(1, 1), Domino(2, 2)
    ]
    game.set_dominoes(dominoes)
    
    # Validate structure
    is_valid, message = game.validate_structure()
    print(f"Game valid: {is_valid} - {message}")
    print()
    
    # Display game
    print(game)
    
    # Test setting some values
    print("\n" + "=" * 40)
    print("Testing board operations:")
    game.board.set_value(Cell(0, 0), 3)
    game.board.set_value(Cell(0, 1), 2)
    game.board.set_value(Cell(1, 0), 3)
    print(game.board)
    
    # Check region 1 condition
    region1_values = [game.board.get_value(cell) for cell in region1.cells]
    print(f"\nRegion 1 values: {region1_values}")
    print(f"Region 1 condition ({region1.condition}): {region1.condition.check(region1_values)}")