# Railway Web UI設定（必須確認）

## 現在の状態

✅ 設定ファイルを修正してGitHubにプッシュ済み
⏳ Web UIでの設定確認が必要

## Web UIで確認・設定すべき項目

### 1. Root Directory（Sourceセクション）

**設定値**: **空**（リポジトリのルートを使用）

確認方法：
1. 「Settings」タブ → 「Source」セクション
2. 「Root Directory」が空になっているか確認
3. 空でない場合は削除して保存

### 2. Build Command（Buildセクション）

**設定値**:
```
cd zoom-recorder-web && python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt
```

確認方法：
1. 「Settings」タブ → 「Build」セクション
2. 「Custom Build Command」に上記のコマンドが設定されているか確認
3. 設定されていない場合は入力して保存

### 3. Start Command（Deployセクション）

**設定値**:
```
cd zoom-recorder-web/backend && python3 main.py
```

確認方法：
1. 「Settings」タブ → 右側サイドバーで「Deploy」をクリック
2. 「Start Command」に上記のコマンドが設定されているか確認
3. 設定されていない場合は入力して保存

### 4. 環境変数（Variablesタブ）

**必須環境変数**:
- `OPENAI_API_KEY` = `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`
- `SECRET_KEY` = （ランダムな文字列、openssl rand -hex 32で生成）

確認方法：
1. 「Variables」タブを開く
2. 上記の環境変数が設定されているか確認
3. 設定されていない場合は追加

## 自動デプロイ

GitHubにプッシュしたので、自動的に再デプロイが開始されます。

## デプロイ確認

1. 「Deployments」タブでデプロイ状況を確認
2. ログでエラーがないか確認
3. デプロイ完了後、公開URLにアクセスして動作確認

## トラブルシューティング

### デプロイが失敗する場合

1. 「Deployments」タブでログを確認
2. エラーメッセージを確認
3. 上記の設定が正しいか再確認

### アプリケーションが起動しない場合

1. 「Deployments」タブでログを確認
2. Start Commandが正しく実行されているか確認
3. 環境変数が設定されているか確認
