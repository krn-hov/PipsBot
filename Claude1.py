"""
NYT Pips Solver with Image Parsing
Simplified version for well-formatted screenshots
"""

import cv2
import numpy as np
import pytesseract
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
from enum import Enum
from collections import defaultdict


# ============================================================================
# Core Data Classes
# ============================================================================

@dataclass(frozen=True)
class Cell:
    row: int
    col: int
    
    def __repr__(self):
        return f"({self.row},{self.col})"


@dataclass
class Domino:
    value1: int
    value2: int
    
    def get_orientations(self):
        """Return both possible orientations"""
        return [(self.value1, self.value2), (self.value2, self.value1)]
    
    def __repr__(self):
        return f"[{self.value1}|{self.value2}]"


class ConstraintType(Enum):
    SUM = "sum"
    EQUAL = "equal"
    NOT_EQUAL = "notequal"
    LESS_THAN = "less"
    GREATER_THAN = "greater"


@dataclass
class Constraint:
    constraint_type: ConstraintType
    value: Optional[int] = None
    
    def check(self, values: List[int]) -> bool:
        """Check if values satisfy constraint"""
        if not values:
            return True
            
        if self.constraint_type == ConstraintType.SUM:
            return sum(values) == self.value
        elif self.constraint_type == ConstraintType.EQUAL:
            return len(set(values)) == 1
        elif self.constraint_type == ConstraintType.NOT_EQUAL:
            return len(set(values)) == len(values)
        elif self.constraint_type == ConstraintType.LESS_THAN:
            return sum(values) < self.value
        elif self.constraint_type == ConstraintType.GREATER_THAN:
            return sum(values) > self.value
        return True
    
    def can_satisfy(self, values: List[int], total_cells: int) -> bool:
        """Check if partial values could potentially satisfy constraint"""
        if not values:
            return True
            
        if self.constraint_type == ConstraintType.SUM:
            current = sum(values)
            remaining = total_cells - len(values)
            # Could we reach target with remaining cells? (0-6 per cell)
            return current <= self.value <= current + (remaining * 6)
        elif self.constraint_type == ConstraintType.NOT_EQUAL:
            return len(set(values)) == len(values)
        elif self.constraint_type == ConstraintType.LESS_THAN:
            return sum(values) < self.value
        elif self.constraint_type == ConstraintType.GREATER_THAN:
            current = sum(values)
            remaining = total_cells - len(values)
            return current + (remaining * 6) > self.value
        return True


@dataclass
class Region:
    cells: List[Cell]
    constraint: Constraint
    region_id: int
    
    def check_constraint(self, board: 'Board') -> bool:
        """Check if this region satisfies its constraint"""
        values = [board.get_value(cell) for cell in self.cells if board.get_value(cell) is not None]
        
        # If region complete, check full constraint
        if len(values) == len(self.cells):
            return self.constraint.check(values)
        
        # Otherwise check if we can still satisfy
        return self.constraint.can_satisfy(values, len(self.cells))


# ============================================================================
# Board Class
# ============================================================================

class Board:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
    
    def get_value(self, cell: Cell) -> Optional[int]:
        return self.grid[cell.row][cell.col]
    
    def set_value(self, cell: Cell, value: int):
        self.grid[cell.row][cell.col] = value
    
    def clear_value(self, cell: Cell):
        self.grid[cell.row][cell.col] = None
    
    def is_empty(self, cell: Cell) -> bool:
        return self.grid[cell.row][cell.col] is None
    
    def can_place_domino(self, cell: Cell, direction: str) -> bool:
        """Check if domino can be placed at cell in direction (h/v)"""
        if direction == 'h':
            if cell.col + 1 >= self.cols:
                return False
            cell2 = Cell(cell.row, cell.col + 1)
        else:  # vertical
            if cell.row + 1 >= self.rows:
                return False
            cell2 = Cell(cell.row + 1, cell.col)
        
        return self.is_empty(cell) and self.is_empty(cell2)
    
    def place_domino(self, cell: Cell, direction: str, value1: int, value2: int):
        """Place domino on board"""
        self.set_value(cell, value1)
        if direction == 'h':
            self.set_value(Cell(cell.row, cell.col + 1), value2)
        else:
            self.set_value(Cell(cell.row + 1, cell.col), value2)
    
    def remove_domino(self, cell: Cell, direction: str):
        """Remove domino from board"""
        self.clear_value(cell)
        if direction == 'h':
            self.clear_value(Cell(cell.row, cell.col + 1))
        else:
            self.clear_value(Cell(cell.row + 1, cell.col))
    
    def is_complete(self) -> bool:
        """Check if all cells are filled"""
        for row in self.grid:
            if None in row:
                return False
        return True
    
    def __repr__(self):
        result = []
        for row in self.grid:
            result.append(' '.join(str(v) if v is not None else '.' for v in row))
        return '\n'.join(result)


