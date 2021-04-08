"""
To install:

```
pip install chess
```
"""

import chess

print(chess.WHITE) # This is True
print(chess.BLACK) # This is False

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
"""

print(chess.STARTING_BOARD_FEN)
board = chess.Board()
print(board.turn == chess.BLACK)

print([move for move in board.legal_moves])
print("Can white move first?", True if chess.Move.from_uci('a2a4') else False)
print("Is moving D7 to D5 a legal move?", True if chess.Move.from_uci('d7d5') in board.legal_moves else False)
print("Let's advance a pawn. Pushing white pawn D2 to D4:", board.push_uci('d2d4'))
print(board)
print("What are all the legal moves now?\n", [move for move in board.legal_moves])
