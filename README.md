# Lazor Puzzle Solver

**EN.540.635 Software Carpentry | Fall 2026**

## 1. Project Overview

This project implements an automatic solver for Lazor puzzles.

The program reads a `.bff` puzzle file, constructs a board,
generates valid arrangements of movable blocks, simulates
laser trajectories, and finds an arrangement that reaches
all target points.

The project includes:

- A BFF file reader
- Block classes and board representation
- Laser trajectory simulation
- An automatic puzzle solver
- An optional optimized solver
- Automated unit tests

The included example puzzle is `mad_1.bff`.

Although the project is demonstrated using this puzzle,
the solver is designed to accept other valid `.bff` files.

## 2. Project Structure

| File | Description |
|---|---|
| `bff_reader.py` | Reads and parses BFF puzzle files |
| `blocks.py` | Defines reflecting, opaque, and refracting blocks |
| `board.py` | Constructs the board and manages block placement |
| `laser.py` | Simulates laser trajectories |
| `solver.py` | Original automatic solver |
| `solver_optimized.py` | Optional optimized solver |
| `test_lazor.py` | Automated unit tests |
| `mad_1.bff` | Included example puzzle |
| `README.md` | Project documentation |

## 3. Requirements

- Python 3.10 or newer
- No external Python packages required

## 4. Installation

Clone the GitHub repository:

```bash
git clone https://github.com/shannoncheny/lazor-project.git
cd lazor-project
```

Alternatively, download the project files and open
the project directory in PyCharm.

## 5. Running the Original Solver

Run the solver on the included puzzle:

```bash
python3 solver.py mad_1.bff
```

To specify a maximum runtime of 60 seconds:

```bash
python3 solver.py mad_1.bff --timeout 60
```

The solver prints:

- Number of arrangements tested
- Execution time
- Solved board
- Movable block positions

The solution is saved to:

`mad_1_solution.txt`

## 6. Running the Optimized Solver

Run:

```bash
python3 solver_optimized.py mad_1.bff
```

Or specify a time limit:

```bash
python3 solver_optimized.py mad_1.bff --timeout 60
```

The optimized solver saves its result separately:

`mad_1_optimized_solution.txt`

This prevents the optimized solver from overwriting
the original solver's output.

## 7. BFF Puzzle Format

A `.bff` file specifies the board layout, available
movable blocks, laser sources, and target points.

| Symbol | Meaning |
|---|---|
| `GRID START` | Beginning of the board |
| `GRID STOP` | End of the board |
| `o` | Position where a movable block may be placed |
| `x` | Position where a movable block cannot be placed |
| `A` | Fixed reflecting block inside the grid |
| `B` | Fixed opaque block inside the grid |
| `C` | Fixed refracting block inside the grid |
| `A n` | Number of movable reflecting blocks |
| `B n` | Number of movable opaque blocks |
| `C n` | Number of movable refracting blocks |
| `L x y vx vy` | Laser starting position and direction |
| `P x y` | Target point |

## 8. Block Behavior

The program supports three types of blocks.

### Reflecting Block (A)

Reflects an incoming laser beam.

### Opaque Block (B)

Absorbs an incoming laser beam, stopping its propagation.

### Refracting Block (C)

Produces a transmitted beam and a reflected beam.

Blocks specified directly inside the BFF grid are fixed
and cannot be moved.

## 9. Original Solving Algorithm

The original solver uses exhaustive search with
combinations and backtracking.

The algorithm follows these steps:

1. Read the BFF file.
2. Construct the board.
3. Identify fixed blocks and available positions.
4. Generate unique arrangements of movable blocks.
5. Simulate laser trajectories for each arrangement.
6. Check whether all target points have been reached.
7. Return the first valid solution.
8. Save the solved board to a text file.

Combinations are used instead of permutations to avoid
duplicate arrangements of identical blocks.

## 10. Optional Optimization Challenge

The project includes a separate optimized solver
implemented in `solver_optimized.py`.

The original `solver.py` remains unchanged so the
two implementations can be compared.

### Optimization 1: Block Object Reuse

The optimized solver creates reusable block objects
instead of constructing new objects for every candidate
arrangement.

This reduces repeated object creation.

### Optimization 2: Reduced Placement Validation

Candidate arrangements are generated using valid
positions and exact block counts.

The optimized solver therefore skips redundant
placement validation during laser simulation.

### Optimization 3: Efficient Target Checking

The optimized solver uses set operations to check
whether all target points have been reached.

### Computational Complexity

Both implementations use exhaustive search.

The optimizations reduce processing overhead per
arrangement but do not reduce the number of candidate
arrangements examined in the recorded benchmark.

The worst-case search complexity remains combinatorial.

## 11. Performance Comparison

Both solvers were tested using the included
`mad_1.bff` puzzle.

| Metric | Original Solver | Optimized Solver |
|---|---:|---:|
| Arrangements tested | 554 | 554 |
| Execution time (seconds) | 0.006 | 0.005120 |
| Valid solution found | Yes | Yes |
| Solution identical | Yes | Yes |

For the recorded runs, the optimized solver showed
an approximately **14.7% reduction in execution time**,
equivalent to an approximately **1.17x speedup**.

These results represent individual runs rather than
averaged benchmarks.

Because this puzzle solves in only a few milliseconds,
the observed difference may be affected by measurement
noise. Repeated benchmarks would be needed to establish
a reliable performance improvement.

## 12. Solution for mad_1.bff

Both solvers produced the same solved board:

```text
o o C o
o o o A
A o o o
o o o o
```

Movable block positions:

| Block | Position (x, y) |
|---|---|
| A | (0, 2) |
| C | (2, 0) |
| A | (3, 1) |

The solution satisfies all target points according
to the project's laser simulation.

## 13. Automated Testing

Run the test suite using:

```bash
python3 -m unittest -v test_lazor
```

The tests cover:

- BFF parsing and invalid symbols
- Block creation
- Fixed block handling
- Legal and illegal movable block placement
- Laser direction validation
- Laser reflection
- Laser absorption
- Laser refraction
- Target detection
- Automatic puzzle solving

The existing test suite passed all 12 tests
in the recorded run.

Some tests may reference additional puzzle files,
depending on the current contents of `test_lazor.py`.

## 14. Error Handling

The solver handles:

- Missing input files
- Invalid file extensions
- Invalid timeout values
- Invalid puzzle data detected by the parser or board

## 15. Limitations

- Exhaustive search may become expensive for larger puzzles.
- The solver returns the first valid solution.
- The optimized solver retains combinatorial search complexity.
- The reported performance comparison uses one puzzle
  and one recorded run per implementation.

## 16. Distribution of Work

The project was developed collaboratively by three
group members, with the following responsibilities.

| Group Member | Responsibilities |
|---|---|
| Member 1 | Implement `.bff` file reading and board representation, including block classes. |
| Member 2 | Implement laser path simulation and interactions with different block types. |
| Member 3 | Develop the solution-search algorithm, including generating and checking possible block arrangements. |
| All Members | Work together on debugging, testing, improving runtime efficiency, writing documentation, and reviewing the final code before submission. |

## 17. Repository

The project is maintained using Git and GitHub.

https://github.com/shannoncheny/lazor-project
