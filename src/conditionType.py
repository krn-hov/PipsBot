from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from enum import Enum

# ============================================================================
# ConditionType - Enum for different constraint types
# ============================================================================

class ConditionType(Enum):
    """Types of conditions that can apply to regions"""
    EQUAL = "equal"              # All values must be equal
    NOT_EQUAL = "not_equal"      # All values must be different
    SUM = "sum"                  # Sum must equal target value
    LESS_THAN = "less_than"      # Sum must be less than target
    GREATER_THAN = "greater_than" # Sum must be greater than target