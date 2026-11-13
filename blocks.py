class Block:
    """
    This class object will be used to represent a Block on the board.
    (laser interactions with specific block type included in laser.py)
    """

    symbol = "placeholder_symbol"
    name = "placeholder_block"

    def __init__(self, fixed=False):
        """
        Initialize a Block object and define its position as fixed or variable.

        **parameters**
            fixed_pos: *bool*
                If true, block position is fixed.
                If false, block is moveable.
        """
        self.fixed = fixed

    def __repr__(self):
        """
        Returns a string representation of the Block object.
        """
        class_name = type(self).__name__
        return f"{class_name} (fixed={self.fixed})"


class Reflect(Block):
    """
    This class object represents Block type 'A'.
    """
    symbol = "A"
    name = "reflect"


class Opaque(Block):
    """
    This class object represents Block type 'B'.
    """
    symbol = "B"
    name = "opaque"


class Refract(Block):
    """
    This class object represents Block type 'C'.
    """
    symbol = "C"
    name = "refract"


BLOCK_TYPES = {
    "A": Reflect,
    "B": Opaque,
    "C": Refract,
}


def make_block(symbol, fixed=False):
    """
    Makes a block object. Requires block type as an input, and it assumes
    block position is not fixed by default.

    **parameters**
        symbol: *str*
            A, B, or C
        fixed_pos: *bool*
            If true, block position is fixed. If false (default),
            block is moveable.

    **returns**
        A block object

    **raises**
        ValueError: If the symbol is unknown (i.e. not A, B, or C).
    """

    block_class = BLOCK_TYPES.get(symbol)

    if block_class is None:
        raise ValueError(f"Unknown block type: {symbol!r}")

    return block_class(fixed=fixed)
