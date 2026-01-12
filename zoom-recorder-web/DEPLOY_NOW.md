# 今すぐデプロイする方法

## 最も簡単な方法（Web UI）

1. **Railwayにアクセス**
   - https://railway.app/ を開く
   - 「Start a New Project」をクリック
   - GitHubアカウントでログイン

2. **プロジェクトを作成**
   - 「New Project」→「Deploy from GitHub repo」
   - リポジトリ `kitayama-ai/portfolio` を選択
   - 「Deploy Now」をクリック

3. **設定を変更**
   - デプロイされたサービスをクリック
   - 「Settings」タブで **Root Directory** を `zoom-recorder-web/backend` に設定

4. **環境変数を設定**
   - 「Variables」タブで以下を追加:
     ```
     OPENAI_API_KEY=sk-your-api-key-here
     SECRET_KEY=your-secret-key-here
     ```

5. **完了！**
   - 「Settings」タブの「Generate Domain」で公開URLを取得

## CLIを使用する場合

```bash
cd zoom-recorder-web
./deploy_railway.sh
```

または手動で:

```bash
# 1. ログイン（ブラウザが開きます）
railway login

# 2. プロジェクトを作成
railway init

# 3. 環境変数を設定
railway variables set OPENAI_API_KEY=sk-your-api-key-here
railway variables set SECRET_KEY=your-secret-key-here

# 4. デプロイ
cd backend
railway up
```

## 所要時間

- Web UI: 約5分
- CLI: 約10分（ログイン含む）
