class LaserSimulator:
    """
    This class object will determine the trajectory of a laser beam within a
    candidate board.

    Provided that blocks assume positions at odd x and y's, the laser only ever
    touches block edges. Therefore, the positions that a laser can
    lie in are restricted to those with either an odd x and even y or vice
    versa.

    If x is even and y is odd, the laser lies on a vertical edge of a block.
    Otherwise, it is positioned at a horizontal edge of a block.
    """

    def __init__(self, board):
        """
        Initialize the simulator and check that every laser tuple
        is valid.

        **parameters**
            board: *Board*
                board reconstructed from a .bff file
        """
        self.board = board
        self.max_x = 2 * board.width
        self.max_y = 2 * board.height

        self.lasers = []
        for laser in board.lasers:
            self.lasers.append(tuple(laser))

        self._chk_lasers()

    def _chk_lasers(self):
        """
        Check if laser lies on an edge or a corner and whether
        the directions are valid

        **raises**
            ValueError:
                If any laser's starting position or direction is invalid
        """
        for x, y, vx, vy in self.lasers:
            # to be on an edge, x and y must sum to an odd number
            laser_start_on_edge = (x + y) % 2
            if laser_start_on_edge == 0:  # even number
                raise ValueError(
                    f"Laser start position {(x,
                                             y)} should lie on the edge of a block"
                )

            if abs(vx) != 1 or abs(vy) != 1:
                raise ValueError(
                    f"Laser directions {(vx, vy)} should be +1 or -1"
                )

    def _is_inside_board(self, x, y):
        """
        Check whether position (x,y) lies inside the board.

        **returns**
            *bool*
                True if (x, y) exists inside the board.
        """
        return 0 <= x <= self.max_x and 0 <= y <= self.max_y

    def _is_on_vertical_edge(self, x):
        """
        Check whether a laser lies on a vertical edge.

        **returns**
            *bool*
                True if a laser with positon (x,y) has even x and
                False if a laser with position (x,y) had odd x
        """
        return x % 2 == 0

    def _beam_symbol_collision(self, play_grid, x, y, vx, vy):
        """
        Identify the symbol that our laser beam will collide with. This will
        be used to determine how the laser beam path should be transformed
        depending on what it encounters.

        **returns**
            bff_symbol: *str*
                The .bff symbol of the space the laser is entering.
                This could be a block (A, B, or C) or an empty space.
        """
        if self._is_on_vertical_edge(x):
            # if our laser is at a vertical edge, move left or right
            # to determine the .bff symbol the laser has collided with
            bff_x = x + vx
            bff_y = y
        # horizontal edge
        else:
            # if our laser is at a horizontal edge, move up or down
            # to determine the .bff symbol the laser has collided with
            bff_x = x
            bff_y = y + vy

        if not self._is_inside_board(bff_x, bff_y):
            return " "

        bff_symbol = play_grid[bff_y][bff_x]
        return bff_symbol

    def _reflect_beam(self, x, vx, vy):
        """
        Calculates the new direction of the laser beam after it
        interacts with an A or C block type. If the laser lies on
        a vertical edge of a block, new_vx = -vx and vy remains
        unchanged; otherwise, if the laser lies on a horizontal
        edge, the new_vy = -vy and vx remains unchanged.

        **parameters**
            x: *int*
                laser beam's x position
            vx: *int*
                laser beam's x direction
            vy: *int*
                laser beam's y direction
        **returns**
                *tuple*
                Returns the updated laser beam direction (vx, vy)
                after reflection
        """
        if self._is_on_vertical_edge(x):
            return -vx, vy
        else:
            return vx, -vy

    def laser_trajectory(self, floater_blocks=None, check_position=True):
        """
        Determine the trajectory of one or multiple laser beams through a board.

        **parameters**
            floater_blocks: *dict*
                maps a grid position (x,y) to a block
            check_position: *bool*
                if True, check whether block placement is valid

        **returns**
            points_traveled_through: *set*
                every position (x, y) the laser beam(s) travel through
                (all positions are unique)
            laser_paths: *list*
                a list of (x, y) positions each laser has traveled through
        """
        play_grid = self.board.play_grid(floater_blocks, check_position)

        points_traveled_through = set()
        laser_paths = []
        beams_left_to_trace = list(self.lasers)
        visited = set()

        while beams_left_to_trace:
            x, y, vx, vy = beams_left_to_trace.pop(0)
            path = [(x, y)]
            points_traveled_through.add((x, y))

            while True:
                current_pos_and_direction = (x, y, vx, vy)
                if current_pos_and_direction in visited:
                    break
                visited.add(current_pos_and_direction)

                symbol = self._beam_symbol_collision(play_grid, x, y, vx, vy)

                if symbol == "B":
                    break

                if symbol == "A":
                    vx, vy = self._reflect_beam(x, vx, vy)
                    x += vx
                    y += vy

                    if not self._is_inside_board(x, y):
                        break

                    path.append((x, y))
                    points_traveled_through.add((x, y))

                    continue

                if symbol == "C":
                    new_vx, new_vy = self._reflect_beam(x, vx, vy)
                    # upon refraction, we add a new laser beam
                    # to our set of laser beams that require tracing
                    beams_left_to_trace.append((x, y, new_vx, new_vy))

                x += vx
                y += vy

                if not self._is_inside_board(x, y):
                    break

                path.append((x, y))
                points_traveled_through.add((x, y))

            laser_paths.append(path)

        return points_traveled_through, laser_paths

    def board_is_solution(self, floater_blocks=None):
        """
        Check if playing board solves the challenge

        **parameters**
            floater_blocks: *dict*
                maps a position (x,y) from the original compact .bff grid
                to a block object
        **returns**
            *bool*
                True if all board targets are included in the list
                of points our beams traveled through.
        """
        points_traveled_through, _ = self.laser_trajectory(floater_blocks)

        for target in self.board.targets:
            if tuple(target) not in points_traveled_through:
                return False

        return True
