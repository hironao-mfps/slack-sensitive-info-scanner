from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
import schedule
import time
import re
import sys

# デバッグ出力を有効化
import logging
logging.basicConfig(level=logging.DEBUG)

# 環境変数の読み込み
load_dotenv()

# 環境変数の確認
print(f"SLACK_BOT_TOKEN: {'設定されています' if os.environ.get('SLACK_BOT_TOKEN') else '設定されていません'}")
print(f"SLACK_APP_TOKEN: {'設定されています' if os.environ.get('SLACK_APP_TOKEN') else '設定されていません'}")

# Slackアプリの初期化
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# センシティブ情報のパターン
PATTERNS = {
    "メールアドレス": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "電話番号": r"\b\d{2,4}[-\s]?\d{2,4}[-\s]?\d{4}\b",
    "クレジットカード": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "住所": r"[東西南北]?\d+条[東西南北]?\d+丁目|〒\d{3}-\d{4}"
}

def create_alert_channel():
    """security-alertsチャンネルの作成または取得"""
    try:
        try:
            response = app.client.conversations_create(name="security-alerts")
            print("security-alertsチャンネルを作成しました")
            return response["channel"]["id"]
        except Exception as e:
            if "name_taken" in str(e):
                result = app.client.conversations_list(types="public_channel")
                for channel in result["channels"]:
                    if channel["name"] == "security-alerts":
                        print("既存のsecurity-alertsチャンネルを使用します")
                        return channel["id"]
            raise e
    except Exception as e:
        print(f"アラートチャンネルの作成/取得でエラーが発生: {str(e)}")
        return None

def join_all_channels():
    """全チャンネルに参加"""
    try:
        result = app.client.conversations_list(types="public_channel,private_channel")
        channels = result["channels"]
        
        for channel in channels:
            try:
                if not channel["is_member"]:
                    app.client.conversations_join(channel=channel["id"])
                    print(f"チャンネル {channel['name']} に参加しました")
            except Exception as e:
                print(f"チャンネル {channel['name']} への参加に失敗: {str(e)}")
    except Exception as e:
        print(f"チャンネル参加処理でエラーが発生: {str(e)}")

def perform_scan(alert_channel_id):
    """チャンネル内のセンシティブ情報をスキャン"""
    if not alert_channel_id:
        print("アラートチャンネルIDが設定されていません")
        return

    try:
        # スキャン開始通知
        app.client.chat_postMessage(
            channel=alert_channel_id,
            text="全チャンネルのスキャンを開始します..."
        )

        # チャンネル一覧の取得とスキャン
        result = app.client.conversations_list(types="public_channel,private_channel")
        channels = result["channels"]
        found_sensitive_info = False
        
        for channel in channels:
            try:
                if channel["name"] == "security-alerts":
                    continue
                
                history = app.client.conversations_history(channel=channel["id"])
                
                for message in history["messages"]:
                    if "text" not in message:
                        continue
                        
                    # パターンマッチング
                    for pattern_name, pattern in PATTERNS.items():
                        matches = re.finditer(pattern, message["text"])
                        for match in matches:
                            found_sensitive_info = True
                            try:
                                permalink = app.client.chat_getPermalink(
                                    channel=channel["id"],
                                    message_ts=message["ts"]
                                )
                                message_link = permalink["permalink"]
                            except Exception as e:
                                message_link = "リンクの取得に失敗しました"

                            # 検出通知
                            app.client.chat_postMessage(
                                channel=alert_channel_id,
                                text=f"警告: #{channel['name']} チャンネルで{pattern_name}を検出しました。\n"
                                     f"検出場所: {message_link}"
                            )
                
            except Exception as e:
                app.client.chat_postMessage(
                    channel=alert_channel_id,
                    text=f"#{channel['name']} チャンネルのスキャン中にエラーが発生: {str(e)}"
                )

        # スキャン結果の通知
        if not found_sensitive_info:
            app.client.chat_postMessage(
                channel=alert_channel_id,
                text="スキャン完了: 全チャンネルでセンシティブ情報は検出されませんでした。"
            )

    except Exception as e:
        print(f"スキャン処理でエラーが発生: {str(e)}")

def scheduled_task():
    """定期実行タスク"""
    try:
        print("定期タスクを実行します...")
        alert_channel_id = create_alert_channel()
        if not alert_channel_id:
            print("アラートチャンネルの作成/取得に失敗しました")
            return

        join_all_channels()
        perform_scan(alert_channel_id)
    except Exception as e:
        print(f"定期タスクでエラーが発生: {str(e)}")

# スラッシュコマンドハンドラ
@app.command("/scan")
def handle_scan_command(ack, say):
    ack()
    say("全チャンネルのスキャンを開始します...")
    scheduled_task()

# メンションハンドラ
@app.event("app_mention")
def handle_mention(event, say):
    if "スキャン" in event["text"]:
        say("全チャンネルのスキャンを開始します...")
        scheduled_task()

if __name__ == "__main__":
    try:
        # Socket Modeハンドラの初期化
        print("Socket Modeハンドラを初期化します...")
        handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
        
        print("初回スキャンを開始します...")
        scheduled_task()
        
        # 定期実行のスケジュール設定
        schedule.every().day.at("09:00").do(scheduled_task)
        print("定期スキャンをスケジュールしました（毎日午前9時）")
        
        # Socket Mode開始
        print("Socket Modeを開始します...")
        handler.start()
        
        # スケジューラーのメインループ
        print("メインループを開始します...")
        while True:
            schedule.run_pending()
            time.sleep(60)
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        sys.exit(1)
