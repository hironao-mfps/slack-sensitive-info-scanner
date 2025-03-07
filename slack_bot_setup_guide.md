# Slack センシティブ情報スキャナー セットアップマニュアル

## 1. Slack アプリの作成と設定

### 1.1 アプリの作成
1. [Slack API](https://api.slack.com/apps) にアクセス
2. "Create New App" をクリック
3. "From scratch" を選択
4. App Name: `slack_personal information_check` を入力
5. ワークスペースを選択して "Create App" をクリック

### 1.2 基本設定
1. 左メニューから "Socket Mode" を選択
2. "Enable Socket Mode" をオン
3. App-Level Token の名前を `scanner_token` として生成
   - スコープ: `connections:write` を追加

### 1.3 権限の設定
1. 左メニューから "OAuth & Permissions" を選択
2. "Bot Token Scopes" で以下の権限を追加：
   - `channels:history`
   - `channels:read`
   - `channels:join`
   - `chat:write`
   - `commands`
   - `app_mentions:read`
   - `channels:manage`
   - `groups:read`
   - `groups:write`
   - `mpim:write`
   - `im:write`

### 1.4 スラッシュコマンドの設定
1. 左メニューから "Slash Commands" を選択
2. "Create New Command" をクリック
3. 以下の情報を入力：
   - Command: `/scan`
   - Description: `チャンネル内の機密情報をスキャン`
   - Usage Hint: `スキャンを開始`

### 1.5 イベントの設定
1. 左メニューから "Event Subscriptions" を選択
2. "Enable Events" をオン
3. "Subscribe to bot events" で `app_mention` を追加

### 1.6 アプリのインストール
1. 左メニューから "Install App" を選択
2. "Install to Workspace" をクリック
3. 認証を承認

## 2. 環境設定

### 2.1 必要なライブラリのインストール
```bash
pip3 install slack-bolt python-dotenv schedule
```

### 2.2 環境変数の設定
1. .envファイルを作成：
```bash
SLACK_BOT_TOKEN=xoxb-あなたのBotトークン
SLACK_APP_TOKEN=xapp-あなたのAppトークン
```

トークンは以下の場所で確認できます：
- Bot Token: "OAuth & Permissions" ページの "Bot User OAuth Token"
- App Token: "Basic Information" ページの "App-Level Tokens"

## 3. ボットの実行

### 3.1 スキャナーの起動
```bash
python3 scheduled_scanner.py
```

### 3.2 使用方法
1. 手動スキャン：
   - スラッシュコマンド: `/scan`
   - メンション: `@slack_personal information_check スキャン`

2. 自動スキャン：
   - 毎日午前9時に自動実行
   - 結果は `#security-alerts` チャンネルに通知

### 3.3 検出項目
- メールアドレス
- 電話番号
- クレジットカード番号
- 住所

## 4. トラブルシューティング

### 4.1 よくあるエラー
1. `invalid_auth`: トークンの再確認が必要
2. `missing_scope`: 必要な権限が不足
3. `channel_not_found`: チャンネルへのアクセス権限がない

### 4.2 対処方法
1. トークンの再確認
2. アプリの再インストール
3. 権限の追加と更新
