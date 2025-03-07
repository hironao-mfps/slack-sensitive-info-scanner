import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

print("=== チャンネル参加スクリプト ===")

# 環境変数の読み込み
load_dotenv()
client = WebClient(token=os.getenv('SLACK_TOKEN'))

try:
    # チャンネル一覧を取得
    print("1. チャンネル一覧を取得中...")
    channels = client.conversations_list(types="public_channel")
    
    print(f"\n2. 合計 {len(channels['channels'])} チャンネルに参加を試みます...")
    for channel in channels['channels']:
        try:
            result = client.conversations_join(channel=channel['id'])
            print(f"✅ #{channel['name']} に参加しました")
        except SlackApiError as e:
            if e.response['error'] == 'already_in_channel':
                print(f"ℹ️ #{channel['name']} には既に参加しています")
            else:
                print(f"❌ #{channel['name']} への参加に失敗: {e.response['error']}")

except SlackApiError as e:
    print(f"エラー: {e}")

print("\n=== 完了 ===")
