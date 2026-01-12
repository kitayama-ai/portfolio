# Zoom自動録画ツール

Zoom会議の録画と議事録を自動生成するWebアプリケーションです。

## 機能

- ✅ Zoom会議の自動検知
- ✅ 録画 + 文字起こし / 文字起こしのみの選択
- ✅ OpenAI Whisper APIによる高精度な文字起こし（日本語対応）
- ✅ GPT-4o-miniによる議事録自動生成
- ✅ Slackへの自動通知
- ✅ Googleドキュメントへの自動保存（オプション）
- ✅ 録画ファイルとドキュメントの自動分離保存
- ✅ 会議終了時の自動停止
- ✅ マルチユーザー対応（認証機能付き）

## セットアップ

### 1. 依存パッケージのインストール

```bash
cd zoom-recorder-web
pip install -r requirements.txt
```

### 2. 環境変数の設定

プロジェクトルートに`.env`ファイルを作成し、以下の環境変数を設定してください：

```env
# OpenAI API（必須）
OPENAI_API_KEY=sk-...

# Slack（オプション）
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#meeting-notes

# JWT秘密鍵（本番環境では強力なランダム文字列に変更してください）
SECRET_KEY=your-secret-key-change-in-production
```

### 3. macOSの場合の追加設定

BlackHoleのインストールが必要です。以下のコマンドで自動インストールできます：

```bash
cd zoom-recorder-web
./install_blackhole.sh
```

または、Homebrewがインストールされている場合：

```bash
brew install blackhole-2ch
```

インストール後、システム環境設定 > サウンド > 出力 で BlackHole 2ch を選択してください。

### 4. サーバーの起動

#### 方法1: GUIアプリから起動（推奨・一般ユーザー向け）

```bash
python3 installer/server_launcher.py
```

「サーバーを起動」ボタンをクリックすると、自動的にブラウザが開きます。

#### 方法2: コマンドラインから起動

```bash
cd backend
python3 main.py
```

サーバーは `http://localhost:8000` で起動します。

他のPCからアクセスする場合は、サーバーPCのIPアドレスを使用：
`http://[サーバーPCのIPアドレス]:8000`

### 5. エージェントのセットアップ（各PC・オプション）

**注意**: 現在の実装では、サーバーと同じPCで録画を実行します。他のPCから録画する場合は、エージェントを各PCにインストールしてください。

各PCでエージェントを起動：

```bash
python3 agent/agent.py --server http://サーバーIP:8000 --token agent_secret_token
```

または、GUIアプリから起動：

```bash
python3 agent/agent_launcher.py
```

## 使用方法

1. ブラウザで `http://サーバーIP:8000` にアクセス
2. 新規登録またはログイン
3. Zoomで会議に参加
4. 「録画開始」ボタンをクリック
5. 会議終了時に自動停止（オプション有効時）
6. 自動で文字起こし→議事録生成→Slack通知

## 設定

- **録画フォルダ**: 録画ファイル（MP4）の保存先
- **ドキュメントフォルダ**: 議事録（テキスト）の保存先
- **Googleドキュメント**: 自動保存を有効化（オプション）

## コスト

- Whisper API: $0.006/分
- GPT-4o-mini: 約$0.001/回
- 1時間の会議: 約$0.36

## 注意事項

- macOSの場合、BlackHoleのインストールが必要です：
  ```bash
  brew install blackhole-2ch
  ```
- システム環境設定 > サウンド > 出力 で BlackHole 2ch を選択してください
- 録画ファイルは25MB以下である必要があります

## ライセンス

MIT License
