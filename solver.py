
"""Automatically solve Lazor puzzles stored in .bff files."""

import argparse
import sys
import time
from itertools import combinations
from pathlib import Path

from bff_reader import read_bff
from board import Board
from blocks import make_block
from laser import LaserSimulator


BLOCK_SYMBOLS = ("A", "B", "C")


def generate_arrangements(board):
    """Yield unique legal arrangements of all movable blocks."""
    positions = tuple(sorted(board.open_positions))
    counts = board.block_counts

    if any(counts.get(symbol, 0) < 0 for symbol in BLOCK_SYMBOLS):
        raise ValueError("Block counts cannot be negative.")

    total_blocks = sum(
        counts.get(symbol, 0) for symbol in BLOCK_SYMBOLS
    )

    if total_blocks > len(positions):
        return

    def backtrack(symbol_index, available, placement):
        """Place one block type at a time without duplicates."""
        if symbol_index == len(BLOCK_SYMBOLS):
            yield placement.copy()
            return

        symbol = BLOCK_SYMBOLS[symbol_index]
        count = counts.get(symbol, 0)

        for chosen in combinations(available, count):
            chosen_set = set(chosen)

            for position in chosen:
                placement[position] = make_block(symbol)

            remaining = tuple(
                position
                for position in available
                if position not in chosen_set
            )

            yield from backtrack(
                symbol_index + 1,
                remaining,
                placement,
            )

            for position in chosen:
                del placement[position]

    yield from backtrack(0, positions, {})


def solve_puzzle(filename, max_seconds=None):
    """Find a valid arrangement using exhaustive search.

    Args:
        filename: Path to the input .bff file.
        max_seconds: Optional positive time limit in seconds.

    Returns:
        Tuple containing the board, solution (or None),
        number of arrangements tested, and elapsed time.
    """
    if max_seconds is not None and max_seconds <= 0:
        raise ValueError("The time limit must be positive.")

    puzzle_path = Path(filename)

    if not puzzle_path.is_file():
        raise FileNotFoundError(
            f"Puzzle file not found: {puzzle_path}"
        )

    if puzzle_path.suffix.lower() != ".bff":
        raise ValueError("The input file must have a .bff extension.")

    board_data = read_bff(str(puzzle_path))
    board = Board(board_data)
    simulator = LaserSimulator(board)

    start = time.perf_counter()
    attempts = 0

    for arrangement in generate_arrangements(board):
        if (
            max_seconds is not None
            and time.perf_counter() - start >= max_seconds
        ):
            elapsed = time.perf_counter() - start
            print("Search stopped: time limit reached.")
            return board, None, attempts, elapsed

        attempts += 1

        if simulator.board_is_solution(arrangement):
            elapsed = time.perf_counter() - start

            return (
                board,
                arrangement.copy(),
                attempts,
                elapsed,
            )

    elapsed = time.perf_counter() - start
    return board, None, attempts, elapsed


def display_solution(board, solution):
    """Display the solved board and movable block positions."""
    grid = [row.copy() for row in board.grid]

    for (x, y), block in solution.items():
        grid[y][x] = block.symbol

    print("\nSolved board:")

    for row in grid:
        print(" ".join(row))

    print("\nMovable block positions:")

    for (x, y), block in sorted(solution.items()):
        print(f"  {block.symbol}: ({x}, {y})")

    return grid


def save_solution(filename, grid, solution):
    """Save a human-readable solution next to the input puzzle."""
    source = Path(filename)
    output = source.with_name(
        f"{source.stem}_solution.txt"
    )

    with output.open("w", encoding="utf-8") as file:
        file.write(f"Solution for {source.name}\n\n")
        file.write("Solved board:\n")

        for row in grid:
            file.write(" ".join(row) + "\n")

        file.write("\nMovable block positions:\n")

        for (x, y), block in sorted(solution.items()):
            file.write(
                f"{block.symbol}: ({x}, {y})\n"
            )

    print(f"\nSolution saved to: {output}")
    return output


def main():
    """Parse command-line arguments and solve the puzzle."""
    parser = argparse.ArgumentParser(
        description="Automatically solve Lazor BFF puzzles."
    )

    parser.add_argument(
        "filename",
        nargs="?",
        default="mad_1.bff",
        help="Path to the puzzle file (default: mad_1.bff)",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional positive time limit in seconds",
    )

    args = parser.parse_args()

    try:
        print(f"Solving: {args.filename}")

        board, solution, attempts, elapsed = solve_puzzle(
            args.filename,
            max_seconds=args.timeout,
        )

        print(f"\nArrangements tested: {attempts}")
        print(f"Elapsed time: {elapsed:.3f} seconds")

        if solution is None:
            print(
                "\nNo solution found within the search performed."
            )
            return 1

        print("\nSUCCESS: All targets are reached!")

        grid = display_solution(board, solution)
        save_solution(args.filename, grid, solution)

        return 0

    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
