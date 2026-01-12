# Railwayデプロイ手順（手動）

Railway CLIのログインはブラウザ認証が必要なため、以下の手順でデプロイしてください。

## 方法1: Railway Web UIを使用（推奨・最も簡単）

### ステップ1: Railwayにアクセス

1. https://railway.app/ にアクセス
2. 「Start a New Project」をクリック
3. GitHubアカウントでログイン

### ステップ2: プロジェクトを作成

1. 「New Project」をクリック
2. 「Deploy from GitHub repo」を選択
3. リポジトリ `kitayama-ai/portfolio` を選択
4. 「Deploy Now」をクリック

### ステップ3: 設定を変更

1. デプロイされたサービスをクリック
2. 「Settings」タブを開く
3. **Root Directory**を設定:
   ```
   zoom-recorder-web/backend
   ```
4. **Start Command**を確認（自動検出される場合あり）:
   ```
   python3 main.py
   ```

### ステップ4: 環境変数を設定

「Variables」タブで以下の環境変数を追加:

**必須:**
```
OPENAI_API_KEY=sk-your-api-key-here
SECRET_KEY=your-secret-key-change-in-production
```

**オプション:**
```
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_CHANNEL=#meeting-notes
```

### ステップ5: デプロイの確認

1. 「Deployments」タブでデプロイ状況を確認
2. ログを確認してエラーがないかチェック
3. デプロイ完了後、「Settings」タブの「Generate Domain」で公開URLを取得

### ステップ6: 動作確認

1. Railwayが提供するURL（例: `https://your-app.railway.app`）にアクセス
2. ログインページが表示されることを確認

## 方法2: Railway CLIを使用（手動ログイン後）

### ステップ1: Railway CLIでログイン

ターミナルで実行:
```bash
cd zoom-recorder-web
railway login
```

ブラウザが開くので、GitHubアカウントでログインします。

### ステップ2: プロジェクトを作成

```bash
railway init
```

プロジェクト名を入力（例: `zoom-recorder-web`）

### ステップ3: 環境変数を設定

```bash
railway variables set OPENAI_API_KEY=sk-your-api-key-here
railway variables set SECRET_KEY=your-secret-key-change-in-production
railway variables set SLACK_BOT_TOKEN=xoxb-your-token-here  # オプション
railway variables set SLACK_CHANNEL=#meeting-notes  # オプション
```

### ステップ4: デプロイ

```bash
railway up
```

### ステップ5: 公開URLを取得

```bash
railway domain
```

または、Railwayダッシュボードで確認

## 推奨方法

**方法1（Web UI）**を推奨します。最も簡単で、視覚的に確認できます。
