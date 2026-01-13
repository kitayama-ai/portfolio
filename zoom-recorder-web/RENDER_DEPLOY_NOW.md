# Renderデプロイ手順（今すぐ実行）

## ステップ1: Renderアカウントを作成

1. https://render.com/ にアクセス
2. 「Get Started for Free」をクリック
3. GitHubアカウントでログイン
4. RenderにGitHubアカウントへのアクセスを許可

## ステップ2: プロジェクトを作成

1. Renderダッシュボードで「New +」をクリック
2. 「Web Service」を選択
3. 「Connect GitHub」をクリック（初回のみ）
4. リポジトリ `kitayama-ai/portfolio` を選択
5. 「Connect」をクリック

## ステップ3: 設定を入力

以下の設定を入力：

### 基本設定
- **Name**: `zoom-recorder-web`（任意）
- **Region**: `Oregon (US West)` または最寄りのリージョン
- **Branch**: `master`
- **Root Directory**: `zoom-recorder-web`（重要！）

### ビルド・起動設定
- **Environment**: `Python 3`
- **Root Directory**: `zoom-recorder-web`（重要！）
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd backend && python main.py`

### インスタンスタイプ
- **Free**（無料プラン）を選択

## ステップ4: 環境変数を設定

「Advanced」セクションを開き、環境変数を追加：

### 必須環境変数
```
OPENAI_API_KEY=sk-your-api-key-here
SECRET_KEY=your-secret-key-change-in-production
```

### オプション環境変数
```
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_CHANNEL=#meeting-notes
```

**注意**: 環境変数は「Environment」セクションでも追加できます（推奨）。

## ステップ5: デプロイ

1. 「Create Web Service」をクリック
2. デプロイが開始されます（通常5-10分）
3. デプロイ完了後、URL（例: `https://zoom-recorder-web.onrender.com`）が表示されます

## ステップ6: 動作確認

1. 公開URLにアクセス
2. ログインページ（`/frontend/login.html`）が表示されることを確認
3. 新規登録してログインできることを確認

## 注意事項

### スリープについて
- 無料プランは15分の非アクティブ後にスリープします
- 初回アクセス時に30秒程度かかって復帰します（正常です）
- 2回目以降のアクセスは通常通り動作します

### スリープを回避する方法
1. **有料プランにアップグレード**（$7/月、スリープなし）
2. **外部サービスで定期アクセス**（UptimeRobotなど）
3. **スリープを許容**（個人開発なら問題なし）

## トラブルシューティング

### デプロイが失敗する場合

1. **ログを確認**（「Logs」タブ）
2. **よくある問題**：
   - `requirements.txt`が見つからない → Root Directoryを確認
   - モジュールインポートエラー → 依存関係を確認
   - ポートエラー → `PORT`環境変数が自動設定されているか確認（Renderが自動設定）

### 環境変数が反映されない場合

1. 環境変数を設定後、自動的に再デプロイが開始されます
2. 再デプロイが開始されない場合は、「Manual Deploy」をクリック

### スリープからの復帰が遅い場合

- 初回アクセス時は30秒程度かかります（正常です）
- 2回目以降は通常通り動作します

## 次のステップ

デプロイ完了後：
1. 公開URLをメモ
2. 動作確認
3. 必要に応じて環境変数を追加・変更
