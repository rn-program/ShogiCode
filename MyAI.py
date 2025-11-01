import random
import shogi

# boardからpiece_listに変換する関数
def board_to_piece_list(board):
    sfen = board.sfen()
    piece_list = []
    board_part = sfen.split()[0]

    for row in board_part.split("/"):
        row_list = []
        i = 0
        while i < len(row):
            c = row[i]
            if c.isdigit():
                row_list.extend(["."] * int(c))
                i += 1
            elif c == "+":
                i += 1
                row_list.append("+" + row[i])
                i += 1
            else:
                row_list.append(c)
                i += 1

        while len(row_list) < 9:
            row_list.append(".")
        piece_list.append(row_list)

    return piece_list


# 駒の損得を計算するクラス
class piece_value:
    def __init__(self, piece_value_dict, weight):
        """piece_value_dict = {
            0: {}, 先手
            1: {}  後手
        }
        """
        self.piece_value_dict = piece_value_dict
        self.weight = weight

    def evaluate(self, piece_list):
        total_piece_value = 0
        for piece in piece_list:
            total_piece_value += self.piece_value_dict.get(piece, 0)
        return total_piece_value


# 駒の位置評価するクラス
class piece_position:
    def __init__(self, position_value_dict, weight):
        self.position_value_dict = position_value_dict
        self.weight = weight

    def evaluate(self, piece_list):
        total_position_value = 0
        for i in range(81):
            total_position_value += self.position_value_dict[piece_list[i]][i]
        return total_position_value


""" 玉の堅さを評価するクラス
class king_safety:
    def __init__(self, position_value_dict, weight):
        self.position_value_dict = position_value_dict
        self.weight = weight
"""

# 将棋AI(評価関数)クラス
class ShogiAI(piece_value, piece_position):
    def evaluate_board(self, piece_list):
        pass
        
# 探索部
def explore_moves(board, depth):
    if depth == 0:
        # evaluate_board(board.sfen)
        print(board.sfen())  # 例: 現在の盤面を表示
        return

    for move in list(board.legal_moves):
        board.push(move)       # 手を指す
        explore_moves(board, depth - 1)  # 次の深さを探索 (処理が終わるまで盤面は戻されない)
        board.pop()            # 手を戻す（必ずpopすることが重要）
        
board = shogi.Board()
explore_moves(board, 5)

# 指し手指示
def get_best_move(board):
    legal_moves_list = list(board.legal_moves)
    if not legal_moves_list == []:
        return random.choice(legal_moves_list)
    else:
        print("投了")
