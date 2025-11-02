import shogi


# --- 評価用クラス ---
class ShogiAI:
    def __init__(self, piece_value_dict):
        self.piece_value_dict = piece_value_dict

    def evaluate(self, piece_list):
        """駒の合計点で盤面を評価"""
        total = 0
        for piece in piece_list:
            total += self.piece_value_dict.get(piece, 0)
        return total


# --- 盤面を駒リストに変換 ---
def board_to_piece_list(board):
    """盤上の駒をリストに変換"""
    piece_list = []
    for square in shogi.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_list.append(piece.symbol())
    return piece_list


# --- αβ探索（最良手付き） ---
def explore_moves(
    board, depth, alpha=-float("inf"), beta=float("inf"), maximizing=True
):
    """
    αβ探索（再帰）
    戻り値: (評価値, 最良手)
    """
    # --- 評価辞書 ---
    piece_value_dict = {
        # 先手（大文字） → 正の値
        "P": 1,
        "L": 5,
        "N": 5,
        "S": 7,
        "G": 8,
        "B": 10,
        "R": 12,
        "+P": 2,
        "+L": 6,
        "+N": 6,
        "+S": 9,
        "+B": 15,
        "+R": 18,
        # 後手（小文字） → 負の値
        "p": -1,
        "l": -5,
        "n": -5,
        "s": -7,
        "g": -8,
        "b": -10,
        "r": -12,
        "+p": -2,
        "+l": -6,
        "+n": -6,
        "+s": -9,
        "+b": -15,
        "+r": -18,
    }

    # --- 終端条件 ---
    if depth == 0 or board.is_game_over():
        ai = ShogiAI(piece_value_dict)
        piece_list = board_to_piece_list(board)
        return ai.evaluate(piece_list), None  # 手はなし

    best_move = None

    # --- 先手（最大化） ---
    if maximizing:
        value = -float("inf")
        for move in board.legal_moves:
            board.push(move)
            child_value, _ = explore_moves(board, depth - 1, alpha, beta, False)
            board.pop()

            if child_value > value:
                value = child_value
                best_move = move

            alpha = max(alpha, value)
            if beta <= alpha:  # βカット
                break

        return value, best_move

    # --- 後手（最小化） ---
    else:
        value = float("inf")
        for move in board.legal_moves:
            board.push(move)
            child_value, _ = explore_moves(board, depth - 1, alpha, beta, True)
            board.pop()

            if child_value < value:
                value = child_value
                best_move = move

            beta = min(beta, value)
            if beta <= alpha:  # αカット
                break

        return value, best_move

def get_best_move(board, depth):
    return explore_moves(board, depth)[1]

# --- 使用例 ---
if __name__ == "__main__":
    board = shogi.Board()
    depth = 5
    value, best_move = explore_moves(board, depth)

    print(f"探索結果の評価値: {value}")
    if best_move:
        print(f"AIが選んだ最良手: {(best_move.usi)}")
    else:
        print("指せる手がありません。")
