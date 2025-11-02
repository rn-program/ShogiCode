# MyAI.pyx
# cython: language_level=3

import shogi

# --- 評価用クラス ---
cdef class ShogiAI:
    cdef dict piece_value_dict

    def __init__(self, dict piece_value_dict):
        self.piece_value_dict = piece_value_dict

    cpdef int evaluate(self, list piece_list):
        """駒の合計点で盤面を評価"""
        cdef int total = 0
        cdef str piece
        for piece in piece_list:
            total += self.piece_value_dict.get(piece, 0)
        return total

# --- 盤面を駒リストに変換 (持ち駒は含まない) ---
cpdef list board_to_piece_list(object board):
    cdef list piece_list = []
    cdef int square
    cdef object piece
    for square in shogi.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            piece_list.append(piece.symbol())
    return piece_list

# --- 持ち駒をリストに変換 ---
cpdef list board_to_hand_list(object board):
    cdef list hand_list = []
    cdef int piece_type, count, i

    # 先手
    for piece_type, count in board.pieces_in_hand[shogi.BLACK].items():
        for i in range(count):
            hand_list.append(shogi.PIECE_SYMBOLS[piece_type])

    # 後手
    for piece_type, count in board.pieces_in_hand[shogi.WHITE].items():
        for i in range(count):
            hand_list.append(shogi.PIECE_SYMBOLS[piece_type].lower())

    return hand_list

# --- 盤面＋持ち駒を合計評価 ---
cpdef int evaluate_board(object board, dict piece_value_dict, bint turn):
    """turn=Trueなら先手、Falseなら後手"""
    cdef ShogiAI ai = ShogiAI(piece_value_dict)
    cdef list pieces = board_to_piece_list(board)
    pieces += board_to_hand_list(board)
    cdef int val = ai.evaluate(pieces)
    if not turn:
        val = -val
    return val

# --- 静止探索（quiescence search） ---
cpdef int quiescence(object board, int alpha, int beta, dict piece_value_dict, bint turn, int depth=0):
    cdef int stand_pat = evaluate_board(board, piece_value_dict, turn)
    cdef object move
    cdef int score

    # βカット
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    # 駒取りの手のみ延長
    for move in board.legal_moves:
        if board.piece_at(move.to_square) is None:
            continue
        board.push(move)
        score = -quiescence(board, -beta, -alpha, piece_value_dict, not turn, depth + 1)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

# --- αβ探索（最良手付き） ---
cpdef tuple explore_moves(object board,
                          int depth,
                          bint turn=True,
                          double alpha=-1e9,
                          double beta=1e9,
                          bint maximizing=True,
                          int ply=0):
    cdef dict piece_value_dict = {
        "P": 1, "L": 5, "N": 5, "S": 7, "G": 8,
        "B": 10, "R": 12, "+P": 2, "+L": 6, "+N": 6,
        "+S": 9, "+B": 15, "+R": 18,
        "p": -1, "l": -5, "n": -5, "s": -7, "g": -8,
        "b": -10, "r": -12, "+p": -2, "+l": -6,
        "+n": -6, "+s": -9, "+b": -15, "+r": -18
    }

    cdef double value
    cdef object best_move = None
    cdef object move
    cdef tuple child_result

    if depth == 0 or board.is_game_over():
        return quiescence(board, int(alpha), int(beta), piece_value_dict, turn), None

    if maximizing:
        value = -1e9
        for move in board.legal_moves:
            board.push(move)
            child_result = explore_moves(board, depth - 1, not turn, alpha, beta, False, ply + 1)
            board.pop()

            if child_result[0] > value:
                value = child_result[0]
                best_move = move

            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value, best_move
    else:
        value = 1e9
        for move in board.legal_moves:
            board.push(move)
            child_result = explore_moves(board, depth - 1, not turn, alpha, beta, True, ply + 1)
            board.pop()

            if child_result[0] < value:
                value = child_result[0]
                best_move = move

            beta = min(beta, value)
            if beta <= alpha:
                break
        return value, best_move

# --- 最良手取得 ---
cpdef object get_best_move(object board, int depth, bint turn=True):
    return explore_moves(board, depth, turn)[1]