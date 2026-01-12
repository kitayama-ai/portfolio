# Railwayデプロイ手順（CLI使用）

## 前提条件

- Railway CLIがインストール済み
- Railwayアカウントが必要

## 手順

### 1. Railwayにログイン

```bash
railway login
```

ブラウザが開き、GitHubアカウントでログインします。

### 2. プロジェクトを作成

```bash
cd zoom-recorder-web
railway init
```

プロジェクト名を入力（例: `zoom-recorder-web`）

### 3. 環境変数を設定

```bash
railway variables set OPENAI_API_KEY=sk-your-api-key-here
railway variables set SECRET_KEY=your-secret-key-change-in-production
railway variables set SLACK_BOT_TOKEN=xoxb-your-token-here  # オプション
railway variables set SLACK_CHANNEL=#meeting-notes  # オプション
```

### 4. デプロイ

```bash
railway up
```

### 5. 公開URLを取得

```bash
railway domain
```

または、Railwayダッシュボードで確認:
https://railway.app/dashboard

## トラブルシューティング

### ログインできない場合

```bash
railway logout
railway login
```

### デプロイが失敗する場合

```bash
railway logs
```

でログを確認

### 環境変数が反映されない場合

```bash
railway variables
```

で環境変数を確認
