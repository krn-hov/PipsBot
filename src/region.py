from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from enum import Enum

from .cell import Cell
from .condition import Condition

# ============================================================================
# Region - Represents a group of cells with a condition
# ============================================================================

@dataclass
class Region:
    """Represents a region (group of cells) with a constraint"""
    cells: List[Cell]
    condition: Condition
    region_id: int = 0
    
    def __post_init__(self):
        """Validate region"""
        if not self.cells:
            raise ValueError("Region must contain at least one cell")
    
    def contains_cell(self, cell: Cell) -> bool:
        """Check if this region contains the given cell"""
        return cell in self.cells
    
    def get_cell_count(self) -> int:
        """Return number of cells in this region"""
        return len(self.cells)
    
    def __repr__(self):
        return f"Region(id={self.region_id}, cells={len(self.cells)}, condition={self.condition})"
    
    def __str__(self):
        cell_str = ", ".join(str(c) for c in self.cells)
        return f"Region {self.region_id}: [{cell_str}] with {self.condition}"