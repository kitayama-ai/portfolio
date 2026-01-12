# Railwayデプロイ手順

## ステップ1: Railwayアカウントを作成

1. https://railway.app/ にアクセス
2. 「Start a New Project」をクリック
3. GitHubアカウントでログイン

## ステップ2: プロジェクトを作成

1. 「New Project」をクリック
2. 「Deploy from GitHub repo」を選択
3. リポジトリ `kitayama-ai/portfolio` を選択
4. 「Deploy Now」をクリック

## ステップ3: 設定を変更

### Root Directoryの設定

1. デプロイされたサービスをクリック
2. 「Settings」タブを開く
3. 「Root Directory」を設定:
   ```
   zoom-recorder-web/backend
   ```
   または、`railway.json`が正しく設定されていれば自動検出されます

### Start Commandの確認

「Settings」タブで「Start Command」を確認:
```
python3 main.py
```

## ステップ4: 環境変数を設定

「Variables」タブで以下の環境変数を追加:

### 必須
```
OPENAI_API_KEY=sk-your-api-key-here
SECRET_KEY=your-secret-key-change-in-production
```

### オプション
```
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_CHANNEL=#meeting-notes
```

### ポート設定（自動）
Railwayは自動的に`PORT`環境変数を設定するので、手動で設定する必要はありません。

## ステップ5: デプロイの確認

1. 「Deployments」タブでデプロイ状況を確認
2. ログを確認してエラーがないかチェック
3. デプロイ完了後、「Settings」タブの「Generate Domain」で公開URLを取得

## ステップ6: 動作確認

1. Railwayが提供するURL（例: `https://your-app.railway.app`）にアクセス
2. ログインページが表示されることを確認
3. 新規登録してログインできることを確認

## トラブルシューティング

### デプロイが失敗する場合

1. **ログを確認**
   - 「Deployments」タブでログを確認
   - エラーメッセージを確認

2. **よくある問題**
   - `requirements.txt`が見つからない → Root Directoryを確認
   - ポートエラー → `PORT`環境変数が正しく設定されているか確認
   - モジュールインポートエラー → 依存関係が正しくインストールされているか確認

3. **再デプロイ**
   - 「Settings」タブで「Redeploy」をクリック

### 環境変数が反映されない場合

1. 環境変数を設定後、再デプロイが必要な場合があります
2. 「Redeploy」をクリックして再デプロイ

## 次のステップ

デプロイが完了したら:
1. 公開URLをメモ
2. 動作確認
3. 必要に応じてカスタムドメインを設定（有料プラン）

## 参考

- Railway公式ドキュメント: https://docs.railway.app/
- サポート: https://railway.app/help
