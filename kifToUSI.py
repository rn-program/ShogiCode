import shogi
import shogi.KIF

# --- KIFファイルを読み込む ---
parser = shogi.KIF.Parser()
records = parser.parse_str(open("static/kif/001.kif", encoding="utf-8").read())

# --- 棋譜を処理 ---
for record in records:
    print("初期局面:", record["sfen"])
    print("指し手:", record["moves"])