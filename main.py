from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
import shogi

# 駒画像ボタン（押せる画像）
class PieceButton(ButtonBehavior, Image):
    def __init__(self, row, col, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col

    def on_press(self):
        print(f"駒が押されました: ({self.row},{self.col})")

# sfenから盤面の駒リストを作成する関数（前回の完全版）
def sfen_to_piece_list(board):
    sfen = board.sfen()
    piece_list = []

    board_part = sfen.split()[0] if " " in sfen else sfen
    rows = board_part.split("/")

    for row in rows:
        row_list = []
        i = 0
        while i < len(row):
            char = row[i]
            if char.isdigit():
                row_list.extend(["."] * int(char))
                i += 1
            elif char == "+":
                i += 1
                row_list.append("+" + row[i])
                i += 1
            else:
                row_list.append(char)
                i += 1
        while len(row_list) < 9:
            row_list.append(".")
        piece_list.append(row_list)

    return piece_list

# 初期局面
board = shogi.Board()
piece_list = sfen_to_piece_list(board)

# 駒画像辞書
piece_images = {
    "P": "static/image/black_pawn.png",
    "L": "static/image/black_lance.png",
    "N": "static/image/black_knight.png",
    "S": "static/image/black_silver.png",
    "G": "static/image/black_gold.png",
    "K": "static/image/black_king.png",
    "R": "static/image/black_rook.png",
    "B": "static/image/black_bishop.png",
    "+P": "static/image/black_prom_pawn.png",
    "+R": "static/image/black_prom_rook.png",
    "+B": "static/image/black_prom_bishop.png",
    "+S": "static/image/black_prom_silver.png",
    "+N": "static/image/black_prom_knight.png",
    "+L": "static/image/black_prom_lance.png",

    "p": "static/image/white_pawn.png",
    "l": "static/image/white_lance.png",
    "n": "static/image/white_knight.png",
    "s": "static/image/white_silver.png",
    "g": "static/image/white_gold.png",
    "k": "static/image/white_king.png",
    "r": "static/image/white_rook.png",
    "b": "static/image/white_bishop.png",
    "+p": "static/image/white_prom_pawn.png",
    "+r": "static/image/white_prom_rook.png",
    "+b": "static/image/white_prom_bishop.png",
    "+s": "static/image/white_prom_silver.png",
    "+n": "static/image/white_prom_knight.png",
    "+l": "static/image/white_prom_lance.png",

    ".": "static/image/missing.png",
}

class ShogiApp(App):
    def build(self):
        self.root = AnchorLayout(anchor_x="center", anchor_y="center")
        self.board_layout = GridLayout(cols=9, rows=9, spacing=2, size_hint=(None, None))
        self.piece_buttons = []

        for row in range(9):
            for col in range(9):
                piece = piece_list[row][col]
                img_path = piece_images.get(piece, "static/image/missing.png")
                btn = PieceButton(row, col, source=img_path)
                self.board_layout.add_widget(btn)
                self.piece_buttons.append(btn)

        self.root.add_widget(self.board_layout)
        self.root.bind(size=self.update_board)
        self.update_board(self.root, self.root.size)

        return self.root

    def update_board(self, instance, size):
        min_side = min(size)
        self.board_layout.size = (min_side * 0.9, min_side * 0.9)
        btn_size = self.board_layout.width / 9
        for btn in self.piece_buttons:
            btn.size = (btn_size, btn_size)

if __name__ == "__main__":
    ShogiApp().run()