import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import re

# 環境変数の読み込み
load_dotenv()
client = WebClient(token=os.getenv('SLACK_TOKEN'))

# 検索パターン
patterns = {
    "メールアドレス": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
    "電話番号": r'(\d{2,4})-?(\d{2,4})-?(\d{3,4})',
    "クレジットカード": r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',
    "住所": r'〒?\d{3}-?\d{4}',
}

print("=== Slackメッセージスキャン開始 ===")

try:
    channels = client.conversations_list(types="public_channel")
    for channel in channels['channels']:
        print(f"\nチャンネル #{channel['name']} をスキャン中...")
        
        try:
            messages = client.conversations_history(channel=channel['id'])
            message_count = len(messages['messages'])
            print(f"- メッセージ数: {message_count}")
            
            found = False
            for message in messages['messages']:
                if 'text' in message:
                    for pattern_name, pattern in patterns.items():
                        matches = re.findall(pattern, message['text'])
                        if matches:
                            found = True
                            print(f"! 検出: {pattern_name}")
                            print(f"  メッセージ: {message['text'][:50]}...")
            
            if not found:
                print("- センシティブ情報なし")
                
        except SlackApiError as e:
            print(f"エラー: {e}")

except SlackApiError as e:
    print(f"エラー: {e}")

print("\n=== スキャン完了 ===")
