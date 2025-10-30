from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, Line
import shogi


# -------------------------
# 駒ボタン
# -------------------------
class PieceButton(ButtonBehavior, Image):
    def __init__(self, row, col, source=None, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.piece = None
        self.highlighted = False

        if source:
            self.source = source

        # マスの背景色
        with self.canvas.before:
            if (row + col) % 2 == 0:
                Color(0.95, 0.85, 0.7, 1)
            else:
                Color(0.85, 0.7, 0.5, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.highlight_line = None
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if self.highlight_line:
            self.highlight_line.rectangle = (
                self.pos[0],
                self.pos[1],
                self.size[0],
                self.size[1],
            )

    def on_press(self):
        global selectedPiece, piece_list, legal_moves_list, turn

        col, row = self.col, self.row
        self.piece = piece_list[row][col]

        # 空マスは、駒選択中でない場合押せない
        if self.piece == "." and selectedPiece is None:
            return

        # 手番でない駒は、駒選択中でない場合押せない
        if selectedPiece is None and (
            (turn == 0 and self.piece.islower()) or (turn == 1 and self.piece.isupper())
        ):
            print("この手番では選択できません")
            return

        # ハイライトトグル
        if self.highlighted:
            self.remove_highlight()
            selectedPiece = None
        else:
            # 他のハイライト解除
            for btn in app_ref.piece_buttons:
                btn.remove_highlight()

            if selectedPiece is not None:
                # 移動先選択
                depature, destination = selectedPiece, CoorsToUSI(col, row)

                # 成り判定を含む合法手検索
                move_candidates = [
                    m
                    for m in board.legal_moves
                    if m.usi().startswith(depature) and m.usi().endswith(destination)
                ]

                if not move_candidates:
                    print(f"反則手: {depature + destination}")
                    selectedPiece = None
                    return

                # 自動的に成れる手を選択
                print(f"move_candidates={move_candidates}")
                move_to_play = move_candidates[0]
                print(f"move_to_play={move_to_play}")
                # 成る手があれば自動で成る
                board.push(move_to_play)
                update_board_and_buttons()
                print(board.sfen())
                selectedPiece = None
            else:
                # 駒を選択
                selectedPiece = CoorsToUSI(col, row)
                self.add_highlight()
                print(f"選択されたマス: {selectedPiece}")

    def add_highlight(self):
        self.highlighted = True
        with self.canvas.after:
            Color(1, 0, 0, 1)
            self.highlight_line = Line(
                rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]),
                width=3,
            )

    def remove_highlight(self):
        if self.highlighted and self.highlight_line:
            self.canvas.after.remove(self.highlight_line)
            self.highlight_line = None
        self.highlighted = False


# -------------------------
# (col,row) → USI座標
# -------------------------
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


# -------------------------
# SFEN → 盤面リスト
# -------------------------
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


# -------------------------
# 盤面とボタン更新
# -------------------------
def update_board_and_buttons():
    global turn, piece_list, legal_moves_list
    piece_list[:] = sfen_to_piece_list(board)
    legal_moves_list[:] = [m.usi() for m in board.legal_moves]
    for btn in app_ref.piece_buttons:
        piece = piece_list[btn.row][btn.col]
        btn.source = "" if piece == "." else piece_images[piece]
    turn = 1 - turn
    print(f"次の手番: {'先手' if turn==0 else '後手'}")


# -------------------------
# 初期設定
# -------------------------
board = shogi.Board()
piece_list = sfen_to_piece_list(board)
legal_moves_list = [m.usi() for m in board.legal_moves]
selectedPiece = None
turn = 0

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
}


# -------------------------
# アプリ本体
# -------------------------
class ShogiApp(App):
    def build(self):
        global app_ref
        app_ref = self
        self.root = AnchorLayout(anchor_x="center", anchor_y="center")
        self.board_layout = GridLayout(
            cols=9, rows=9, spacing=2, size_hint=(None, None)
        )
        self.piece_buttons = []

        for row in range(9):
            for col in range(9):
                piece = piece_list[row][col]
                btn = PieceButton(
                    row, col, source="" if piece == "." else piece_images[piece]
                )
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


# -------------------------
# 起動
# -------------------------
if __name__ == "__main__":
    ShogiApp().run()
