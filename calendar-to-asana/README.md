# Googleカレンダー → Asana自動タスク登録ツール

Googleカレンダーから特定アカウントの予定を取得し、Asanaのマイタスクに期限を当日設定で自動登録するツールです。

## 機能

- 指定されたGoogleカレンダーの予定を取得
- 特定のメールアドレスで参加している予定のみをフィルタ
- Asanaのマイタスク（他の人から見えないプライベートエリア）にタスクを作成
- 期限を当日に設定
- 毎朝6:00に自動実行（macOSのlaunchdを使用）

## セットアップ

### 1. 依存関係のインストール

```bash
# portfolioディレクトリから実行（zoom-recorder-webにいる場合は親ディレクトリに移動）
cd ../calendar-to-asana
# または絶対パスで移動
cd "/Users/yamatokitada/マイドライブ（yamato.kitada@cyan-inc.net）/Cursor/portfolio/calendar-to-asana"

# pip3を使用（pipが見つからない場合）
pip3 install -r requirements.txt
# または
python3 -m pip install -r requirements.txt
```

### 2. Google Calendar APIの設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Google Calendar APIを有効化
3. OAuth 2.0認証情報を作成（デスクトップアプリ）
4. 認証情報をダウンロードして`credentials.json`として保存

### 3. Asana APIの設定

1. [Asana Developer Console](https://app.asana.com/0/my-apps)でアプリを作成
2. Personal Access Tokenを生成
3. ワークスペースGIDを取得（Asana APIで確認）

### 4. 環境変数の設定

`.env`ファイルを作成：

```bash
# Google Calendar
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
CALENDAR_EMAIL=your-email@example.com  # チェックするカレンダーのメールアドレス

# Asana
ASANA_ACCESS_TOKEN=your-asana-access-token
ASANA_WORKSPACE_GID=your-workspace-gid
```

### 5. 初回認証

```bash
# calendar-to-asanaディレクトリにいることを確認
python3 main.py
```

初回実行時にGoogle認証のブラウザが開きます。認証を完了してください。

### 6. 自動実行の設定（macOS）

`setup_launchd.sh`を実行：

```bash
chmod +x setup_launchd.sh
./setup_launchd.sh
```

または手動で設定する場合：

1. `com.calendar-to-asana.plist`ファイル内の`REPLACE_WITH_FULL_PATH_TO_MAIN_PY`を実際のパスに置き換え
2. plistファイルを`~/Library/LaunchAgents/`にコピー
3. `launchctl load ~/Library/LaunchAgents/com.calendar-to-asana.plist`で読み込み

## PCが起動していない場合の運用

macOSのlaunchdはPCが起動している必要があります。PCが起動していない場合でも実行するには、以下の方法があります：

### 方法1: クラウドサービスを使用（推奨）

- AWS Lambda + EventBridge
- Google Cloud Functions + Cloud Scheduler
- Azure Functions + Timer Trigger

これらのサービスを使用すると、PCが起動していなくても毎朝6:00に実行されます。

### 方法2: 常時起動しているサーバーを使用

- Raspberry Pi
- クラウドサーバー（AWS EC2、Google Compute Engineなど）

## 手動実行

```bash
# calendar-to-asanaディレクトリに移動してから実行
cd calendar-to-asana
python3 main.py
```

## ログ確認

```bash
# launchdのログ
tail -f /tmp/calendar-to-asana.log
tail -f /tmp/calendar-to-asana-error.log
```

## トラブルシューティング

### Google認証エラー

- `credentials.json`が正しいパスに配置されているか確認
- OAuth 2.0認証情報が正しく作成されているか確認

### Asana認証エラー

- Personal Access Tokenが正しく設定されているか確認
- ワークスペースGIDが正しいか確認

### 予定が取得できない

- `CALENDAR_EMAIL`が正しく設定されているか確認
- カレンダーへのアクセス権限があるか確認
