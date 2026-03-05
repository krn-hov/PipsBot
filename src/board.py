from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from enum import Enum

from .cell import Cell

# ============================================================================
# Board - Represents the game board state
# ============================================================================

class Board:
    """Represents the Pips game board"""
    
    def __init__(self, rows: int, cols: int):
        """
        Initialize an empty board
        
        Args:
            rows: Number of rows
            cols: Number of columns
        """
        if rows < 1 or cols < 1:
            raise ValueError("Board must have at least 1 row and 1 column")
        
        self.rows = rows
        self.cols = cols
        # Grid stores pip values (0-6) or None for empty cells
        self.grid: List[List[Optional[int]]] = [[None] * cols for _ in range(rows)]
    
    def is_valid_cell(self, cell: Cell) -> bool:
        """Check if cell is within board bounds"""
        return 0 <= cell.row < self.rows and 0 <= cell.col < self.cols
    
    def get_value(self, cell: Cell) -> Optional[int]:
        """Get the value at a cell (or None if empty)"""
        if not self.is_valid_cell(cell):
            raise ValueError(f"Cell {cell} is out of bounds")
        return self.grid[cell.row][cell.col]
    
    def set_value(self, cell: Cell, value: int):
        """Set the value at a cell"""
        if not self.is_valid_cell(cell):
            raise ValueError(f"Cell {cell} is out of bounds")
        if not (0 <= value <= 6):
            raise ValueError(f"Value must be between 0 and 6, got {value}")
        self.grid[cell.row][cell.col] = value
    
    def clear_cell(self, cell: Cell):
        """Clear a cell (set to None)"""
        if not self.is_valid_cell(cell):
            raise ValueError(f"Cell {cell} is out of bounds")
        self.grid[cell.row][cell.col] = None
    
    def is_empty(self, cell: Cell) -> bool:
        """Check if a cell is empty"""
        return self.get_value(cell) is None
    
    def is_full(self) -> bool:
        """Check if all cells are filled"""
        for row in self.grid:
            if None in row:
                return False
        return True
    
    def get_empty_cells(self) -> List[Cell]:
        """Return list of all empty cells"""
        empty = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] is None:
                    empty.append(Cell(r, c))
        return empty
    
    def copy(self) -> 'Board':
        """Create a deep copy of this board"""
        new_board = Board(self.rows, self.cols)
        for r in range(self.rows):
            for c in range(self.cols):
                new_board.grid[r][c] = self.grid[r][c]
        return new_board
    
    def __repr__(self):
        return f"Board({self.rows}x{self.cols})"
    
    def __str__(self):
        """Return a visual representation of the board"""
        lines = []
        for row in self.grid:
            line = " ".join(str(v) if v is not None else "." for v in row)
            lines.append(line)
        return "\n".join(lines)