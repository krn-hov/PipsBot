from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from enum import Enum

from .conditionType import ConditionType

# ============================================================================
# Condition - Represents a constraint on a region
# ============================================================================

@dataclass
class Condition:
    """Represents a constraint that must be satisfied by a region"""
    condition_type: ConditionType
    target_value: Optional[int] = None  # Used for SUM, LESS_THAN, GREATER_THAN
    
    def __post_init__(self):
        """Validate condition parameters"""
        needs_value = {ConditionType.SUM, ConditionType.LESS_THAN, ConditionType.GREATER_THAN}
        
        if self.condition_type in needs_value and self.target_value is None:
            raise ValueError(f"{self.condition_type.value} condition requires a target_value")
        
        if self.condition_type not in needs_value and self.target_value is not None:
            raise ValueError(f"{self.condition_type.value} condition should not have a target_value")
    
    def check(self, values: List[int]) -> bool:
        """
        Check if the given values satisfy this condition
        
        Args:
            values: List of pip values in the region
            
        Returns:
            True if condition is satisfied, False otherwise
        """
        if not values:
            return True  # Empty region trivially satisfies any condition
        
        if self.condition_type == ConditionType.EQUAL:
            return len(set(values)) == 1  # All values the same
        
        elif self.condition_type == ConditionType.NOT_EQUAL:
            return len(set(values)) == len(values)  # All values unique
        
        elif self.condition_type == ConditionType.SUM:
            return sum(values) == self.target_value
        
        elif self.condition_type == ConditionType.LESS_THAN:
            return sum(values) < self.target_value
        
        elif self.condition_type == ConditionType.GREATER_THAN:
            return sum(values) > self.target_value
        
        return False
    
    def can_satisfy(self, values: List[int], remaining_cells: int) -> bool:
        """
        Check if partial values could potentially satisfy this condition
        Used during solving to prune invalid branches early
        
        Args:
            values: Current values in the region
            remaining_cells: Number of empty cells in the region
            
        Returns:
            True if condition could still be satisfied, False if impossible
        """
        if not values:
            return True
        
        current_sum = sum(values)
        
        if self.condition_type == ConditionType.EQUAL:
            # All current values must be the same
            return len(set(values)) == 1
        
        elif self.condition_type == ConditionType.NOT_EQUAL:
            # No duplicates allowed
            return len(set(values)) == len(values)
        
        elif self.condition_type == ConditionType.SUM:
            # Check if we can still reach target
            min_possible = current_sum + (remaining_cells * 0)  # Add all 0s
            max_possible = current_sum + (remaining_cells * 6)  # Add all 6s
            return min_possible <= self.target_value <= max_possible
        
        elif self.condition_type == ConditionType.LESS_THAN:
            # Even with all 0s, must stay below target
            return current_sum < self.target_value
        
        elif self.condition_type == ConditionType.GREATER_THAN:
            # With all 6s, must be able to exceed target
            max_possible = current_sum + (remaining_cells * 6)
            return max_possible > self.target_value
        
        return True
    
    def __repr__(self):
        if self.target_value is not None:
            return f"Condition({self.condition_type.value}, {self.target_value})"
        return f"Condition({self.condition_type.value})"
    
    def __str__(self):
        """Return human-readable condition string"""
        if self.condition_type == ConditionType.EQUAL:
            return "="
        elif self.condition_type == ConditionType.NOT_EQUAL:
            return "≠"
        elif self.condition_type == ConditionType.SUM:
            return f"= {self.target_value}"
        elif self.condition_type == ConditionType.LESS_THAN:
            return f"< {self.target_value}"
        elif self.condition_type == ConditionType.GREATER_THAN:
            return f"> {self.target_value}"
        return "?"