# ============================================================================
# Puzzle Class
# ============================================================================

class Puzzle:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.regions: List[Region] = []
        self.dominoes: List[Domino] = []
        self.cell_to_region = {}
    
    def add_region(self, region: Region):
        self.regions.append(region)
        for cell in region.cells:
            self.cell_to_region[cell] = region
    
    def set_dominoes(self, dominoes: List[Domino]):
        self.dominoes = dominoes
    
    def get_region_for_cell(self, cell: Cell) -> Optional[Region]:
        return self.cell_to_region.get(cell)


# ============================================================================
# Solver Class
# ============================================================================

class Solver:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.board = Board(puzzle.rows, puzzle.cols)
        self.backtrack_count = 0
    
    def solve(self) -> Optional[Board]:
        """Main solving method using backtracking"""
        positions = self._get_all_positions()
        used_dominoes = set()
        
        if self._backtrack(0, positions, used_dominoes):
            return self.board
        return None
    
    def _get_all_positions(self) -> List[Tuple[Cell, str]]:
        """Get all possible domino positions (cell, direction)"""
        positions = []
        for r in range(self.puzzle.rows):
            for c in range(self.puzzle.cols):
                cell = Cell(r, c)
                if c + 1 < self.puzzle.cols:
                    positions.append((cell, 'h'))
                if r + 1 < self.puzzle.rows:
                    positions.append((cell, 'v'))
        return positions
    
    def _backtrack(self, pos_idx: int, positions: List, used_dominoes: Set[int]) -> bool:
        """Recursive backtracking solver"""
        # Check if board is complete
        if self.board.is_complete():
            return True
        
        # Try next position
        if pos_idx >= len(positions):
            return False
        
        cell, direction = positions[pos_idx]
        
        # Skip if position already occupied
        if not self.board.can_place_domino(cell, direction):
            return self._backtrack(pos_idx + 1, positions, used_dominoes)
        
        # Try each unused domino
        for domino_idx, domino in enumerate(self.puzzle.dominoes):
            if domino_idx in used_dominoes:
                continue
            
            # Try both orientations
            for v1, v2 in domino.get_orientations():
                # Place domino
                self.board.place_domino(cell, direction, v1, v2)
                used_dominoes.add(domino_idx)
                
                # Check if all region constraints still satisfiable
                if self._check_all_constraints():
                    if self._backtrack(pos_idx + 1, positions, used_dominoes):
                        return True
                
                # Backtrack
                self.board.remove_domino(cell, direction)
                used_dominoes.remove(domino_idx)
                self.backtrack_count += 1
        
        return False
    
    def _check_all_constraints(self) -> bool:
        """Check if all region constraints are satisfied or can be satisfied"""
        for region in self.puzzle.regions:
            if not region.check_constraint(self.board):
                return False
        return True


# ============================================================================
# Image Parser Classes
# ============================================================================

