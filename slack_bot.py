from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# アプリの初期化
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# 簡単なテストコマンド
@app.command("/hello")
def hello(ack, say):
    ack()
    say("こんにちは！")

# メイン処理
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
