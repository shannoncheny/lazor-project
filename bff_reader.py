"""Read Lazor .bff files into Python data structures."""

import argparse
from pathlib import Path
from pprint import pprint


def _parse_numbers(parts, expected_count, line_number):
    """Read a record's numeric fields as a tuple of integers."""
    record_type = parts[0]
    if len(parts) != expected_count + 1:
        raise ValueError(
            f"Line {line_number}: {record_type} requires "
            f"{expected_count} integer value(s)."
        )

    try:
        return tuple(int(value) for value in parts[1:])
    except ValueError as error:
        raise ValueError(
            f"Line {line_number}: {record_type} values must be integers."
        ) from error


def read_bff(filename):
    """Read a .bff file and return its board data as a dictionary.

    The grid contains the original symbols: o, x, A, B, and C.
    Access a grid cell using grid[row][col]. Uppercase grid symbols
    describe fixed blocks; block_counts describes movable blocks.

    Each laser is an (x, y, vx, vy) tuple. Each target is an (x, y)
    tuple. These coordinates use half-block units, with the origin
    at the top left, x increasing rightward, and y increasing downward.

    Raise ValueError for invalid content. File access errors are
    allowed to propagate to the caller.
    """
    grid = []
    block_counts = {"A": 0, "B": 0, "C": 0}
    lasers = []
    targets = []
    specified_counts = set()
    grid_state = "before"

    with open(filename, "r", encoding="utf-8-sig") as bff_file:
        for line_number, line in enumerate(bff_file, start=1):
            # Remove comments and skip empty lines.
            line = line.split("#", 1)[0].strip()
            if not line:
                continue

            parts = line.split()
            prefix = f"Line {line_number}: "

            # Identify the beginning and end of the grid.
            if parts == ["GRID", "START"]:
                if grid_state != "before":
                    raise ValueError(prefix + "Duplicate GRID START.")
                grid_state = "inside"
                continue

            if parts == ["GRID", "STOP"]:
                if grid_state != "inside":
                    raise ValueError(prefix + "Unexpected GRID STOP.")
                grid_state = "after"
                continue

            # Store each grid row as a list of symbols.
            if grid_state == "inside":
                for symbol in parts:
                    if symbol not in {"o", "x", "A", "B", "C"}:
                        raise ValueError(
                            prefix + f"Invalid grid symbol: {symbol!r}."
                        )
                if grid and len(parts) != len(grid[0]):
                    raise ValueError(
                        prefix + "Grid rows must have the same length."
                    )
                grid.append(parts)
                continue

            # Read movable block counts, laser records, and targets.
            record_type = parts[0]
            if record_type in block_counts:
                count = _parse_numbers(parts, 1, line_number)[0]
                if count < 0:
                    raise ValueError(
                        prefix + "Block counts cannot be negative."
                    )
                if record_type in specified_counts:
                    raise ValueError(
                        prefix + f"Duplicate count for {record_type}."
                    )
                block_counts[record_type] = count
                specified_counts.add(record_type)

            elif record_type == "L":
                laser = _parse_numbers(parts, 4, line_number)
                if laser[2:] == (0, 0):
                    raise ValueError(
                        prefix + "Laser direction cannot be (0, 0)."
                    )
                lasers.append(laser)

            elif record_type == "P":
                targets.append(_parse_numbers(parts, 2, line_number))

            else:
                raise ValueError(
                    prefix + f"Unknown record type: {record_type!r}."
                )

    # Check the complete grid before using its dimensions.
    if grid_state == "before":
        raise ValueError("Missing GRID START.")
    if grid_state == "inside":
        raise ValueError("Missing GRID STOP.")
    if not grid:
        raise ValueError("The grid cannot be empty.")

    width = len(grid[0])
    height = len(grid)

    # Half-block coordinates include the outer edges of the board.
    for x, y, vx, vy in lasers:
        if not (0 <= x <= 2 * width and 0 <= y <= 2 * height):
            raise ValueError(f"Laser start {(x, y)} is outside the board.")

    for x, y in targets:
        if not (0 <= x <= 2 * width and 0 <= y <= 2 * height):
            raise ValueError(f"Target {(x, y)} is outside the board.")

    return {
        "grid": grid,
        "width": width,
        "height": height,
        "block_counts": block_counts,
        "lasers": lasers,
        "targets": targets,
    }


def main():
    """Read a board file and display the parsed data."""
    default_file = Path(__file__).with_name("mad_1.bff")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "filename",
        nargs="?",
        default=str(default_file),
        help=(
            "Path to a .bff file. The default is mad_1.bff "
            "beside this script."
        ),
    )
    args = parser.parse_args()

    try:
        board_data = read_bff(args.filename)
    except (OSError, ValueError) as error:
        parser.exit(status=1, message=f"Error: {error}\n")

    pprint(board_data, sort_dicts=False)


if __name__ == "__main__":
    main()
