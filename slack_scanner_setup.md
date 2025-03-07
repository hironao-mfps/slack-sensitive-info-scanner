# Slack センシティブ情報スキャンボット セットアップガイド

## 1. 準備作業

### 1.1 Slackアプリの作成
1. https://api.slack.com/apps にアクセス
2. 「Create New App」→「From scratch」を選択
3. アプリ名とワークスペースを設定

### 1.2 権限の設定
1. 「OAuth & Permissions」で以下の権限を追加：
- channels:history
- channels:read
- channels:join

### 1.3 アプリのインストール
App Manifestの設定:
```json
{
    "display_information": {
        "name": "slack_personal information_check"
    },
    "features": {
        "bot_user": {
            "display_name": "slack_personal information_check",
            "always_online": false
        }
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "channels:history",
                "channels:read",
                "channels:join"
            ]
        }
    },
    "settings": {
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```

## 2. 環境構築

### 2.1 必要なライブラリのインストール
```bash
pip3 install slack-sdk python-dotenv
```

### 2.2 環境変数の設定
```bash
# .envファイルの作成
echo 'SLACK_TOKEN=xoxb-あなたのボットトークン' > .env
```

## 3. スクリプトファイル

### 3.1 チャンネル参加スクリプト (join_channels.py)
```python
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
```

### 3.2 スキャナースクリプト (scanner.py)
```python
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
```

## 4. 実行手順

1. ボットをチャンネルに参加させる：
```bash
python3 join_channels.py
```

2. スキャンを実行：
```bash
python3 scanner.py
```

## 5. 確認ポイント
- すべてのチャンネルにアクセスできているか
- センシティブ情報が正しく検出されているか
- エラーが発生していないか

## 6. カスタマイズオプション
- 定期実行の設定
- 通知機能の追加
- 検出パターンの追加/カスタマイズ
