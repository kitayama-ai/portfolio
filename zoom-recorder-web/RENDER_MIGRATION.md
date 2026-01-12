# Railway → Render 移行ガイド

## 移行のタイミング

- Railwayの無料トライアル（30日間）終了後
- または、無料で継続利用したい場合

## 移行手順

### ステップ1: Renderアカウントを作成

1. https://render.com/ にアクセス
2. GitHubアカウントでログイン
3. アカウント作成完了

### ステップ2: プロジェクトを作成

1. Renderダッシュボードで「New」をクリック
2. 「Web Service」を選択
3. 「Connect GitHub」をクリック
4. リポジトリ `kitayama-ai/portfolio` を選択
5. 「Connect」をクリック

### ステップ3: 設定を入力

以下の設定を入力：

**基本設定:**
- **Name**: `zoom-recorder-web`（任意）
- **Region**: `Oregon (US West)`（最寄りのリージョン）
- **Branch**: `master`
- **Root Directory**: `zoom-recorder-web/backend`

**ビルド設定:**
- **Environment**: `Python 3`
- **Build Command**: `cd zoom-recorder-web && pip install -r requirements.txt`
- **Start Command**: `cd zoom-recorder-web/backend && python3 main.py`

**インスタンスタイプ:**
- **Free**（無料プラン）を選択

### ステップ4: 環境変数を設定

「Advanced」セクションで環境変数を追加：

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

### ステップ5: デプロイ

1. 「Create Web Service」をクリック
2. デプロイが開始されます（通常5-10分）
3. デプロイ完了後、URL（例: `https://zoom-recorder-web.onrender.com`）が表示されます

### ステップ6: 動作確認

1. 公開URLにアクセス
2. ログインページが表示されることを確認
3. 新規登録してログインできることを確認

### ステップ7: Railwayの停止（オプション）

1. Railwayダッシュボードにアクセス
2. プロジェクトを選択
3. 「Settings」→「Delete Project」で削除
   - または、サービスを停止してクレジットを節約

## 注意事項

### スリープについて

- 無料プランは15分の非アクティブ後にスリープします
- 初回アクセス時に30秒程度かかって復帰します
- 2回目以降のアクセスは通常通り動作します

### スリープを回避する方法

1. **有料プランにアップグレード**（$7/月）
2. **外部サービスで定期アクセス**（UptimeRobotなど）
3. **スリープを許容**（個人開発なら問題なし）

## トラブルシューティング

### デプロイが失敗する場合

1. ログを確認（「Logs」タブ）
2. よくある問題：
   - `requirements.txt`が見つからない → Root Directoryを確認
   - モジュールインポートエラー → 依存関係を確認
   - ポートエラー → `PORT`環境変数が自動設定されているか確認

### 環境変数が反映されない場合

1. 環境変数を設定後、自動的に再デプロイが開始されます
2. 再デプロイが開始されない場合は、「Manual Deploy」をクリック

### スリープからの復帰が遅い場合

- 初回アクセス時は30秒程度かかります（正常）
- 2回目以降は通常通り動作します

## 移行チェックリスト

- [ ] Renderアカウント作成
- [ ] プロジェクト作成
- [ ] 設定入力（Root Directory、Build Command、Start Command）
- [ ] 環境変数設定
- [ ] デプロイ完了
- [ ] 動作確認
- [ ] Railwayプロジェクトの停止/削除（オプション）

## 参考

- Render公式ドキュメント: https://render.com/docs
- サポート: https://render.com/support
