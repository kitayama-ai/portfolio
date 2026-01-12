# Zoom自動録画ツール - URL化・デプロイ方法（おすすめ）

## 🎯 おすすめの方法

このプロジェクトは**FastAPIバックエンド + フロントエンド**の構成なので、以下の方法がおすすめです。

## 1位: Railway（最もおすすめ）⭐

### 理由
- ✅ **無料トライアルあり**（30日間、$5相当）
- ✅ **セットアップが簡単**（GitHub連携で自動デプロイ）
- ✅ **Python/FastAPIに最適化**
- ✅ **環境変数の設定が簡単**
- ✅ **自動HTTPS対応**
- ⚠️ **30日後は有料プラン（$5/月〜）が必要**

### 手順

1. **Railwayにアクセス**
   - https://railway.app/ にアクセス
   - GitHubアカウントでログイン

2. **プロジェクトを作成**
   - 「New Project」をクリック
   - 「Deploy from GitHub repo」を選択
   - リポジトリを選択

3. **設定**
   - **Root Directory**: `zoom-recorder-web/backend` に設定
   - **Start Command**: `python3 main.py`（自動検出される場合あり）

4. **環境変数を設定**
   ```
   OPENAI_API_KEY=your-api-key-here
   SECRET_KEY=your-secret-key-here
   SLACK_BOT_TOKEN=xoxb-your-token-here（オプション）
   SLACK_CHANNEL=#meeting-notes（オプション）
   ```

5. **デプロイ**
   - 自動的にデプロイが開始されます
   - 完了後、Railwayが提供するURL（例: `https://your-app.railway.app`）でアクセス可能

### 所要時間: 約5分

---

## 2位: Render（無料で継続利用可能・おすすめ）⭐⭐⭐⭐⭐

### 理由
- ✅ **無料プランあり**（無期限、制限あり）
- ✅ **セットアップが簡単**
- ✅ **自動HTTPS対応**
- ⚠️ 無料プランは15分の非アクティブ後にスリープ（アクセス時に自動復帰）
- ✅ **30日後も無料で継続利用可能**

### 手順

1. **Renderにアクセス**
   - https://render.com/ にアクセス
   - GitHubアカウントでログイン

2. **Webサービスを作成**
   - 「New」→「Web Service」を選択
   - GitHubリポジトリを選択

3. **設定**
   - **Name**: 任意の名前
   - **Root Directory**: `zoom-recorder-web/backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && python3 main.py`

4. **環境変数を設定**
   - ダッシュボードで環境変数を追加

5. **デプロイ**
   - 「Create Web Service」をクリック
   - デプロイ完了後、URL（例: `https://your-app.onrender.com`）でアクセス可能

### 所要時間: 約10分

---

## 3位: ngrok（開発・テスト用）⭐

### 理由
- ✅ **即座に試せる**（5分で完了）
- ✅ **ローカルサーバーをそのまま公開**
- ⚠️ 無料プランではURLが毎回変わる
- ⚠️ 開発・テスト用途向け

### 手順

1. **ngrokをインストール**（既にインストール済み）
   ```bash
   brew install ngrok/ngrok/ngrok
   ```

2. **ngrokアカウントを作成**
   - https://ngrok.com/ にアクセス
   - アカウント作成後、authtokenを取得

3. **authtokenを設定**
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

4. **サーバーを起動**
   ```bash
   cd zoom-recorder-web/backend
   python3 main.py
   ```

5. **ngrokでトンネルを作成**
   ```bash
   ngrok http 8000
   ```

6. **公開URLを取得**
   - ngrokが表示するURL（例: `https://xxxx-xx-xx-xx-xx.ngrok-free.app`）を使用

### 所要時間: 約5分

---

## 比較表

| 方法 | 無料枠 | セットアップ | 固定URL | おすすめ度 |
|------|--------|------------|---------|-----------|
| **Railway** | ✅ あり | ⭐⭐⭐ 簡単 | ✅ あり | ⭐⭐⭐⭐⭐ |
| **Render** | ✅ あり | ⭐⭐⭐ 簡単 | ✅ あり | ⭐⭐⭐⭐ |
| **ngrok** | ✅ あり | ⭐⭐⭐⭐⭐ 超簡単 | ⚠️ 変わる | ⭐⭐⭐ |

---

## 推奨フロー

### 本番環境
1. **Railway**を使用（最も簡単で安定）

### 開発・テスト
1. **ngrok**を使用（即座に試せる）

### 予算がある場合
1. **Railway有料プラン**（$20/月、より多くのリソース）

---

## 注意事項

### セキュリティ
- 本番環境では必ずHTTPSを使用（すべての方法で自動対応）
- 環境変数（APIキーなど）は絶対に公開しない
- 認証機能を必ず有効化

### CORS設定
- バックエンドAPIのCORS設定で、アクセスを許可するドメインを設定
- 現在は開発環境用に`*`（すべて許可）になっていますが、本番環境では適切に制限してください

---

## 次のステップ

1. **Railwayを試す**（最もおすすめ）
2. デプロイ後、動作確認
3. 必要に応じて細かい調整
