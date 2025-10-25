from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
import shogi

# sfenから盤面の駒リストを作成する関数
def sfen_to_piece_list(board):
    sfen = board.sfen()
    piece_list = []
    board_part = sfen.split()[0] if ' ' in sfen else sfen
    rows = board_part.split('/')

    for row in rows:
        row_list = []
        i = 0
        while i < len(row):
            char = row[i]
            if char.isdigit():
                # 数字はその数だけ空マスを追加
                row_list.extend(['.'] * int(char))
                i += 1
            elif char == '+':
                # 成り駒の場合、次の文字と組み合わせて1要素に
                i += 1
                row_list.append('+' + row[i])
                i += 1
            else:
                row_list.append(char)
                i += 1
        # 最後に必ず9個の要素になるよう確認（不足分は空マスで埋める）
        while len(row_list) < 9:
            row_list.append('.')
        piece_list.append(row_list)

    return piece_list

# 局面(shogi.Board())から(row,col)の駒名を取得する関数
def get_piece(board, row, col, piece_list):
    return piece_list[row][col]

# 初期局面の定義
board = shogi.Board()
sfen = board.sfen()

piece_list = sfen_to_piece_list(board)

class ShogiApp(App):
    def build(self):
        # 盤を画面中央に配置
        self.root = AnchorLayout(anchor_x='center', anchor_y='center')

        # 将棋盤の作成・表示
        self.board_layout = GridLayout(cols=9, rows=9, spacing=2, size_hint=(None, None))
        self.buttons = []
        
        for i in range(81):
            btn = Button(
                text='',
                size_hint=(None, None),
                background_normal=self.piece_image,  # 通常表示の画像
                background_down=self.piece_image     # 押した時の画像
            )
            self.piece_image = "static/image/"
            self.board_layout.add_widget(btn)
            self.buttons.append(btn)

        self.root.add_widget(self.board_layout)

        # 画面サイズに応じてセルの大きさを調整
        self.root.bind(size=self.update_board)
        self.update_board(self.root, self.root.size)  # 初期サイズ調整

        return self.root

    def update_board(self, instance, size):
        # ルートの幅と高さのうち小さい方に合わせる
        min_side = min(size)
        self.board_layout.size = (min_side * 0.9, min_side * 0.9)  # 余白10%
        
        # 各ボタンを正方形に調整
        btn_size = self.board_layout.width / 9
        for btn in self.buttons:
            btn.size = (btn_size, btn_size)

if __name__ == "__main__":
    ShogiApp().run()