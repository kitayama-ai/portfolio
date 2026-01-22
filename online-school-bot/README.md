# オンラインスクールチャットボット

オンラインスクールの教材内容に関する質問に即座に回答するチャットボットシステムです。**Chatwork**と**LINE**の両方のプラットフォームに対応しています。

## 機能

- ✅ **マルチプラットフォーム対応**: ChatworkとLINEの両方に対応
- ✅ **Chatwork Bot連携**: 既存のグループチャットに統合可能、DM対応
- ✅ **LINE Messaging API連携**: コースごとに独立したLINEボット
- ✅ **PDF教材のアップロード・解析**: 管理画面からPDFをアップロードし、自動でベクトル化
- ✅ **AI回答生成**: 教材内容を参照し、必要に応じて最新情報も参照
- ✅ **画像対応**: 画像メッセージを解析して回答生成（LINE対応）
- ✅ **満足度判定**: ユーザーのメッセージ内容から自動で満足度を判定
- ✅ **スプレッドシート記録**: すべての質問・回答をGoogleスプレッドシートに記録
- ✅ **二次回答フロー**: 不満がある場合、Slackで運営スタッフに通知
- ✅ **管理画面**: 会話履歴の閲覧、PDFアップロード、コース管理

## セットアップ

### 1. 依存パッケージのインストール

```bash
cd online-school-bot
pip install -r requirements.txt
```

### 2. 環境変数の設定

プロジェクトルートに`.env`ファイルを作成し、以下の環境変数を設定してください：

```env
# OpenAI API（必須）
OPENAI_API_KEY=sk-...

# Chatwork API（コースごとに設定、推奨）
# コースIDごとに個別のAPIトークンを設定
# ChatworkのAPIトークンは https://www.chatwork.com/service/packages/chatwork/subpackages/api/apply_beta.php で取得
CHATWORK_API_TOKEN_course1=xxx
CHATWORK_API_TOKEN_course2=yyy

# LINE Messaging API（コースごとに設定、オプション）
# コースIDごとに個別のチャネルアクセストークンとシークレットを設定
LINE_CHANNEL_ACCESS_TOKEN_course1=xxx
LINE_CHANNEL_SECRET_course1=yyy
LINE_CHANNEL_ACCESS_TOKEN_course2=xxx
LINE_CHANNEL_SECRET_course2=yyy

# Slack（二次回答通知用）
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#school-support

# Google Sheets（記録用）
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_SPREADSHEET_ID=your-spreadsheet-id

# JWT秘密鍵（本番環境では強力なランダム文字列に変更してください）
SECRET_KEY=your-secret-key-change-in-production
```

### 3. Chatwork APIの設定（推奨・1000人以上対応）

**重要：このボットはDM（1対1のチャット）でのやりとりを想定しています。**

