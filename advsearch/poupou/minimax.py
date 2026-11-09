from typing import Tuple, Callable

def minimax_move(state, max_depth:int, eval_func:Callable) -> Tuple[int, int]:
    """
    Returns a move computed by the minimax algorithm with alpha-beta pruning for the given game state.
    :param state: state to make the move (instance of GameState)
    :param max_depth: maximum depth of search (-1 = unlimited)
    :param eval_func: the function to evaluate a terminal or leaf state (when search is interrupted at max_depth)
                    This function should take a GameState object and a string identifying the player,
                    and should return a float value representing the utility of the state for the player.
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """
    me = state.player

    def value(s, depth, alpha, beta) -> float:
        if s.is_terminal() or depth == max_depth:
            return eval_func(s, me)

        # since we othello could lead to two turns in a row, compare with root player
        maximizing = s.player == me
        best = float('-inf') if maximizing else float('inf')

        for move in s.legal_moves():
            v = value(s.next_state(move), depth + 1, alpha, beta)
            if maximizing:
                best = max(best, v)
                alpha = max(alpha, best)
            else:
                best = min(best, v)
                beta = min(beta, best)
            if alpha >= beta:
                break

        return best

    best_move, alpha = None, float('-inf')

    for move in state.legal_moves():
        v = value(state.next_state(move), 1, alpha, float('inf'))
        if v > alpha or best_move is None:
            best_move, alpha = move, v

    return best_move