class GridDetector:
    def __init__(self, image: np.ndarray):
        self.image = image
        self.gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def detect_grid(self) -> Tuple[int, int, List[Tuple[int, int, int, int]]]:
        """
        Detect grid and return (rows, cols, cell_boxes)
        cell_boxes = list of (x, y, w, h) for each cell
        """
        # Apply edge detection
        edges = cv2.Canny(self.gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find rectangular cells (simplified - assumes regular grid)
        cell_boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # Filter for cell-sized rectangles
            if 30 < w < 200 and 30 < h < 200 and 0.8 < w/h < 1.2:
                cell_boxes.append((x, y, w, h))
        
        # Sort and organize into grid
        cell_boxes.sort(key=lambda b: (b[1], b[0]))  # Sort by y, then x
        
        # Estimate grid dimensions
        if not cell_boxes:
            return 0, 0, []
        
        # Group by rows (similar y values)
        rows = []
        current_row = [cell_boxes[0]]
        for box in cell_boxes[1:]:
            if abs(box[1] - current_row[0][1]) < 20:  # Same row
                current_row.append(box)
            else:
                rows.append(sorted(current_row, key=lambda b: b[0]))
                current_row = [box]
        rows.append(sorted(current_row, key=lambda b: b[0]))
        
        num_rows = len(rows)
        num_cols = len(rows[0]) if rows else 0
        
        return num_rows, num_cols, cell_boxes


class RegionDetector:
    def __init__(self, image: np.ndarray, cell_boxes: List):
        self.image = image
        self.cell_boxes = cell_boxes
    
    def detect_regions(self) -> dict:
        """
        Detect regions by color clustering
        Returns dict: {region_id: [cell_indices]}
        """
        # Extract average color for each cell
        cell_colors = []
        for x, y, w, h in self.cell_boxes:
            cell_img = self.image[y:y+h, x:x+w]
            avg_color = cv2.mean(cell_img)[:3]  # BGR
            cell_colors.append(avg_color)
        
        # Simple color clustering (could use k-means for better results)
        regions = defaultdict(list)
        color_to_region = {}
        next_region_id = 0
        
        for idx, color in enumerate(cell_colors):
            # Round color to nearest 30 to group similar colors
            color_key = tuple(int(c // 30) * 30 for c in color)
            
            if color_key not in color_to_region:
                color_to_region[color_key] = next_region_id
                next_region_id += 1
            
            region_id = color_to_region[color_key]
            regions[region_id].append(idx)
        
        return regions


class ConstraintParser:
    @staticmethod
    def parse_constraint_text(text: str) -> Optional[Constraint]:
        """
        Parse OCR text into Constraint object
        Examples: "= 8", "> 5", "=", "≠"
        """
        text = text.strip().replace(' ', '')
        
        if text == '=' or text == '==':
            return Constraint(ConstraintType.EQUAL)
        elif text == '≠' or text == '!=':
            return Constraint(ConstraintType.NOT_EQUAL)
        elif text.startswith('=') and len(text) > 1:
            try:
                value = int(text[1:])
                return Constraint(ConstraintType.SUM, value)
            except ValueError:
                pass
        elif text.startswith('>'):
            try:
                value = int(text[1:])
                return Constraint(ConstraintType.GREATER_THAN, value)
            except ValueError:
                pass
        elif text.startswith('<'):
            try:
                value = int(text[1:])
                return Constraint(ConstraintType.LESS_THAN, value)
            except ValueError:
                pass
        
        return None
    
    @staticmethod
    def extract_constraint_from_region(image: np.ndarray, cell_box: Tuple) -> Optional[Constraint]:
        """
        Extract constraint from top-left corner of first cell in region
        """
        x, y, w, h = cell_box
        # Crop top-left corner
        constraint_area = image[y:y+h//3, x:x+w//2]
        
        # Preprocess for OCR
        gray = cv2.cvtColor(constraint_area, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Run OCR
        text = pytesseract.image_to_string(thresh, config='--psm 7')
        
        return ConstraintParser.parse_constraint_text(text)


class ImageParser:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.image = None
    
    def parse(self) -> Puzzle:
        """Main parsing pipeline"""
        # Load image
        self.image = cv2.imread(self.image_path)
        
        # Detect grid
        grid_detector = GridDetector(self.image)
        rows, cols, cell_boxes = grid_detector.detect_grid()
        
        print(f"Detected {rows}x{cols} grid with {len(cell_boxes)} cells")
        
        # Detect regions
        region_detector = RegionDetector(self.image, cell_boxes)
        region_map = region_detector.detect_regions()
        
        print(f"Detected {len(region_map)} regions")
        
        # Create puzzle
        puzzle = Puzzle(rows, cols)
        
        # Create regions with constraints
        for region_id, cell_indices in region_map.items():
            # Convert indices to Cell objects
            cells = []
            for idx in cell_indices:
                row = idx // cols
                col = idx % cols
                cells.append(Cell(row, col))
            
            # Extract constraint from first cell
            first_idx = cell_indices[0]
            constraint = ConstraintParser.extract_constraint_from_region(
                self.image, cell_boxes[first_idx]
            )
            
            if constraint is None:
                # Default to equal constraint if can't parse
                constraint = Constraint(ConstraintType.EQUAL)
            
            region = Region(cells, constraint, region_id)
            puzzle.add_region(region)
        
        # Parse dominoes (simplified - would need domino section detection)
        # For now, use standard domino set
        dominoes = self._get_standard_dominoes(rows * cols // 2)
        puzzle.set_dominoes(dominoes)
        
        return puzzle
    
    def _get_standard_dominoes(self, count: int) -> List[Domino]:
        """Generate standard domino set"""
        dominoes = []
        for i in range(7):
            for j in range(i, 7):
                dominoes.append(Domino(i, j))
                if len(dominoes) >= count:
                    return dominoes
        return dominoes


# ============================================================================
# Main Automation Class
# ============================================================================

class PipsAutomation:
    def __init__(self, screenshot_path: str):
        self.screenshot_path = screenshot_path
        self.puzzle = None
        self.solution = None
    
    def run(self):
        """End-to-end automation"""
        print("=" * 60)
        print("NYT Pips Solver - Automated")
        print("=" * 60)
        
        # Parse screenshot
        print("\n[1/3] Parsing screenshot...")
        parser = ImageParser(self.screenshot_path)
        self.puzzle = parser.parse()
        
        # Solve puzzle
        print("\n[2/3] Solving puzzle...")
        solver = Solver(self.puzzle)
        self.solution = solver.solve()
        
        # Display results
        print("\n[3/3] Results:")
        print("=" * 60)
        
        if self.solution:
            print("✓ Solution found!")
            print(f"  Backtracks: {solver.backtrack_count}")
            print("\nSolution:")
            print(self.solution)
        else:
            print("✗ No solution found")
            print(f"  Backtracks attempted: {solver.backtrack_count}")
        
        return self.solution


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Create a simple puzzle manually for testing
    puzzle = Puzzle(4, 4)
    
    # Define regions
    region1 = Region(
        [Cell(0,0), Cell(0,1), Cell(1,0)],
        Constraint(ConstraintType.SUM, 8),
        0
    )
    region2 = Region(
        [Cell(0,2), Cell(0,3), Cell(1,3)],
        Constraint(ConstraintType.EQUAL),
        1
    )
    region3 = Region(
        [Cell(1,1), Cell(1,2), Cell(2,1), Cell(2,2)],
        Constraint(ConstraintType.LESS_THAN, 12),
        2
    )
    region4 = Region(
        [Cell(2,0), Cell(3,0), Cell(3,1)],
        Constraint(ConstraintType.SUM, 6),
        3
    )
    region5 = Region(
        [Cell(2,3), Cell(3,2), Cell(3,3)],
        Constraint(ConstraintType.GREATER_THAN, 8),
        4
    )
    
    puzzle.add_region(region1)
    puzzle.add_region(region2)
    puzzle.add_region(region3)
    puzzle.add_region(region4)
    puzzle.add_region(region5)
    
    # Add dominoes
    dominoes = [
        Domino(0, 1), Domino(1, 2), Domino(2, 3), Domino(3, 4),
        Domino(4, 5), Domino(5, 6), Domino(1, 1), Domino(2, 2)
    ]
    puzzle.set_dominoes(dominoes)
    
    # Solve
    solver = Solver(puzzle)
    solution = solver.solve()
    
    if solution:
        print("Solution found!")
        print(solution)
    else:
        print("No solution found")
    
    # For image parsing (uncomment when you have a screenshot):
    # automation = PipsAutomation("pips_screenshot.png")
    # automation.run()