1. [Chatwork API申請ページ](https://www.chatwork.com/service/packages/chatwork/subpackages/api/apply_beta.php)でAPIトークンを申請
2. APIトークンを取得し、環境変数に設定: `CHATWORK_API_TOKEN_{course_id}=xxx`

**1000人以上に対応するため、ポーリング方式を採用しています：**
- Webhookの制約（1アカウントあたり最大5件）を回避するため、**ポーリング方式で未読メッセージを自動取得**します
- サーバー起動時に自動的にポーリングタスクが開始されます
- 30秒ごとに全DMルームの未読メッセージをチェックし、自動的に処理します
- **Webhookの設定は不要です**（ポーリング方式を使用する場合）

**DMルームの作成方法：**
- ユーザーがボットアカウントにDMを送信すると、DMルームが自動的に作成されます
- または、ボットアカウントから各ユーザーにDMを送信してDMルームを作成することもできます
- 作成されたDMルームは自動的にポーリング対象になります

**注意事項：**
- レート制限：Chatwork APIは300リクエスト/5分の制限があります（有料プランでも同じ）
- ポーリング間隔：30秒ごとにチェック（レート制限を考慮）
- 処理済みメッセージは重複処理されません

**重要：有料プランでもWebhook制限は5件まで**
- ChatworkのWebhook制限（1アカウントあたり5件）は、有料プラン（ビジネス・エンタープライズ）でも変わりません
- そのため、1000人以上に対応するにはポーリング方式が必須です

### 4. LINE公式アカウントの設定（オプション）

1. [LINE Developers](https://developers.line.biz/ja/)でプロバイダーを作成
2. 各コースごとにMessaging APIチャネルを作成
3. Webhook URLを設定: `https://your-domain.com/api/webhook/line/{course_id}`
4. チャネルアクセストークンとチャネルシークレットを取得し、環境変数に設定

### 5. Google Sheets APIの設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Google Sheets APIを有効化
3. 認証情報（OAuth 2.0）を作成し、`credentials.json`として保存
4. 初回実行時にブラウザで認証が求められます

### 6. サーバーの起動

```bash
cd backend
python main.py
```

サーバーは `http://localhost:8002` で起動します。

## 使用方法

### 管理画面での操作

1. `http://localhost:8002` にアクセス
2. ログイン（初回はユーザー登録が必要）
3. **コース管理タブ**: コースを登録
4. **PDF教材タブ**: 各コースにPDF教材をアップロード
5. **会話履歴タブ**: すべての会話を閲覧

### Chatworkボットの使い方（推奨・DM対応）

1. **ボットアカウントとDMを開始**（グループチャットではなく、1対1のDMでやりとりします）
2. 教材に関する質問を送信
3. ボットが教材内容を参照して回答
4. 不満がある場合、自動でSlackに通知され、運営スタッフが二次回答

**注意：** 各DMルームにWebhookを設定する必要があります（上記の「Chatwork APIの設定」を参照）

### LINEボットの使い方（オプション）

1. 各コースのLINE公式アカウントを友だち追加
2. 教材に関する質問を送信（画像も対応）
3. ボットが教材内容を参照して回答
4. 不満がある場合、自動でSlackに通知され、運営スタッフが二次回答

## アーキテクチャ

```
online-school-bot/
├── backend/
│   ├── main.py              # FastAPIサーバー（Webhook受信）
│   ├── chatwork_bot.py      # Chatwork API連携
│   ├── line_bot.py          # LINE Messaging API連携
│   ├── pdf_processor.py     # PDF教材の解析・ベクトル化
│   ├── ai_responder.py      # AI回答生成（教材+ネット検索）
│   ├── satisfaction_analyzer.py  # 満足度判定
│   ├── spreadsheet.py       # スプレッドシート記録
│   ├── slack_notifier.py    # Slack通知（二次回答フロー）
│   ├── course_manager.py    # コース管理
│   ├── conversation_manager.py  # 会話履歴管理
│   ├── auth.py              # 認証
│   └── config.py            # 設定
├── frontend/
│   ├── admin.html           # 管理画面
│   └── login.html           # ログイン画面
├── static/
│   ├── admin.css            # 管理画面スタイル
│   └── admin.js             # 管理画面スクリプト
└── requirements.txt
```

## 料金について

### Chatwork API

- **無料**: 基本的なAPI機能は無料で利用可能
- **制限**: API呼び出し回数に制限がある場合があります（詳細はChatwork公式ドキュメントを参照）

### LINE Messaging API

- **応答メッセージ**: 無料（ユーザーからのメッセージに対する応答）
- **プッシュメッセージ**: 
  - コミュニケーションプラン（無料）: 月200通まで
  - ライトプラン: 月額5,000円、月5,000通まで
  - スタンダードプラン: 月額15,000円、月30,000通まで

### OpenAI API

- 埋め込み生成: $0.00002 / 1K tokens
- GPT-4o-mini: $0.15 / 1M input tokens, $0.60 / 1M output tokens

## 注意事項

- PDFファイルは自動でベクトル化され、`~/.online_school_bot/vectors/`に保存されます
- 会話履歴は`~/.online_school_bot/conversations/`に保存されます
- 本番環境では、SECRET_KEYを強力なランダム文字列に変更してください
- Google Sheets APIの認証情報は安全に管理してください

## ライセンス

MIT License
