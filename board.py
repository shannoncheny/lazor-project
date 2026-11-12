from blocks import Block, make_block


class Board:
    """
    This class object will represent a board and prepare it for
    the laser simulator.
    """

    def __init__(self, board_data):
        """
        Initialize the board by copying the board data from the
        dictionary returned by read_bff().

        **parameters**
            board_data: *dict*
                output from read_bff()
            fixed_blocks: *dict*
                maps a position (x,y) to a fixed block
            open_positions: *set*
                positions on grid where a floater block may be placed
            playing_grid: *list*
                expanded grid with fixed blocks
        """
        self.grid = []
        for row in board_data["grid"]:
            self.grid.append(row.copy())

        self.width = board_data["width"]
        self.height = board_data["height"]
        self.block_counts = board_data["block_counts"].copy()
        self.lasers = list(board_data["lasers"].copy())
        self.targets = list(board_data["targets"].copy())

        self.fixed_blocks = {}
        self.open_positions = set()
        self._interpret_grid()
        self.playing_grid = self._new_grid()

    def _interpret_grid(self):
        """
        Reads through each symbol in the grid and
        identifies blocks with fixed positions (making a block object
        for each) and keeps track of the leftover/open spots

        **parameters**
            none
        **returns**
            none
        """
        for row in range(self.height):
            for col in range(self.width):
                symbol = self.grid[row][col]

                if symbol in ["A", "B", "C"]:
                    block = make_block(symbol, fixed=True)
                    self.fixed_blocks[(col, row)] = block

                elif symbol == "o":
                    self.open_positions.add((col, row))

    def _new_grid(self):
        """
        The laser travels in half block step sizes. We therefore build a new,
        expanded, and empty grid that can work with the laser simulator.

        i.e. for a symbol in position (x,y) the new coordinate of the symbol
        would be (2x+1, 2y+1)

        **parameters**
            none
        **returns**
            new_grid: *list of lists*
                grid representing game board and friendly to laser simulator
        """
        new_grid = []

        for row in range(2 * self.height + 1):
            new_row = []
            for col in range(2 * self.width + 1):
                new_row.append(" ")
            new_grid.append(new_row)

        for position, block in self.fixed_blocks.items():
            x, y = position
            updated_x = 2 * x + 1
            updated_y = 2 * y + 1
            new_grid[updated_y][updated_x] = block.symbol

        return new_grid

    def play_grid(self, floater_blocks=None, check_position=True):
        """
        This function places the fixed and moveable blocks on the new
        grid to create the play grid that will be fed to the laser tracer

        **parameters**
            floater_blocks: *dict*
                maps a position (x,y) from the original compact .bff grid
                to a block object
            check_position: *bool*
                if True, check whether block placement is valid

        **returns**
            play_grid: *list of lists*
                the playing field for the laser simulation
        """
        if floater_blocks is None:
            floater_blocks = {}

        if check_position:
            self._chk_pos(floater_blocks)

        play_grid = []
        for new_row in self.playing_grid:
            play_grid.append(new_row.copy())

        for position, block in floater_blocks.items():
            x, y = position
            updated_x = 2 * x + 1
            updated_y = 2 * y + 1
            play_grid[updated_y][updated_x] = block.symbol

        return play_grid

    def _chk_pos(self, floater_blocks):
        """
        This functions checks if a moveable block can be moved
        to a proposed position

        We have the following constraints:
        - The block should only be placed in open positions,
        - The blocks should be moveable and
        - the maximum amount of a certain block type should match
          the criteria in the .bff file

        **parameters**
            floater_blocks: *dict*
                maps a position (x,y) from the original compact .bff grid
                to a block object
        **raises**
            ValueError:
                error raised if a block is placed outside the board,
                on an 'x' or a position that already contains a fixed block,
                if labeled as fixed itself, has a symbol that is not A, B, or C,
                or if block counts are inconsistent with the constraints set
                by the .bff file

            TypeError:
                error raised if block is not an object
        """
        play_grid_block_counts = {"A": 0, "B": 0, "C": 0}

        for position, block in floater_blocks.items():
            if position not in self.open_positions:
                x, y = position

                on_board = 0 <= x < self.width and 0 <= y < self.height
                if not on_board:
                    raise ValueError("Block cannot exist outside the board")

                if position in self.fixed_blocks:
                    fixed_block = self.fixed_blocks[position]
                    raise ValueError(
                        f"A fixed {
                            fixed_block.name} block already exists at position {position}")

                raise ValueError(
                    "Block cannot be placed on a position marked with x")

            if not isinstance(block, Block):
                raise TypeError("At least one of your blocks is not an object")

            if block.symbol not in play_grid_block_counts:
                raise ValueError("Unknown block type")

            if block.fixed:
                raise ValueError(
                    "Block position is fixed. It should not be moved!"
                )

            play_grid_block_counts[block.symbol] += 1

        for symbol in ["A", "B", "C"]:
            expected = self.block_counts.get(symbol, 0)
            reality = play_grid_block_counts[symbol]

            if reality != expected:
                raise ValueError(f"Incorrect number of {symbol} blocks." +
                                 f"Expected {str(expected)}" +
                                 f"but received {str(reality)}")
