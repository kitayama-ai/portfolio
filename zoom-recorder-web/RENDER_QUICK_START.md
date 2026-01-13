# Renderデプロイ（クイックスタート）

## 3ステップで完了

### ステップ1: アカウント作成・ログイン
https://render.com/ → GitHubアカウントでログイン

### ステップ2: Webサービス作成
1. 「New +」→「Web Service」
2. GitHubリポジトリ `kitayama-ai/portfolio` を選択
3. 以下の設定を入力：
   - **Name**: `zoom-recorder-web`
   - **Root Directory**: `zoom-recorder-web`
   - **Build Command**: `cd zoom-recorder-web && pip install -r requirements.txt`
   - **Start Command**: `cd zoom-recorder-web/backend && python main.py`
   - **Plan**: `Free`

### ステップ3: 環境変数設定・デプロイ
1. 「Environment」セクションで以下を追加：
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   SECRET_KEY=your-secret-key-change-in-production
   ```
2. 「Create Web Service」をクリック
3. デプロイ完了を待つ（5-10分）
4. 表示されたURLにアクセス

## 完了！

詳細は `RENDER_DEPLOY_NOW.md` を参照してください。
