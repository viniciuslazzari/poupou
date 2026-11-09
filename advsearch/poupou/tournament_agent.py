import time
from typing import Tuple
from ..othello.board import Board
from ..othello.gamestate import GameState
from .minimax import minimax_move
from .othello_minimax_custom import evaluate_custom

TIME_BUDGET = 4.0 # segundos, com margem de 1s para o limite

class FasterBoard(Board):
    """Igual ao Board do kit, mas copia sem passar por texto e reaproveita as jogadas ja calculadas."""

    def copy(self):
        new = FasterBoard.__new__(FasterBoard)          # cria o objeto sem rodar o __init__
        new.tiles = [row[:] for row in self.tiles]      # copia cada linha do tabuleiro
        new.piece_count = dict(self.piece_count)
        new._legal_moves = dict(self._legal_moves)      # o tabuleiro e igual, entao as jogadas tambem sao
        new.flipped = set()
        return new

    def has_legal_move(self, color):
        return len(self.legal_moves(color)) > 0         # usa as jogadas ja calculadas

class _Timeout(Exception):
    pass

def make_move(state) -> Tuple[int, int]:
    """
    Returns a move for the given game state. 
    Consider that this will be called in the Othello tournament situation,
    so you should call the best implementation you got.

    :param state: state to make the move
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """

    moves = state.legal_moves()

    if len(moves) == 1:
        return next(iter(moves))

    deadline = time.time() + TIME_BUDGET

    def timed_eval(s, player: str) -> float:
        if time.time() > deadline:
            raise _Timeout()
        
        return evaluate_custom(s, player)

    best = next(iter(moves))
    max_possible_depth = state.board.num_pieces(Board.EMPTY)
    root = GameState(FasterBoard.copy(state.board), state.player) 

    for depth in range(1, max_possible_depth + 1):
        try:
            best = minimax_move(root, depth, timed_eval)
        except _Timeout:
            break

    return best


