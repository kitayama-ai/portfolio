# GitHub Pages クイックスタート

## 3ステップでGitHub Pagesにデプロイ

### ステップ1: バックエンドAPIをデプロイ

**Railwayを使用（推奨）:**

1. https://railway.app/ にアクセスしてログイン
2. 「New Project」→「Deploy from GitHub repo」
3. リポジトリを選択
4. ルートディレクトリ: `zoom-recorder-web/backend`
5. 環境変数を設定:
   ```
   OPENAI_API_KEY=your-key-here
   SECRET_KEY=your-secret-key
   ```
6. デプロイ後、URLをコピー（例: `https://your-app.railway.app`）

### ステップ2: フロントエンドの設定

`zoom-recorder-web/frontend/config.js` を編集:

```javascript
window.API_BASE_URL = 'https://your-app.railway.app';
window.WS_BASE_URL = 'wss://your-app.railway.app';
```

### ステップ3: GitHub Pagesを有効化

1. GitHubリポジトリの「Settings」→「Pages」
2. Source: 「GitHub Actions」を選択
3. 完了！

## アクセス

デプロイ後、以下のURLでアクセスできます：
```
https://kitayama-ai.github.io/portfolio/zoom-recorder-web/frontend/
```

## 注意

- バックエンドAPIのCORS設定でGitHub Pagesのドメインを許可してください
- WebSocket接続もバックエンドAPIのURLを使用します
