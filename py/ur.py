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

import math
import os
import random
import time
from typing import Optional

MAX_DEPTH = 10

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

  def copy(self) -> "RoyalGameOfUr":
    new_game = RoyalGameOfUr()
    new_game.p1_pieces = list(self.p1_pieces)
    new_game.p2_pieces = list(self.p2_pieces)
    new_game.dice = list(self.dice)
    new_game.turn = self.turn
    return new_game

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
    first_unused = [self.unused_pieces[0]] if self.unused_pieces else []
    available = self.used_pieces + first_unused
    return [i for i in available if self.can_move_piece(i)]

  @property
  def used_pieces(self) -> list[int]:
    return [i for i in range(NUM_PIECES) if i not in self.unused_pieces]

  @property
  def unused_pieces(self) -> list[int]:
    return self.p1_unused_pieces if self.turn else self.p2_unused_pieces

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
    return sum(map(lambda tile: tile == P1_PATH[-1], self.p1_pieces))

  @property
  def p2_score(self) -> int:
    return sum(map(lambda tile: tile == P2_PATH[-1], self.p2_pieces))

  @property
  def winner(self) -> Optional[bool]:
    if self.p1_pieces.count(P1_PATH[-1]) == NUM_PIECES:
      return P1
    if self.p2_pieces.count(P2_PATH[-1]) == NUM_PIECES:
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


def get_computer_move(initial_node: RoyalGameOfUr) -> int:
  if len(initial_node.movable_pieces) == 1:
    return initial_node.movable_pieces[0]
  return alphabeta(initial_node, 0, -math.inf, math.inf)[0]


def alphabeta(
  node: RoyalGameOfUr,
  depth: int,
  alpha: float,
  beta: float,
) -> tuple[int, float]:
  node_value = node.p1_score - node.p2_score

  if node.winner is not None or depth == MAX_DEPTH:
    return 0, node_value

  best_move: tuple[int, float] = (0, -math.inf if node.turn == P1 else math.inf)

  for pieceIdx in node.movable_pieces:
    next_node = node.copy()
    next_node.move(pieceIdx)
    result = alphabeta(next_node, depth + 1, alpha, beta)
    result = (pieceIdx, result[1])

    if node.turn == P1:
      best_move = max(result, best_move, key=lambda x: x[1])
      if best_move[1] >= beta:
        break
      alpha = max(alpha, best_move[1])
    else:
      best_move = min(result, best_move, key=lambda x: x[1])
      if best_move[1] <= alpha:
        break
      beta = min(beta, best_move[1])

  return best_move


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

    if game.turn == P1:
      while True:
        ch = input("Enter Piece: ").strip().upper()
        if ch in movable:
          break
      piece_idx = chars.index(ch)
    else:
      print("Computer Is Deciding Move...")
      piece_idx = get_computer_move(game)
      print(f"Computer Moved {chars[piece_idx]}")
      time.sleep(1.5)

    curr_player = game.turn
    game.move(piece_idx)

    if game.turn == curr_player:
      print(f"P{'1' if game.turn else '2'} Goes Again!")
      time.sleep(1.5)


run()
