
"""
Automated tests for the Lazor puzzle solver.

Tests:
- BFF file reading
- Block classes
- Board representation
- Laser simulation
- Original solver
- Optimized solver

Run from the project root:
    python3 -m unittest -v test_lazor
"""

import tempfile
import unittest
from pathlib import Path

from bff_reader import read_bff
from blocks import Opaque, Reflect, Refract, make_block
from board import Board
from laser import LaserSimulator


ROOT = Path(__file__).resolve().parent
PUZZLE = ROOT / "mad_1.bff"


def sample_data(grid=None, counts=None, lasers=None, targets=None):
    """Create a small board for isolated tests."""

    grid = grid if grid is not None else [["o"]]

    return {
        "grid": grid,
        "width": len(grid[0]),
        "height": len(grid),
        "block_counts": (
            counts
            if counts is not None
            else {"A": 0, "B": 0, "C": 0}
        ),
        "lasers": (
            lasers
            if lasers is not None
            else [(0, 1, 1, 1)]
        ),
        "targets": (
            targets
            if targets is not None
            else [(1, 2)]
        ),
    }


class TestBffReader(unittest.TestCase):
    """Tests for reading BFF puzzle files."""

    def test_mad_1_parses_expected_fields(self):
        """Check that mad_1.bff is parsed correctly."""

        self.assertTrue(
            PUZZLE.is_file(),
            "mad_1.bff must exist in the project folder."
        )

        data = read_bff(PUZZLE)

        self.assertEqual(
            (data["width"], data["height"]),
            (4, 4)
        )

        self.assertEqual(
            data["block_counts"],
            {"A": 2, "B": 0, "C": 1}
        )

        self.assertEqual(
            data["lasers"],
            [(2, 7, 1, -1)]
        )

        self.assertEqual(
            len(data["targets"]),
            4
        )

    def test_invalid_grid_symbol_rejected(self):
        """Reject unsupported symbols in BFF grids."""

        content = (
            "GRID START\n"
            "o Z\n"
            "GRID STOP\n"
            "L 0 1 1 1\n"
            "P 1 2\n"
        )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.bff"

            path.write_text(
                content,
                encoding="utf-8"
            )

            with self.assertRaises(ValueError):
                read_bff(path)


class TestBlocksAndBoard(unittest.TestCase):
    """Tests for blocks and board placement."""

    def test_block_factory(self):
        """Check block creation and fixed properties."""

        self.assertIsInstance(
            make_block("A"),
            Reflect
        )

        self.assertIsInstance(
            make_block("B"),
            Opaque
        )

        self.assertIsInstance(
            make_block("C"),
            Refract
        )

        self.assertFalse(
            make_block("A").fixed
        )

        self.assertTrue(
            make_block("A", fixed=True).fixed
        )

        with self.assertRaises(ValueError):
            make_block("Z")

    def test_fixed_blocks_and_open_positions(self):
        """Check that fixed blocks cannot be moved."""

        board = Board(
            sample_data(
                grid=[
                    ["A", "o"],
                    ["x", "o"]
                ]
            )
        )

        self.assertEqual(
            board.open_positions,
            {(1, 0), (1, 1)}
        )

        self.assertTrue(
            board.fixed_blocks[(0, 0)].fixed
        )

        self.assertEqual(
            board.play_grid()[1][1],
            "A"
        )

    def test_valid_movable_placement(self):
        """Accept a legal movable block placement."""

        board = Board(
            sample_data(
                counts={
                    "A": 1,
                    "B": 0,
                    "C": 0
                }
            )
        )

        placement = {
            (0, 0): make_block("A")
        }

        self.assertEqual(
            board.play_grid(placement)[1][1],
            "A"
        )

    def test_illegal_placements_rejected(self):
        """Reject illegal block placements."""

        board = Board(
            sample_data(
                grid=[["x", "o"]],
                counts={
                    "A": 1,
                    "B": 0,
                    "C": 0
                }
            )
        )

        # Cannot place a block on a forbidden position.
        with self.assertRaises(ValueError):
            board.play_grid({
                (0, 0): make_block("A")
            })

        # Cannot place a fixed block as a movable block.
        with self.assertRaises(ValueError):
            board.play_grid({
                (1, 0): make_block(
                    "A",
                    fixed=True
                )
            })

        # Cannot omit required movable blocks.
        with self.assertRaises(ValueError):
            board.play_grid({})


