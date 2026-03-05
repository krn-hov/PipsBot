from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from enum import Enum

# ============================================================================
# Cell - Represents a single position on the board
# ============================================================================

@dataclass(frozen=True)
class Cell:
    """Represents a single cell position on the grid"""
    row: int
    col: int
    
    def __repr__(self):
        return f"Cell({self.row}, {self.col})"
    
    def __str__(self):
        return f"({self.row},{self.col})"


