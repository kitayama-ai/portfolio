# Railwayデプロイ手順（Web UI）

## 現在のステップ

✅ Railwayにログイン済み

## 次のステップ

### ステップ1: プロジェクトを作成

1. Railwayダッシュボードで「New Project」をクリック
2. 「Deploy from GitHub repo」を選択
3. リポジトリ `kitayama-ai/portfolio` を検索して選択
4. 「Deploy Now」をクリック

### ステップ2: 設定を変更

デプロイが開始されたら：

1. デプロイされたサービス（通常はリポジトリ名）をクリック
2. 「Settings」タブを開く
3. 以下の設定を確認・変更：

   **Root Directory:**
   ```
   zoom-recorder-web/backend
   ```
   
   **Start Command:**
   ```
   python3 main.py
   ```
   （自動検出される場合もあります）

### ステップ3: 環境変数を設定

1. 「Variables」タブを開く
2. 以下の環境変数を追加：

   **必須:**
   - `OPENAI_API_KEY` = `sk-your-api-key-here`
   - `SECRET_KEY` = `your-secret-key-change-in-production`

   **オプション:**
   - `SLACK_BOT_TOKEN` = `xoxb-your-token-here`
   - `SLACK_CHANNEL` = `#meeting-notes`

3. 各環境変数を追加後、「Add」をクリック

### ステップ4: デプロイの確認

1. 「Deployments」タブでデプロイ状況を確認
2. ログを確認してエラーがないかチェック
3. デプロイが完了するまで待機（通常2-5分）

### ステップ5: 公開URLを取得

1. 「Settings」タブに戻る
2. 「Generate Domain」をクリック
3. 表示されたURL（例: `https://your-app.railway.app`）をコピー

### ステップ6: 動作確認

1. 公開URLにアクセス
2. ログインページが表示されることを確認
3. 新規登録してログインできることを確認

## トラブルシューティング

### デプロイが失敗する場合

1. 「Deployments」タブでログを確認
2. エラーメッセージを確認
3. よくある問題：
   - `requirements.txt`が見つからない → Root Directoryを確認
   - モジュールインポートエラー → 依存関係が正しくインストールされているか確認

### 環境変数が反映されない場合

1. 環境変数を設定後、自動的に再デプロイが開始されます
2. 再デプロイが開始されない場合は、「Redeploy」をクリック

## 完了後

デプロイが完了したら、公開URLをメモしてください！
