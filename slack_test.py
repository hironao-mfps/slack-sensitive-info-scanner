import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

print("=== Slack接続テスト ===")

# 環境変数の読み込み
load_dotenv()
token = os.getenv('SLACK_TOKEN')
print(f"1. トークン確認: OK")

# クライアントの初期化
client = WebClient(token=token)

try:
    # 接続テスト
    print("\n2. Slack接続テスト実行中...")
    result = client.auth_test()
    print(f"✅ 接続成功！")
    print(f"- ワークスペース: {result['team']}")
    print(f"- ボット名: {result['bot_id']}")
    
    # チャンネル一覧を取得
    print("\n3. チャンネル一覧取得中...")
    channels = client.conversations_list(types="public_channel")
    print(f"✅ 取得成功！ 合計: {len(channels['channels'])} チャンネル")
    print("\nアクセス可能なチャンネル:")
    for channel in channels['channels']:
        print(f"- #{channel['name']}")

except SlackApiError as e:
    print(f"❌ エラーが発生: {e}")

print("\n=== テスト完了 ===")
