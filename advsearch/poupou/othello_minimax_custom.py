from typing import Tuple
from ..othello.board import Board
from .minimax import minimax_move

MAX_DEPTH = 4

# cada quina (linha, coluna) -> a casa na diagonal dela ("X-square")
CORNERS = {(0, 0): (1, 1), (0, 7): (1, 6), (7, 0): (6, 1), (7, 7): (6, 6)}

def make_move(state) -> Tuple[int, int]:
    """
    Returns a move for the given game state
    :param state: state to make the move
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """

    return minimax_move(state, MAX_DEPTH, evaluate_custom)


def evaluate_custom(state, player:str) -> float:
    """
    Evaluates an othello state from the point of view of the given player. 
    If the state is terminal, returns its utility. 
    If non-terminal, returns an estimate of its value based on your custom heuristic
    :param state: state to evaluate (instance of GameState)
    :param player: player to evaluate the state for (B or W)
    """

    board = state.board
    opponent = Board.opponent(player)

    if state.is_terminal():
        diff = board.num_pieces(player) - board.num_pieces(opponent)
        
        if diff > 0:
            return 1000
        
        if diff < 0:
            return -1000
        
        return 0

    corners = 0
    x_squares = 0
    for (r, c), (xr, xc) in CORNERS.items():
        corner = board.tiles[r][c]

        if corner == player:
            corners += 1
        elif corner == opponent:
            corners -= 1
        elif board.tiles[xr][xc] == player:
            x_squares -= 1
        elif board.tiles[xr][xc] == opponent:
            x_squares += 1

    # mobilidade: quantas jogadas eu tenho a mais que o oponente
    mobility = len(board.legal_moves(player)) - len(board.legal_moves(opponent))

    return 10 * corners + 5 * x_squares + mobility
