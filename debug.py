import os
from dotenv import load_dotenv

print("=== デバッグテスト ===")
print("1. カレントディレクトリ:")
print(os.getcwd())

print("\n2. .envファイルの存在確認:")
print(os.path.exists('.env'))

print("\n3. .envファイルの内容:")
try:
    with open('.env', 'r') as f:
        print(f.read())
except Exception as e:
    print(f"エラー: {e}")

print("\n4. 環境変数読み込みテスト:")
load_dotenv()
token = os.getenv('SLACK_TOKEN')
print(f"トークン: {token if token else '見つかりません'}")
