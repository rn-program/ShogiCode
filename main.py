from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
import shogi


# -------------------------
# 駒ボタンクラス
# -------------------------
class PieceButton(ButtonBehavior, Image):
    def __init__(self, row, col, source=None, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.piece = None
        self.highlighted = False
        self.promotion_buttons = []

        # サイズ固定でタッチイベント対応
        self.size_hint = (None, None)
        self.size = (50, 50)

        if source:
            self.source = source

        # マス背景
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
        global selectedPiece, piece_list, turn

        col, row = self.col, self.row
        self.piece = piece_list[row][col]

        print(f"on_press: row={row}, col={col}, piece={self.piece}")

        if self.piece == "." and selectedPiece is None:
            return

        if selectedPiece is None and (
            (turn == 0 and self.piece.islower()) or (turn == 1 and self.piece.isupper())
        ):
            print("この手番では選択できません")
            return

        if self.highlighted:
            self.remove_highlight()
            selectedPiece = None
        else:
            for btn in app_ref.piece_buttons:
                btn.remove_highlight()
                btn.remove_promotion_buttons()

            # 移動処理
            if selectedPiece is not None:
                departure, destination = selectedPiece, CoorsToUSI(col, row)
                usi_normal = departure + destination
                usi_promote = departure + destination + "+"

                legal_usi = [m.usi() for m in board.legal_moves]
                normal_legal = usi_normal in legal_usi
                promote_legal = usi_promote in legal_usi

                if normal_legal and promote_legal:
                    self.show_promotion_buttons(departure, destination)
                    return
                elif promote_legal:
                    move_to_play = shogi.Move.from_usi(usi_promote)
                elif normal_legal:
                    move_to_play = shogi.Move.from_usi(usi_normal)
                else:
                    print(f"反則手: {usi_normal}")
                    selectedPiece = None
                    return

                handle_capture(move_to_play)
                board.push(move_to_play)
                update_board_and_buttons()
                selectedPiece = None
            else:
                selectedPiece = CoorsToUSI(col, row)
                self.add_highlight()

    def show_promotion_buttons(self, departure, destination):
        self.remove_promotion_buttons()
        btn_size = self.size[0] / 2

        btn_promote = Button(
            text="成",
            font_size=18,
            font_name="static/NotoSansJP-Regular.ttf",
            size_hint=(None, None),
            size=(btn_size, btn_size * 0.7),
            pos=(
                self.pos[0] + self.size[0] - btn_size,
                self.pos[1] + self.size[1] - btn_size * 0.7,
            ),
            background_color=(1, 0.6, 0.6, 1),
        )
        btn_normal = Button(
            text="不成",
            font_size=18,
            font_name="static/NotoSansJP-Regular.ttf",
            size_hint=(None, None),
            size=(btn_size, btn_size * 0.7),
            pos=(self.pos[0], self.pos[1] + self.size[1] - btn_size * 0.7),
            background_color=(0.6, 0.8, 1, 1),
        )

        def promote_action(instance):
            global selectedPiece
            move = shogi.Move.from_usi(departure + destination + "+")
            handle_capture(move)
            board.push(move)
            self.remove_promotion_buttons()
            update_board_and_buttons()
            selectedPiece = None
            for btn in app_ref.piece_buttons:
                btn.remove_highlight()

        def normal_action(instance):
            global selectedPiece
            move = shogi.Move.from_usi(departure + destination)
            handle_capture(move)
            board.push(move)
            self.remove_promotion_buttons()
            update_board_and_buttons()
            selectedPiece = None
            for btn in app_ref.piece_buttons:
                btn.remove_highlight()

        btn_promote.bind(on_press=promote_action)
        btn_normal.bind(on_press=normal_action)

        app_ref.root.add_widget(btn_promote)
        app_ref.root.add_widget(btn_normal)
        self.promotion_buttons.extend([btn_promote, btn_normal])

    def remove_promotion_buttons(self):
        for b in self.promotion_buttons:
            if b.parent:
                b.parent.remove_widget(b)
        self.promotion_buttons = []

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
# (col,row) → USI
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
    for row in board_part.split("/"):
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
# 盤面更新
# -------------------------
def update_board_and_buttons():
    global turn, piece_list
    piece_list[:] = sfen_to_piece_list(board)
    for btn in app_ref.piece_buttons:
        piece = piece_list[btn.row][btn.col]
        btn.source = "" if piece == "." else piece_images[piece]
    turn = 0 if board.turn == shogi.BLACK else 1
    update_holding_area()


# -------------------------
# 持ち駒管理
# -------------------------
holding_pieces = {0: [], 1: []}


def handle_capture(move):
    """
    move: shogi.Move
    board.push(move) の前に呼ぶ
    """
    # 移動先の駒を取得
    captured_piece = board.piece_at(move.to_square)
    if captured_piece:
        # 現手番と逆が持ち駒に追加
        holder = 0 if board.turn == shogi.BLACK else 1
        piece_symbol = captured_piece.symbol()  # 文字列
        piece_symbol = piece_symbol.replace("+", "")  # 成駒を元に戻す
        piece_symbol = piece_symbol.upper() if holder == 0 else piece_symbol.lower()
        holding_pieces[holder].append(piece_symbol)


def update_holding_area():
    app_ref.top_captures.clear_widgets()
    app_ref.bottom_captures.clear_widgets()
    for p in holding_pieces[0]:
        img = Image(source=piece_images[p], size_hint=(None, None), size=(30, 30))
        app_ref.top_captures.add_widget(img)
    for p in holding_pieces[1]:
        img = Image(source=piece_images[p], size_hint=(None, None), size=(30, 30))
        app_ref.bottom_captures.add_widget(img)


# -------------------------
# 初期設定
# -------------------------
board = shogi.Board()
piece_list = sfen_to_piece_list(board)
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
        self.root = FloatLayout()

        # 上側持ち駒表示エリア
        self.top_captures = BoxLayout(
            size_hint=(1, 0.1), pos_hint={"top": 1}, spacing=2, padding=5
        )
        # 下側持ち駒表示エリア
        self.bottom_captures = BoxLayout(
            size_hint=(1, 0.1), pos_hint={"y": 0}, spacing=2, padding=5
        )
        self.root.add_widget(self.top_captures)
        self.root.add_widget(self.bottom_captures)

        # 盤面
        self.board_container = AnchorLayout(
            anchor_x="center", anchor_y="center", size_hint=(1, 0.8)
        )
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

        self.board_container.add_widget(self.board_layout)
        self.root.add_widget(self.board_container)

        self.root.bind(size=self.update_board)
        self.update_board(self.root, self.root.size)
        update_holding_area()
        return self.root

    def update_board(self, instance, size):
        min_side = min(size[0], size[1] * 0.8)
        self.board_layout.size = (min_side, min_side)
        btn_size = self.board_layout.width / 9
        for btn in self.piece_buttons:
            btn.size = (btn_size, btn_size)


# -------------------------
# 起動
# -------------------------
if __name__ == "__main__":
    ShogiApp().run()
