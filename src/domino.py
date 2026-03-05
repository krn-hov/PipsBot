from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from enum import Enum


# ============================================================================
# Domino - Represents a domino piece with two values
# ============================================================================

@dataclass
class Domino:
    """Represents a domino piece with two pip values"""
    value1: int  # First value (0-6)
    value2: int  # Second value (0-6)
    
    def __post_init__(self):
        """Validate domino values"""
        if not (0 <= self.value1 <= 6 and 0 <= self.value2 <= 6):
            raise ValueError("Domino values must be between 0 and 6")
    
    def total(self) -> int:
        """Return sum of both values"""
        return self.value1 + self.value2
    
    def get_values(self) -> Tuple[int, int]:
        """Return both values as tuple"""
        return (self.value1, self.value2)
    
    def flip(self) -> 'Domino':
        """Return a new domino with flipped values"""
        return Domino(self.value2, self.value1)
    
    def __repr__(self):
        return f"Domino({self.value1}, {self.value2})"
    
    def __str__(self):
        return f"[{self.value1}|{self.value2}]"
    
    def __eq__(self, other):
        if not isinstance(other, Domino):
            return False
        # Dominoes are equal if values match in either orientation
        return (self.value1 == other.value1 and self.value2 == other.value2) or \
               (self.value1 == other.value2 and self.value2 == other.value1)
    
    def __hash__(self):
        # Hash based on sorted values for consistent hashing
        return hash(tuple(sorted([self.value1, self.value2])))