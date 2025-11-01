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


# 評価関数
def evaluate_board(board):
    pass

# 探索部
def search_move(sfen, depth):
    pass # 再起呼び出しでdepth回for文を呼び出し、α・β探索法を用いる