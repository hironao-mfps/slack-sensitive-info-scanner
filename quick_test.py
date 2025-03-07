import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 環境変数の読み込み
load_dotenv()
token = os.getenv('SLACK_TOKEN')

print("=== Slackボット接続テスト ===")
print(f"1. トークンチェック: {token[:10]}...") # トークンの最初の10文字のみ表示

client = WebClient(token=token)

try:
    # 基本的な接続テスト
    print("\n2. 接続テスト実行中...")
    auth_test = client.auth_test()
    print(f"✅ 認証成功！")
    print(f"- ボット名: {auth_test.get('bot_id')}")
    print(f"- チーム名: {auth_test.get('team')}")
    
    # チャンネル一覧を取得
    print("\n3. チャンネル一覧取得中...")
    channels = client.conversations_list(types="public_channel")
    print(f"✅ 取得成功！ 合計: {len(channels['channels'])} チャンネル")
    
    # チャンネル名を表示
    print("\n4. アクセス可能なチャンネル:")
    for channel in channels['channels']:
        print(f"- #{channel['name']}")

except SlackApiError as e:
    print(f"❌ エラーが発生: {e}")

print("\n=== テスト完了 ===")
