# Zoom自動録画ツール - URL化・デプロイ方法

## 方法1: ngrokを使用（最も簡単・即座にURL化）

### インストール

```bash
# Homebrew経由
brew install ngrok/ngrok/ngrok

# または、公式サイトからダウンロード
# https://ngrok.com/download
```

### 使用方法

1. **ngrokアカウントを作成**（無料）
   - https://ngrok.com/ にアクセス
   - アカウント作成後、authtokenを取得

2. **authtokenを設定**
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

3. **サーバーを起動**
   ```bash
   cd zoom-recorder-web/backend
   python3 main.py
   ```

4. **ngrokでトンネルを作成**
   ```bash
   ngrok http 8000
   ```

5. **公開URLを取得**
   - ngrokが表示するURL（例: `https://xxxx-xx-xx-xx-xx.ngrok-free.app`）を使用
   - このURLでインターネットからアクセス可能

### 注意事項

- 無料プランでは、URLはセッションごとに変わります
- 有料プランでは固定URLが使用可能
- HTTPSが自動で有効になります

## 方法2: Vercelにデプロイ（推奨・無料）

### セットアップ

1. **Vercelアカウントを作成**
   - https://vercel.com/ にアクセス
   - GitHubアカウントでログイン

2. **プロジェクトをインポート**
   - GitHubリポジトリを選択
   - ビルド設定を自動検出

3. **環境変数を設定**
   - Vercelダッシュボードで環境変数を追加
   - `.env`ファイルの内容を設定

### デプロイコマンド

```bash
# Vercel CLIをインストール
npm i -g vercel

# デプロイ
cd zoom-recorder-web
vercel
```

## 方法3: Railwayにデプロイ（推奨・無料枠あり）

### セットアップ

1. **Railwayアカウントを作成**
   - https://railway.app/ にアクセス
   - GitHubアカウントでログイン

2. **プロジェクトを作成**
   - 「New Project」をクリック
   - GitHubリポジトリを選択

3. **環境変数を設定**
   - Railwayダッシュボードで環境変数を追加

### デプロイ設定

`railway.json`を作成：

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && python3 main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## 方法4: Renderにデプロイ（推奨・無料枠あり）

### セットアップ

1. **Renderアカウントを作成**
   - https://render.com/ にアクセス
   - GitHubアカウントでログイン

2. **Webサービスを作成**
   - 「New Web Service」を選択
   - GitHubリポジトリを選択

3. **設定**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && python3 main.py`

## 方法5: 自宅サーバーで公開（固定IPが必要）

### ポートフォワーディング設定

1. ルーターの設定でポート8000をフォワーディング
2. 固定IPを取得（プロバイダーに問い合わせ）
3. ドメインを設定（オプション）

## おすすめ

- **すぐに試したい**: ngrok（5分で完了）
- **本番環境**: Railway または Render（無料枠あり、簡単）
- **エンタープライズ**: VPS + ドメイン

## セキュリティ注意事項

- 本番環境では必ずHTTPSを使用
- 環境変数（APIキーなど）は絶対に公開しない
- 認証機能を必ず有効化
- レート制限を実装（推奨）
