# Railwayデプロイ - 次のステップ

## 現在の状態

✅ プロジェクト作成済み
✅ GitHubリポジトリ連携済み

## 次のステップ（Web UIで実行）

### ステップ1: プロジェクトの設定を確認

1. Railwayダッシュボードで作成したプロジェクトを開く
2. デプロイされたサービスをクリック
3. 「Settings」タブを開く

### ステップ2: Root Directoryを設定

**重要**: 以下の設定を確認・変更してください：

- **Root Directory**: `zoom-recorder-web/backend`
- **Start Command**: `python3 main.py`（自動検出される場合あり）

### ステップ3: 環境変数を設定

「Variables」タブで以下の環境変数を追加：

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

### ステップ4: デプロイの確認

1. 「Deployments」タブでデプロイ状況を確認
2. ログを確認してエラーがないかチェック
3. デプロイが完了するまで待機

### ステップ5: 公開URLを取得

1. 「Settings」タブに戻る
2. 「Generate Domain」をクリック
3. 表示されたURL（例: `https://your-app.railway.app`）をコピー

### ステップ6: 動作確認

1. 公開URLにアクセス
2. ログインページが表示されることを確認

## トラブルシューティング

### Root Directoryが設定されていない場合

デプロイが失敗する可能性があります。必ず `zoom-recorder-web/backend` に設定してください。

### 環境変数が設定されていない場合

一部の機能（文字起こし、議事録生成など）が動作しません。必ず `OPENAI_API_KEY` を設定してください。

### デプロイが失敗する場合

1. 「Deployments」タブでログを確認
2. エラーメッセージを確認
3. よくある問題：
   - `requirements.txt`が見つからない → Root Directoryを確認
   - モジュールインポートエラー → 依存関係を確認
