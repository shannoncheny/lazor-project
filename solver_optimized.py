
"""
Optimized automatic solver for Lazor puzzles.

Optional optimization challenge:
1. Reuse block objects across candidate arrangements.
2. Skip redundant placement validation.
3. Use efficient set-based target checking.

The original solver.py remains unchanged.
"""

import argparse
import sys
import time
from itertools import combinations
from pathlib import Path

from bff_reader import read_bff
from blocks import make_block
from board import Board
from laser import LaserSimulator


BLOCK_TYPES = ("A", "B", "C")


def generate_arrangements(board):
    """
    Generate unique, valid arrangements of movable blocks.

    Optimizations:
    - Use combinations instead of permutations.
    - Reuse block objects for each block type.
    - Avoid generating duplicate arrangements.
    """

    positions = tuple(sorted(board.open_positions))
    counts = board.block_counts

    for symbol in BLOCK_TYPES:
        if counts.get(symbol, 0) < 0:
            raise ValueError(
                f"Invalid negative block count for {symbol}."
            )

    total_blocks = sum(
        counts.get(symbol, 0)
        for symbol in BLOCK_TYPES
    )

    if total_blocks > len(positions):
        return

    # Create one reusable block object per block type.
    block_objects = {
        symbol: make_block(symbol)
        for symbol in BLOCK_TYPES
        if counts.get(symbol, 0) > 0
    }

    def backtrack(index, available, placement):
        """Recursively generate valid block placements."""

        if index == len(BLOCK_TYPES):
            yield placement.copy()
            return

        symbol = BLOCK_TYPES[index]
        count = counts.get(symbol, 0)

        if count == 0:
            yield from backtrack(
                index + 1,
                available,
                placement
            )
            return

        block = block_objects[symbol]

        for chosen in combinations(available, count):

            chosen_set = set(chosen)

            for position in chosen:
                placement[position] = block

            remaining = tuple(
                position
                for position in available
                if position not in chosen_set
            )

            yield from backtrack(
                index + 1,
                remaining,
                placement
            )

            for position in chosen:
                del placement[position]

    yield from backtrack(
        0,
        positions,
        {}
    )


def solve_puzzle(filename, max_seconds=None):
    """
    Solve a Lazor puzzle using optimized exhaustive search.

    Parameters
    ----------
    filename : str
        Path to a .bff puzzle file.

    max_seconds : float or None
        Optional positive time limit.

    Returns
    -------
    tuple
        (board, solution, attempts, elapsed)

    solution is None if no solution is found.
    """

    if max_seconds is not None and max_seconds <= 0:
        raise ValueError(
            "The time limit must be positive."
        )

    puzzle_path = Path(filename)

    if not puzzle_path.is_file():
        raise FileNotFoundError(
            f"Puzzle file not found: {filename}"
        )

    if puzzle_path.suffix.lower() != ".bff":
        raise ValueError(
            "The input file must have a .bff extension."
        )

    board_data = read_bff(str(puzzle_path))
    board = Board(board_data)

    simulator = LaserSimulator(board)

    # Optimization: convert targets to a set once.
    targets = {
        tuple(target)
        for target in board.targets
    }

    start_time = time.perf_counter()
    attempts = 0

    for arrangement in generate_arrangements(board):

        elapsed = time.perf_counter() - start_time

        if (
            max_seconds is not None
            and elapsed >= max_seconds
        ):
            print(
                "Search stopped: time limit reached."
            )

            return (
                board,
                None,
                attempts,
                elapsed
            )

        attempts += 1

        # Optimization:
        # Arrangements are generated with valid positions
        # and exact block counts, so skip validation.
        visited_points, _ = simulator.laser_trajectory(
            arrangement,
            check_position=False
        )

        # Optimization:
        # Set membership checks are efficient.
        if targets.issubset(set(visited_points)):

            elapsed = time.perf_counter() - start_time

            return (
                board,
                arrangement.copy(),
                attempts,
                elapsed
            )

    elapsed = time.perf_counter() - start_time

    return (
        board,
        None,
        attempts,
        elapsed
    )


def display_solution(board, solution):
    """Print the solved board and movable block positions."""

    grid = [
        row.copy()
        for row in board.grid
    ]

    for (x, y), block in solution.items():
        grid[y][x] = block.symbol

    print("\nSolved board:")

    for row in grid:
        print(" ".join(row))

    print("\nMovable block positions:")

    for (x, y), block in sorted(solution.items()):
        print(
            f"  {block.symbol}: ({x}, {y})"
        )

    return grid


def save_solution(filename, grid, solution):
    """Save the solved puzzle to a text file."""

    puzzle_path = Path(filename)

    output_path = puzzle_path.with_name(
        f"{puzzle_path.stem}_optimized_solution.txt"
    )

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            f"Optimized solution for {puzzle_path.name}\n\n"
        )

        file.write("Solved board:\n")

        for row in grid:
            file.write(
                " ".join(row) + "\n"
            )

        file.write(
            "\nMovable block positions:\n"
        )

        for (x, y), block in sorted(solution.items()):
            file.write(
                f"{block.symbol}: ({x}, {y})\n"
            )

    print(
        f"\nSolution saved to: {output_path}"
    )

    return output_path


def main():
    """Run the optimized solver from the command line."""

    parser = argparse.ArgumentParser(
        description=(
            "Optimized automatic Lazor puzzle solver."
        )
    )

    parser.add_argument(
        "filename",
        nargs="?",
        default="mad_1.bff",
        help="Path to the .bff puzzle file"
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional time limit in seconds"
    )

    args = parser.parse_args()

    try:
        print("=" * 45)
        print("OPTIMIZED LAZOR SOLVER")
        print("=" * 45)

        print(
            f"Solving: {args.filename}"
        )

        board, solution, attempts, elapsed = solve_puzzle(
            args.filename,
            max_seconds=args.timeout
        )

        print(
            f"\nArrangements tested: {attempts}"
        )

        print(
            f"Elapsed time: {elapsed:.6f} seconds"
        )

        if solution is None:
            print(
                "\nNo solution found within the search performed."
            )
            return 1

        print(
            "\nSUCCESS: All targets are reached!"
        )

        grid = display_solution(
            board,
            solution
        )

        save_solution(
            args.filename,
            grid,
            solution
        )

        return 0

    except (
        FileNotFoundError,
        ValueError,
        OSError
    ) as error:

        print(
            f"\nERROR: {error}",
            file=sys.stderr
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())
