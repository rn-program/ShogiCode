import random


# boardからsfenに変換する関数
def sfen_to_piece_list(board):
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


# 玉の堅さを評価するクラス


# 評価関数
def evaluate_board(board):
    pass


# 探索部
def search_move(sfen, depth):
    pass  # 再起呼び出しでdepth回for文を呼び出し、α・β探索法を用いる


# 指し手指示
def get_best_move(board):
    legal_moves_list = list(board.legal_moves)
    if not legal_moves_list == []:
        return random.choice(legal_moves_list)
    else:
        print("投了")
        return