class TestLaser(unittest.TestCase):
    """Tests for laser trajectory simulation."""

    def test_unblocked_laser_reaches_target(self):
        """Check laser propagation without obstacles."""

        simulator = LaserSimulator(
            Board(sample_data())
        )

        points, paths = simulator.laser_trajectory()

        self.assertIn(
            (0, 1),
            points
        )

        self.assertIn(
            (1, 2),
            points
        )

        self.assertTrue(paths)

        self.assertTrue(
            simulator.board_is_solution()
        )

    def test_opaque_block_stops_laser(self):
        """Check that an opaque block absorbs the laser."""

        simulator = LaserSimulator(
            Board(
                sample_data(
                    grid=[["B"]]
                )
            )
        )

        points, _ = simulator.laser_trajectory()

        self.assertNotIn(
            (1, 2),
            points
        )

        self.assertFalse(
            simulator.board_is_solution()
        )

    def test_reflecting_block_turns_laser(self):
        """Check that reflecting blocks redirect lasers."""

        simulator = LaserSimulator(
            Board(
                sample_data(
                    grid=[["A"]]
                )
            )
        )

        points, _ = simulator.laser_trajectory()

        self.assertNotIn(
            (1, 2),
            points
        )

        self.assertFalse(
            simulator.board_is_solution()
        )

        self.assertEqual(
            simulator._reflect_beam(0, 1, 1),
            (-1, 1)
        )

        self.assertEqual(
            simulator._reflect_beam(1, 1, 1),
            (1, -1)
        )

    def test_refracting_block_transmits_and_splits(self):
        """Check that refracting blocks split laser beams."""

        simulator = LaserSimulator(
            Board(
                sample_data(
                    grid=[["C"]]
                )
            )
        )

        points, paths = simulator.laser_trajectory()

        self.assertIn(
            (1, 2),
            points
        )

        self.assertGreaterEqual(
            len(paths),
            2
        )

        self.assertTrue(
            simulator.board_is_solution()
        )

    def test_invalid_laser_direction_rejected(self):
        """Reject invalid laser directions."""

        with self.assertRaises(ValueError):
            LaserSimulator(
                Board(
                    sample_data(
                        lasers=[
                            (0, 1, 0, 1)
                        ]
                    )
                )
            )


class TestSolver(unittest.TestCase):
    """Tests for original and optimized solvers."""

    def check_solution(self, solve_function):
        """Check a solver's solution to mad_1.bff."""

        self.assertTrue(
            PUZZLE.is_file(),
            "mad_1.bff must exist in the project folder."
        )

        board, solution, attempts, elapsed = solve_function(
            str(PUZZLE),
            max_seconds=60
        )

        # A valid solution must be found.
        self.assertIsNotNone(
            solution,
            "No solution found for mad_1.bff."
        )

        # The solver must examine at least one arrangement.
        self.assertGreater(
            attempts,
            0
        )

        # The solver must finish within the time limit.
        self.assertLess(
            elapsed,
            60
        )

        # All targets must be reached.
        simulator = LaserSimulator(board)

        self.assertTrue(
            simulator.board_is_solution(solution)
        )

        # All movable blocks must occupy open positions.
        self.assertTrue(
            set(solution).issubset(
                board.open_positions
            )
        )

        # The number of blocks must match the BFF file.
        for symbol in ("A", "B", "C"):
            actual_count = sum(
                block.symbol == symbol
                for block in solution.values()
            )

            expected_count = board.block_counts.get(
                symbol,
                0
            )

            self.assertEqual(
                actual_count,
                expected_count
            )

        return solution

    def test_original_solver(self):
        """Test the original solver on mad_1.bff."""

        from solver import solve_puzzle

        self.check_solution(solve_puzzle)

    def test_optimized_solver(self):
        """Test the optimized solver on mad_1.bff."""

        from solver_optimized import solve_puzzle

        self.check_solution(solve_puzzle)


if __name__ == "__main__":
    unittest.main(verbosity=2)
