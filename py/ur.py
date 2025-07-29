# BOARD TILES
# +---+---+---+---+       +---+---+
# | 0 | 1 | 2 | 3 | 4   5 | 6 | 7 |
# +---+---+---+---+---+---+---+---+
# | 8 | 9 | 10| 11| 12| 13| 14| 15|
# +---+---+---+---+---+---+---+---+
# | 16| 17| 18| 19| 20  21| 22| 23|
# +---+---+---+---+       +---+---+

# DIE ROLL OUTCOMES
#            [0]            |            [1]
#    0        1        1    |    1        0        0
#  / 0 \    / 0 \    / 0 \  |  / 1 \    / 1 \    / 1 \
# 1 --- 1  0 --- 1  1 --- 0 | 0 --- 0  1 --- 0  0 --- 1
#   (0)      (1)      (2)   |   (3)      (4)      (5)

import random

NUM_TILES = 24
NUM_PIECES = 7
NUM_DICE = 4

P1 = True
P2 = False

P1_PATH = [4, 3, 2, 1, 0, 8, 9, 10, 11, 12, 13, 14, 15, 7, 6, 5]
P2_PATH = [20, 19, 18, 17, 16, 8, 9, 10, 11, 12, 13, 14, 15, 23, 22, 21]

P1_CHARS = ["1", "2", "3", "4", "5", "6", "7"]
P2_CHARS = ["A", "B", "C", "D", "E", "F", "G"]

INVISIBLE_TILES = [4, 5, 20, 21]
ROSETTE_TILES = [0, 6, 11, 16, 22]
SAFE_ROSETTE_TILE = 11

BOARD = """
+---+---+---+---+       +---+---+
| ❁ |   |   |   |       | ❁ |   |
+---+---+---+---+---+---+---+---+
|   |   |   | ❁ |   |   |   |   |
+---+---+---+---+---+---+---+---+
| ❁ |   |   |   |       | ❁ |   |
+---+---+---+---+       +---+---+
"""


class RoyalGameOfUr:
  def __init__(self):
    self.p1_pieces = [P1_PATH[0]] * NUM_PIECES
    self.p2_pieces = [P2_PATH[0]] * NUM_PIECES
    self.dice = [0] * NUM_DICE
    self.turn = P1

  def move(self, piece_idx: int) -> None:
    tile = self.pieces[piece_idx]
    pass

  def roll(self) -> None:
    self.dice = [random.randint(0, 5) for _ in range(NUM_DICE)]

  @property
  def roll_value(self) -> int:
    return sum([1 if d > 2 else 0 for d in self.dice])

  @property
  def pieces(self) -> list[int]:
    return self.p1_pieces if self.turn else self.p2_pieces

  def print_board(self) -> None:
    board_str = BOARD

    for tile in range(NUM_TILES):
      if tile in self.p1_pieces:
        pass
      if tile in self.p2_pieces:
        pass

    print(board_str)
