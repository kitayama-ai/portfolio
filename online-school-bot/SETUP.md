# セットアップガイド

## クイックスタート

### 1. 依存パッケージのインストール

```bash
cd online-school-bot
pip3 install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを編集して、以下を設定してください：

**必須:**
- `OPENAI_API_KEY` - OpenAI APIキー

**オプション:**
- `CHATWORK_API_TOKEN_{course_id}` - Chatworkを使う場合
- `SLACK_BOT_TOKEN` - Slack通知を使う場合
- `GOOGLE_CREDENTIALS_PATH`, `GOOGLE_SPREADSHEET_ID` - スプレッドシート記録を使う場合

### 3. 初期ユーザーの作成

```bash
cd backend
python3 create_admin_user.py
```

ユーザー名とパスワードを入力してください。

### 4. サーバーの起動

```bash
# 方法1: 起動スクリプトを使用
./start.sh

# 方法2: 直接起動
cd backend
python3 main.py
```

サーバーは `http://localhost:8002` で起動します。

### 5. 管理画面にアクセス

1. ブラウザで `http://localhost:8002` にアクセス
2. 作成したユーザー名とパスワードでログイン

## 次のステップ

### コースの登録

1. 管理画面の「コース管理」タブを開く
2. 「コースを登録」ボタンをクリック
3. コースID、コース名、プラットフォーム（Chatwork推奨）を入力
4. 登録

### PDF教材のアップロード

1. 管理画面の「PDF教材」タブを開く
2. コースを選択
3. PDFファイルを選択してアップロード

### Chatwork Webhookの設定（DM対応・1000人以上対応）

**重要：このボットはDM（1対1のチャット）でのやりとりを想定しています。**

1. [Chatwork API申請ページ](https://www.chatwork.com/service/packages/chatwork/subpackages/api/apply_beta.php)でAPIトークンを申請
2. `.env`ファイルに `CHATWORK_API_TOKEN_{course_id}=xxx` を設定

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

## トラブルシューティング

### `pip`コマンドが見つからない

macOSでは`pip3`を使用してください：
```bash
pip3 install -r requirements.txt
```

### サーバーが起動しない

- `.env`ファイルが正しく設定されているか確認
- `OPENAI_API_KEY`が設定されているか確認
- ポート8002が使用されていないか確認

### ログインできない

- 初期ユーザーを作成したか確認
- `python3 create_admin_user.py`を実行してユーザーを作成
