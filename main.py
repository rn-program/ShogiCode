from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, Line
import ctypes
import shogi

# --- ライブラリ読み込み ---
lib = ctypes.CDLL("./ShogiAI.dll")

lib.add.argtypes = (ctypes.c_int, ctypes.c_int)
lib.add.restype = ctypes.c_int

# 駒ボタン
class PieceButton(ButtonBehavior, Image):
    def __init__(self, row, col, source=None, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.piece = None
        self.highlighted = False  # ←ハイライト中かどうかの状態

        # 空マスの場合、画像は設定しない
        if source:
            self.source = source

        # マスの背景色を描画
        with self.canvas.before:
            if (row + col) % 2 == 0:
                Color(0.95, 0.85, 0.7, 1)  # 明るい木目
            else:
                Color(0.85, 0.7, 0.5, 1)   # 少し濃い木目
            self.rect = Rectangle(pos=self.pos, size=self.size)

        # ハイライト用（初期はNone）
        self.highlight_line = None

        # ボタンサイズ・位置変更時に背景を更新
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if self.highlight_line:
            # ハイライトの位置も更新
            self.highlight_line.rectangle = (
                self.pos[0],
                self.pos[1],
                self.size[0],
                self.size[1],
            )

    def on_press(self):
        global selectedPiece

        col, row = self.col, self.row
        self.piece = piece_list[row][col]

        # 駒を選択した場合、赤枠をトグル表示
        if self.highlighted:
            self.remove_highlight()
            selectedPiece = None
        else:
            # ほかのマスのハイライトを全部解除
            for btn in app_ref.piece_buttons:
                btn.remove_highlight()
            # この駒をハイライト
            self.add_highlight()
            selectedPiece = CoorsToUSI(col, row)
        print(f"選択されたマス: {selectedPiece}")

    def add_highlight(self):
        self.highlighted = True
        with self.canvas.after:
            Color(1, 0, 0, 1)  # 赤
            self.highlight_line = Line(
                rectangle=(
                    self.pos[0],
                    self.pos[1],
                    self.size[0],
                    self.size[1],
                ),
                width=3,
            )

    def remove_highlight(self):
        if self.highlighted and self.highlight_line:
            self.canvas.after.remove(self.highlight_line)
            self.highlight_line = None
        self.highlighted = False


# (col,row)座標をUSI形式に変換する関数
def CoorsToUSI(col, row):
    colToAlpha = {
        0: "a",
        1: "b",
        2: "c",
        3: "d",
        4: "e",
        5: "f",
        6: "g",
        7: "h",
        8: "i",
    }
    return str(9 - col) + colToAlpha[row]


# SFENから盤面リストを作成する関数
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

# 駒を選んでいるかの情報を持つ変数
selectedPiece = None
selectedHandPiece = None

# 駒画像辞書（透過PNG想定）
piece_images = {
    # 黒（先手）
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
    # 白（後手）
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
}


class ShogiApp(App):
    def build(self):
        global app_ref
        app_ref = self  # 他クラスから参照できるように
        self.root = AnchorLayout(anchor_x="center", anchor_y="center")
        self.board_layout = GridLayout(cols=9, rows=9, spacing=2, size_hint=(None, None))
        self.piece_buttons = []

        # 駒ボタン作成
        for row in range(9):
            for col in range(9):
                piece = piece_list[row][col]
                if piece == ".":
                    btn = PieceButton(row, col)  # 空マスは画像なし
                else:
                    img_path = piece_images.get(piece)
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
    try:
        ShogiApp().run()
    except KeyboardInterrupt:
        print("アプリを終了しました。")