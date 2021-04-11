"""
To install:
```
pip install chess
```
"""

import chess
import numpy as np

print(chess.WHITE) # This is True
print(chess.BLACK) # This is False

class BoardTiles:
    """
    Boards start at, from the left corner from the player playing White,
    A1, moving horizontally along the letters and vertically away from the 
    player along the numbers.
    The first square is black, and alternates white, black, white, etc. from 
    there.
    Parameters
    ----------
    black : OBJ
    white : OBJ
    black_selectable : OBJ
    white_selectable : OBJ
    """
    LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8]
    def __init__(self, black, white, black_selectable, white_selectable, 
                 black_pieces, white_pieces, dist):
        self.board = chess.Board()
        self._black = black
        self._white = white
        self._black_sel = black_selectable
        self._white_sel = white_selectable
        self.black_pieces = black_pieces
        self.white_pieces = white_pieces
        # self.board_obj = np.array([[black, white] * 4,
        #                        [white, black] * 4] * 4)
        self.dist = dist
        self.active_tile = None

    def uci_to_rc(self, uci: str):
        """
        A string in uci notation, e.g. 'c4', 'a2', etc.
        Returns
        -------
        row, col : int, int
            The zero-indexed row and column of the tile.
        """
        col = self.LETTERS.index(uci[0])
        row = self.NUMBERS.index(int(uci[1]))
        return row, col

    def set_active_tile(self, square):
        self.active_tile = square

    def deactivate_tiles(self):
        self.active_tile = None

    def possible_move(self, square):
        if self.active_tile is not None:
            if square in [move.to_square for move in self.board.legal_moves if move.from_square == self.active_tile]:
                return True
        else: 
            return False

    def bw(self, row, col):
        """
        Returns True if square is White, False if square is Black.
        Parameters
        ----------
        row : int
            0-indexed row.
        col : int
            0-indexed column.
        Example
        -------
        >>> b.bw(1,1) == chess.BLACK
        True
        """
        if row % 2: # row starts with white
            if col % 2:
                return chess.BLACK
            else:
                return chess.WHITE
        else: # row starts with black
            if col % 2:
                return chess.WHITE
            else:
                return chess.BLACK

    def get_tiles(self):
        square = 0
        for row in range(8):
            for col in range(8):
                dx = row * self.dist
                dy = col * self.dist
                if self.possible_move(square):
                    if self.bw(row, col) == chess.BLACK:
                        yield dx, dy, self._black_sel
                    else:
                        yield dx, dy, self._white_sel
                else:
                    if self.bw(row, col) == chess.BLACK:
                        yield dx, dy, self._black
                    else:
                        yield dx, dy, self._white
                    # yield dx, dy, self.board_obj[row, col]
                square += 1

    def get_pieces(self):
        locs = str(self.board).splitlines()
        for row in range(7, -1, -1):
            col = 0
            for piece in locs[row].split():
                piecename = self.piece_by_identifier(piece.lower())
                if piecename is None:
                    yield None, None, None
                dx = (7-row) * self.dist
                dy = col * self.dist
                if piece.isupper():
                    yield dx, dy, self.white_pieces[piecename]
                else:
                    yield dx, dy, self.black_pieces[piecename]
                col += 1

    def piece_by_identifier(self, identifier):
        if identifier == 'r':
            return 'rook'
        elif identifier == 'n':
            return 'knight'
        elif identifier == 'b':
            return 'bishop'
        elif identifier == 'q':
            return 'queen'
        elif identifier == 'k':
            return 'king'
        elif identifier == 'p':
            return 'pawn'
        elif identifier == '.':
            return None



if __name__ == "__main__":
    """
    >>> print(board)
    r n b q k b n r
    p p p p p p p p
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    P P P P P P P P
    R N B Q K B N R
    White is capitals, black is lowercase. White moves first.
    Board positions are named as follows:
    A B C D E F G H
    8 o   o   o   o 
    7   o   o   o   o
    6 o   o   o   o  
    5   o   o   o   o
    4 o   o   o   o 
    3   o   o   o   o
    2 o   o   o   o  
    1   o   o   o   o
    Squares are also numbered like so:
    A B C D E F G  H
    8|      ...    62 63
    7| 
    6|        .       .
    5|       .        .
    4|      .         .
    3| 
    2| 
    1| 1 2 3 4 5 6 7  8
    """

    print(chess.STARTING_BOARD_FEN)
    board = chess.Board()
    print(board.turn == chess.BLACK)

    print([move for move in board.legal_moves])
    print("Can white move first?", True if chess.Move.from_uci('a2a4') else False)
    print("Is moving D7 to D5 a legal move?", True if chess.Move.from_uci('d7d5') in board.legal_moves else False)
    print("Let's advance a pawn. Pushing white pawn D2 to D4:", board.push_uci('d2d4'))
    print(board)
    moves = [move for move in board.legal_moves]
    print("What are all the legal moves now?\n", moves)
    print(f"The next first legal move is from {moves[0].from_square} to {moves[0].to_square}, also known as {chess.square_name(moves[0].from_square)} and {chess.square_name(moves[0].to_square)}")
    print("So, if we know what piece we'd like to move next, we can gather all legal moves for that piece (like this black knight):", [move for move in board.legal_moves if move.from_square == 62])


    bt = BoardTiles('b ', 'w ', 'bs', 'ws', 5)
    gen = bt.get_tiles()
    for row in range(8):
        r = [next(gen)[2] for col in range(8)]
        print(r)

    print()
    bt.set_active_tile(1)
    gen = bt.get_tiles()
    for row in range(8):
        r = [next(gen)[2] for col in range(8)]
        print(r)

    def possible_move(self, square, active_tile, board):
            if active_tile is not None:
                if square in [move.to_square for move in board.legal_moves if move.from_square == active_tile]:
                    return True
            else: 
                return False

    board = chess.Board()
    row, col = bt.uci_to_rc('e2')
    ind = row*8+col
    active_tile = ind
    print(f"moves: {[move.to_square for move in board.legal_moves if move.from_square == active_tile]}")
    print(board)