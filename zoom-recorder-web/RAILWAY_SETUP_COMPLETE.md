# Railway設定完了ガイド

## 現在の状態

✅ Railway CLIログイン完了
✅ プロジェクト確認済み: `humble-friendship`

## 次のステップ（Web UIで設定）

Railway CLIの一部コマンドは対話モードが必要なため、Web UIで設定する方が簡単です。

### ステップ1: プロジェクトにリンク

ターミナルで以下を実行（対話モードで実行）：

```bash
cd zoom-recorder-web
railway link
```

プロンプトが表示されたら、`humble-friendship` を選択してください。

### ステップ2: 環境変数を設定（Web UI推奨）

1. Railwayダッシュボードにアクセス
2. `humble-friendship` プロジェクトを開く
3. デプロイされたサービスをクリック
4. 「Variables」タブを開く
5. 以下の環境変数を追加：

**必須:**
```
OPENAI_API_KEY=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
SECRET_KEY=（ランダムな文字列を生成）
```

**SECRET_KEYの生成方法:**
```bash
openssl rand -hex 32
```

### ステップ3: Root Directoryを設定

1. サービスの「Settings」タブを開く
2. **Root Directory** を以下に設定：
   ```
   zoom-recorder-web/backend
   ```

### ステップ4: デプロイの確認

1. 「Deployments」タブでデプロイ状況を確認
2. ログを確認してエラーがないかチェック
3. デプロイが完了するまで待機

### ステップ5: 公開URLを取得

1. 「Settings」タブに戻る
2. 「Generate Domain」をクリック
3. 表示されたURLをコピー

## トラブルシューティング

### プロジェクトにリンクできない場合

Web UIで直接設定する方が簡単です：
1. Railwayダッシュボードでプロジェクトを開く
2. 上記の手順に従って設定

### 環境変数の設定方法

Railway CLIのバージョンによってコマンドが異なるため、Web UIでの設定を推奨します。
