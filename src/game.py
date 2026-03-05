from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from enum import Enum

from .board import Board
from .region import Region
from .domino import Domino
from .cell import Cell

# ============================================================================
# Game - Represents the complete Pips puzzle
# ============================================================================

class Game:
    """Represents a complete Pips puzzle game"""
    
    def __init__(self, rows: int, cols: int):
        """
        Initialize a new game
        
        Args:
            rows: Board height
            cols: Board width
        """
        self.board = Board(rows, cols)
        self.regions: List[Region] = []
        self.available_dominoes: List[Domino] = []
        self._cell_to_region: dict[Cell, Region] = {}
    
    def add_region(self, region: Region):
        """Add a region to the game"""
        # Validate that cells don't overlap with existing regions
        for cell in region.cells:
            if not self.board.is_valid_cell(cell):
                raise ValueError(f"Cell {cell} is out of board bounds")
            if cell in self._cell_to_region:
                raise ValueError(f"Cell {cell} already belongs to region {self._cell_to_region[cell].region_id}")
        
        self.regions.append(region)
        for cell in region.cells:
            self._cell_to_region[cell] = region
    
    def get_region_for_cell(self, cell: Cell) -> Optional[Region]:
        """Get the region that contains this cell"""
        return self._cell_to_region.get(cell)
    
    def set_dominoes(self, dominoes: List[Domino]):
        """Set the available dominoes for this game"""
        self.available_dominoes = dominoes.copy()
    
    def validate_structure(self) -> Tuple[bool, str]:
        """
        Validate that the game structure is correct
        
        Returns:
            (is_valid, error_message)
        """
        total_cells = self.board.rows * self.board.cols
        
        # Check that all cells belong to a region
        region_cells = sum(len(r.cells) for r in self.regions)
        if region_cells != total_cells:
            return False, f"Not all cells are assigned to regions ({region_cells}/{total_cells})"
        
        # Check that we have the right number of dominoes
        expected_dominoes = total_cells // 2
        if len(self.available_dominoes) != expected_dominoes:
            return False, f"Wrong number of dominoes ({len(self.available_dominoes)}/{expected_dominoes})"
        
        return True, "Game structure is valid"
    
    def check_all_conditions(self) -> bool:
        """
        Check if all region conditions are satisfied with current board state
        
        Returns:
            True if all conditions satisfied, False otherwise
        """
        for region in self.regions:
            values = []
            for cell in region.cells:
                val = self.board.get_value(cell)
                if val is None:
                    return False  # Board not complete
                values.append(val)
            
            if not region.condition.check(values):
                return False
        
        return True
    
    def __repr__(self):
        return f"Game({self.board.rows}x{self.board.cols}, {len(self.regions)} regions, {len(self.available_dominoes)} dominoes)"
    
    def __str__(self):
        """Return detailed game state"""
        lines = [
            f"Pips Game - {self.board.rows}x{self.board.cols}",
            "=" * 40,
            "Board:",
            str(self.board),
            "",
            f"Regions ({len(self.regions)}):"
        ]
        for region in self.regions:
            lines.append(f"  {region}")
        
        lines.append("")
        lines.append(f"Available Dominoes ({len(self.available_dominoes)}):")
        lines.append("  " + ", ".join(str(d) for d in self.available_dominoes))
        
        return "\n".join(lines)