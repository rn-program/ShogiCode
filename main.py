from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
import shogi

# 将棋盤・局面情報などの定義
board = shogi.Board()
board_sfen_list = str(board).split()

# 将棋盤のcellボタン一つを定義
class CellButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
    
    def on_size(self, *args):
        # 幅と高さを同じにして正方形にする
        self.height = self.width

# 将棋盤の表示
class ShogiApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=10)
        layout = GridLayout(cols=9, rows=9, spacing=2, size_hint=(1, None))
        layout.bind(minimum_height=layout.setter('height'))

        # セルボタンの追加
        for row in range(9):
            for col in range(9):
                btn = CellButton(
                    text=f"{row},{col}",
                )             
                btn.bind(on_press=self.on_button_press)
                layout.add_widget(btn)

        root.add_widget(layout)
        return root
    
    # セルボタンが押された時の処理
    def on_button_press(self, instance):
        instance.text = "pressed"

if __name__ == "__main__":
    ShogiApp().run()