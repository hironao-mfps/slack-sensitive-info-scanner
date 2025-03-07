from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
import schedule
import time
import re

# 環境変数の読み込み
load_dotenv()

# Slackアプリの初期化
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# センシティブ情報のパターン
PATTERNS = {
    'メールアドレス': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    '電話番号': r'\b\d{2,4}[-\s]?\d{2,4}[-\s]?\d{4}\b',
    'クレジットカード': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    '住所': r'[東西南北]?\d+条[東西南北]?\d+丁目|〒\d{3}-\d{4}'
}

def create_alert_channel():
    try:
        # security-alertsチャンネルの作成を試みる
        try:
            response = app.client.conversations_create(name="security-alerts")
            print("security-alertsチャンネルを作成しました")
            return response["channel"]["id"]
        except Exception as e:
            if "name_taken" in str(e):
                # チャンネルが既に存在する場合、一覧から探す
                result = app.client.conversations_list(types="public_channel")
                for channel in result["channels"]:
                    if channel["name"] == "security-alerts":
                        print("既存のsecurity-alertsチャンネルを使用します")
                        return channel["id"]
            else:
                raise e
    except Exception as e:
        print(f"アラートチャンネルの作成/取得でエラーが発生: {str(e)}")
        return None

def join_all_channels():
    try:
        # チャンネル一覧の取得
        result = app.client.conversations_list(types="public_channel,private_channel")
        channels = result["channels"]
        
        # 全チャンネルに参加
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
    if not alert_channel_id:
        print("アラートチャンネルIDが設定されていません")
        return

    try:
        app.client.chat_postMessage(
            channel=alert_channel_id,
            text="全チャンネルのスキャンを開始します..."
        )

        result = app.client.conversations_list(types="public_channel,private_channel")
        channels = result["channels"]
        found_sensitive_info = False
        
        for channel in channels:
            try:
                if channel["name"] == "security-alerts":
                    continue
                
                app.client.chat_postMessage(
                    channel=alert_channel_id,
                    text=f"チャンネル #{channel['name']} のスキャンを開始..."
                )
                
                history = app.client.conversations_history(channel=channel["id"])
                
                for message in history["messages"]:
                    if "text" not in message:
                        continue
                        
                    for pattern_name, pattern in PATTERNS.items():
                        matches = re.finditer(pattern, message["text"])
                        for match in matches:
                            found_sensitive_info = True
                            # メッセージへのパーマリンクを取得
                            try:
                                permalink = app.client.chat_getPermalink(
                                    channel=channel["id"],
                                    message_ts=message["ts"]
                                )
                                message_link = permalink["permalink"]
                            except Exception as e:
                                message_link = "リンクの取得に失敗しました"

                            # 検出情報の通知（リンク付き）
                            app.client.chat_postMessage(
                                channel=alert_channel_id,
                                text=f"警告: #{channel['name']} チャンネルで{pattern_name}を検出しました。\n"
                                     f"検出場所: {message_link}\n"
                                     f"投稿時刻: <!date^{int(float(message['ts']))}^{{date}} {{time}}|{message['ts']}>"
                            )
                
            except Exception as e:
                app.client.chat_postMessage(
                    channel=alert_channel_id,
                    text=f"#{channel['name']} チャンネルのスキャン中にエラーが発生: {str(e)}"
                )

        if not found_sensitive_info:
            app.client.chat_postMessage(
                channel=alert_channel_id,
                text="スキャン完了: 全チャンネルでセンシティブ情報は検出されませんでした。"
            )

    except Exception as e:
        print(f"スキャン処理でエラーが発生: {str(e)}")

def scheduled_task():
    # アラートチャンネルの作成/取得
    alert_channel_id = create_alert_channel()
    if not alert_channel_id:
        print("アラートチャンネルの作成/取得に失敗しました")
        return

    # 全チャンネルに参加
    join_all_channels()
    
    # スキャンの実行
    perform_scan(alert_channel_id)

# スラッシュコマンドの追加
@app.command("/scan")
def handle_scan_command(ack, say):
    ack()
    say("全チャンネルのスキャンを開始します...")
    scheduled_task()

# メンション対応の追加
@app.event("app_mention")
def handle_mention(event, say):
    if "スキャン" in event["text"]:
        say("全チャンネルのスキャンを開始します...")
        scheduled_task()

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    
    print("初回スキャンを開始します...")
    scheduled_task()
    
    # 毎日午前9時に実行するようにスケジュール
    schedule.every().day.at("09:00").do(scheduled_task)
    
    print("定期スキャンをスケジュールしました（毎日午前9時）")
    
    handler.start()
    
    while True:
        schedule.run_pending()
        time.sleep(60) 