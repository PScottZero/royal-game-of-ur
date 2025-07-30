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

import os
import random
import time
from typing import Optional

NUM_TILES = 24
NUM_PIECES = 7
NUM_DICE = 4

P1 = True
P2 = False

P1_PATH = [4, 3, 2, 1, 0, 8, 9, 10, 11, 12, 13, 14, 15, 7, 6, 5]
P2_PATH = [20, 19, 18, 17, 16, 8, 9, 10, 11, 12, 13, 14, 15, 23, 22, 21]

P1_CHARS = ["1", "2", "3", "4", "5", "6", "7"]
P2_CHARS = ["Q", "W", "E", "R", "T", "Y", "U"]

INVISIBLE_TILES = [4, 5, 20, 21]
ROSETTE_TILES = [0, 6, 11, 16, 22]
SAFE_ROSETTE_TILE = 11

BOARD_STR_WIDTH = 34
BOARD_STR_TILE_WIDTH = 4
BOARD = """
+---+---+---+---+       +---+---+
| * |   |   |   |       | * |   |
+---+---+---+---+---+---+---+---+
|   |   |   | * |   |   |   |   |
+---+---+---+---+---+---+---+---+
| * |   |   |   |       | * |   |
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
    path_idx = self.path.index(tile)
    next_idx = path_idx + self.roll_value
    next_tile = self.path[next_idx]
    self.pieces[piece_idx] = next_tile

    # if piece lands on opponent's piece, reset
    # opponents piece to beginning
    if next_tile in self.opponent_pieces:
      opponent_piece_idx = self.opponent_pieces.index(next_tile)
      self.opponent_pieces[opponent_piece_idx] = self.opponent_path[0]

    # when a player moves a piece onto a rosette tile,
    # they get to roll again
    if next_tile not in ROSETTE_TILES:
      self.turn = not self.turn

  def can_move_piece(self, piece_idx: int) -> bool:
    tile = self.pieces[piece_idx]

    # cannot move piece that has already been scored
    if tile == self.path[-1]:
      return False

    path_idx = self.path.index(tile)
    next_idx = path_idx + self.roll_value

    # piece must roll the exact amount of spaces left
    # in order to leave the board
    if next_idx >= len(self.path):
      return False

    next_tile = self.path[next_idx]

    # piece cannot land on the player's other pieces
    if next_tile != self.path[-1] and next_tile in self.pieces:
      return False

    # piece cannot land on opponent's piece if its on
    # the rosette in the center of the board
    if next_tile == SAFE_ROSETTE_TILE and next_tile in self.opponent_pieces:
      return False

    return True

  def roll(self) -> None:
    self.dice = [random.randint(0, 5) for _ in range(NUM_DICE)]

  @property
  def roll_value(self) -> int:
    return sum([1 if d > 2 else 0 for d in self.dice])

  @property
  def pieces(self) -> list[int]:
    return self.p1_pieces if self.turn else self.p2_pieces

  @property
  def opponent_pieces(self) -> list[int]:
    return self.p2_pieces if self.turn else self.p1_pieces

  @property
  def movable_pieces(self) -> list[int]:
    used = [i for i, tile in enumerate(self.pieces) if tile != self.path[0]]
    unused = [i for i, tile in enumerate(self.pieces) if tile == self.path[0]]
    available = used + ([unused[0]] if unused else [])
    return [i for i in available if self.can_move_piece(i)]

  @property
  def p1_unused_pieces(self) -> list[int]:
    return [i for i, tile in enumerate(self.p1_pieces) if tile == P1_PATH[0]]

  @property
  def p2_unused_pieces(self) -> list[int]:
    return [i for i, tile in enumerate(self.p2_pieces) if tile == P2_PATH[0]]

  @property
  def path(self) -> list[int]:
    return P1_PATH if self.turn else P2_PATH

  @property
  def opponent_path(self) -> list[int]:
    return P2_PATH if self.turn else P1_PATH

  @property
  def p1_score(self) -> int:
    return len(
      [i for i, tile in enumerate(self.p1_pieces) if tile == P1_PATH[-1]]
    )

  @property
  def p2_score(self) -> int:
    return len(
      [i for i, tile in enumerate(self.p2_pieces) if tile == P2_PATH[-1]]
    )

  @property
  def winner(self) -> Optional[bool]:
    p1_won = True
    for piece_tile in self.p1_pieces:
      if piece_tile != P1_PATH[-1]:
        p1_won = False
        break
    if p1_won:
      return P1

    p2_won = True
    for piece_tile in self.p1_pieces:
      if piece_tile != P1_PATH[-1]:
        p2_won = False
        break
    if p2_won:
      return P2

    return None

  def print_board(self) -> None:
    board_str = BOARD

    for tile in range(NUM_TILES):
      if tile in INVISIBLE_TILES:
        continue
      ch = ""
      if tile in self.p1_pieces:
        piece_idx = self.p1_pieces.index(tile)
        ch = P1_CHARS[piece_idx]
      if tile in self.p2_pieces:
        piece_idx = self.p2_pieces.index(tile)
        ch = P2_CHARS[piece_idx]
      if ch:
        row_offset = (2 * (tile // 8) + 1) * BOARD_STR_WIDTH
        col_offset = (tile % 8) * BOARD_STR_TILE_WIDTH + 2
        board_idx = row_offset + col_offset + 1
        board_str = board_str[:board_idx] + ch + board_str[board_idx + 1 :]

    print(board_str)


def run():
  game = RoyalGameOfUr()
  while True:
    os.system("clear")

    game.print_board()

    print("::::::::::: Game Info :::::::::::")
    unused_p1_pieces = [P1_CHARS[i] for i in game.p1_unused_pieces]
    print(f"P1: {game.p1_score} {unused_p1_pieces}")
    unused_p2_pieces = [P2_CHARS[i] for i in game.p2_unused_pieces]
    print(f"P2: {game.p2_score} {unused_p2_pieces}\n")

    if game.winner is not None:
      print(f"!!!!!!!!!!!! P{'1' if game.winner else '2'} Wins !!!!!!!!!!!!\n")
      break

    print(f">>>>>>>>>>> P{'1' if game.turn else '2'}'s Turn <<<<<<<<<<<")

    game.roll()
    print(f"Roll: {game.roll_value}")
    chars = P1_CHARS if game.turn else P2_CHARS
    movable = [chars[p] for p in game.movable_pieces]
    print(f"Movable: {movable}")
    if not movable:
      print("No Moves!")
      time.sleep(1.5)
      game.turn = not game.turn
      continue

    while True:
      ch = input("Enter Piece: ").strip().upper()
      if ch in movable:
        break
    piece_idx = chars.index(ch)
    curr_player = game.turn
    game.move(piece_idx)

    if game.turn == curr_player:
      print(f"P{'1' if game.turn else '2'} Goes Again!")
      time.sleep(1.5)


def test_path():
  game = RoyalGameOfUr()

  print("START")
  game.print_board()

  while True:
    game.roll()
    if game.can_move_piece(0):
      game.move(0)
      game.turn = P1
    print(f"ROLLED {game.roll_value}")
    game.print_board()
    if game.p1_pieces[0] == P1_PATH[-1]:
      break


def test_collision():
  game = RoyalGameOfUr()
  game.p1_pieces[0] = SAFE_ROSETTE_TILE - 3
  game.p1_pieces[1] = SAFE_ROSETTE_TILE - 1
  game.p2_pieces[0] = SAFE_ROSETTE_TILE - 2
  game.p2_pieces[1] = SAFE_ROSETTE_TILE
  game.print_board()

  for i in range(NUM_DICE + 1):
    game.dice = ([5] * i) + ([0] * (NUM_DICE - i))
    print(game.roll_value, game.can_move_piece(0))


run()
