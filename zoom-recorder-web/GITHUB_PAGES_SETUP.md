# GitHub Pagesでのデプロイ方法

## 概要

このプロジェクトは、フロントエンドをGitHub Pagesでホストし、バックエンドAPIを別のサービス（Railway、Renderなど）でホストする構成です。

## セットアップ手順

### 1. バックエンドAPIをデプロイ

まず、バックエンドAPIを以下のいずれかのサービスにデプロイします：

#### Railwayを使用（推奨・無料枠あり）

1. https://railway.app/ にアクセス
2. GitHubアカウントでログイン
3. 「New Project」→「Deploy from GitHub repo」を選択
4. リポジトリを選択
5. ルートディレクトリを `zoom-recorder-web/backend` に設定
6. 環境変数を設定：
   - `OPENAI_API_KEY`
   - `SECRET_KEY`
   - `SLACK_BOT_TOKEN`（オプション）
   - `SLACK_CHANNEL`（オプション）
7. デプロイ後、Railwayが提供するURLをコピー（例: `https://your-app.railway.app`）

#### Renderを使用

1. https://render.com/ にアクセス
2. GitHubアカウントでログイン
3. 「New Web Service」を選択
4. リポジトリを選択
5. 設定：
   - Build Command: `cd zoom-recorder-web && pip install -r requirements.txt`
   - Start Command: `cd zoom-recorder-web/backend && python3 main.py`
6. 環境変数を設定
7. デプロイ後、URLをコピー

### 2. GitHub Pagesの設定

1. GitHubリポジトリの「Settings」→「Pages」に移動
2. Source: 「GitHub Actions」を選択
3. ワークフローが自動的に実行されます

### 3. フロントエンドの設定

`zoom-recorder-web/frontend/config.js` を編集して、バックエンドAPIのURLを設定：

```javascript
// バックエンドAPIのURLを設定
window.API_BASE_URL = 'https://your-backend.railway.app';
window.WS_BASE_URL = 'wss://your-backend.railway.app';
```

### 4. コミット＆プッシュ

```bash
git add zoom-recorder-web/frontend/config.js
git commit -m "Configure API base URL for GitHub Pages"
git push origin master
```

### 5. アクセス

GitHub PagesのURL（例: `https://your-username.github.io/portfolio/zoom-recorder-web/frontend/`）にアクセス

## 注意事項

### CORS設定

バックエンドAPIのCORS設定で、GitHub Pagesのドメインを許可する必要があります：

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-username.github.io",
        "http://localhost:8000"  # ローカル開発用
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### WebSocket接続

WebSocketもバックエンドAPIのURLを使用するように設定されています。

### 環境変数

GitHub Pagesは静的サイトなので、環境変数は使用できません。
`config.js`で直接設定するか、ビルド時に環境変数を注入する必要があります。

## トラブルシューティング

### CORSエラーが発生する場合

バックエンドAPIのCORS設定を確認し、GitHub Pagesのドメインを許可してください。

### WebSocket接続が失敗する場合

`config.js`の`WS_BASE_URL`が正しく設定されているか確認してください。
HTTPSの場合は`wss://`、HTTPの場合は`ws://`を使用します。

### APIリクエストが失敗する場合

ブラウザの開発者ツール（F12）でネットワークタブを確認し、リクエストURLが正しいか確認してください。
