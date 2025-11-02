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


# --- 盤面を駒リストに変換 (持ち駒は含まない) ---
def board_to_piece_list(board):
    """盤上の駒をリストに変換"""
    piece_list = []
    for square in shogi.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_list.append(piece.symbol())
    return piece_list


# --- 持ち駒をリストに変換 ---
def board_to_hand_list(board):
    """先手・後手の持ち駒をまとめてリストに変換"""
    hand_list = []

    # 先手の持ち駒
    for p in board.pieces_in_hand[shogi.BLACK]:
        hand_list.append(p.symbol())
    # 後手の持ち駒
    for p in board.pieces_in_hand[shogi.WHITE]:
        hand_list.append(p.symbol().lower())  # 後手は小文字

    return hand_list


# --- 盤面＋持ち駒を合計評価する関数 ---
def evaluate_board(board, piece_value_dict):
    """盤上駒＋持ち駒で評価値を返す"""
    ai = ShogiAI(piece_value_dict)
    pieces = board_to_piece_list(board)
    pieces += board_to_hand_list(board)  # 持ち駒も含める
    return ai.evaluate(pieces)


# --- 静止探索（quiescence search） ---
def quiescence(board, alpha, beta, piece_value_dict, depth=0):
    stand_pat = evaluate_board(board, piece_value_dict)

    indent = "    " * depth
    print(f"{indent}Q探索 深さ{depth}: 評価={stand_pat}, α={alpha}, β={beta}")

    # βカット
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    # 駒取りの手のみ延長探索
    for move in board.legal_moves:
        if board.piece_at(move.to_square) is None:
            continue

        board.push(move)
        score = -quiescence(board, -beta, -alpha, piece_value_dict, depth + 1)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


# --- αβ探索（最良手付き） ---
def explore_moves(
    board, depth, alpha=-float("inf"), beta=float("inf"), maximizing=True, ply=0
):
    indent = "    " * ply

    # 評価辞書
    piece_value_dict = {
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

    if depth == 0 or board.is_game_over():
        value = quiescence(board, alpha, beta, piece_value_dict)
        return value, None

    best_move = None

    if maximizing:
        value = -float("inf")
        for move in board.legal_moves:
            board.push(move)
            child_value, _ = explore_moves(
                board, depth - 1, alpha, beta, False, ply + 1
            )
            board.pop()

            if child_value > value:
                value = child_value
                best_move = move

            alpha = max(alpha, value)
            if beta <= alpha:
                break

        return value, best_move
    else:
        value = float("inf")
        for move in board.legal_moves:
            board.push(move)
            child_value, _ = explore_moves(board, depth - 1, alpha, beta, True, ply + 1)
            board.pop()

            if child_value < value:
                value = child_value
                best_move = move

            beta = min(beta, value)
            if beta <= alpha:
                break

        return value, best_move


def get_best_move(board, depth):
    return explore_moves(board, depth)[1]


# --- 使用例 ---
if __name__ == "__main__":
    board = shogi.Board()
    depth = 3
    value, best_move = explore_moves(board, depth)

    print(f"\n探索結果の評価値: {value}")
    if best_move:
        print(f"AIが選んだ最良手: {best_move.usi()}")
    else:
        print("指せる手がありません。")
