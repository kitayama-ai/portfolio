# Railway自動設定手順

## ステップ1: Railway CLIでログイン（一度だけ）

ターミナルで以下を実行してください：

```bash
cd zoom-recorder-web
railway login
```

ブラウザが開くので、GitHubアカウントでログインしてください。

## ステップ2: 自動設定スクリプトを実行

ログイン後、以下を実行：

```bash
./setup_railway.sh
```

このスクリプトが以下を自動実行します：
- プロジェクトのリンク
- 環境変数の設定（.envファイルから読み込み）
- 設定の確認

## 手動設定が必要な項目

スクリプト実行後、Railway Web UIで以下を設定してください：

1. **Root Directory**: `zoom-recorder-web/backend`
   - プロジェクト → サービス → Settings → Root Directory

2. **デプロイの確認**
   - Deploymentsタブでデプロイ状況を確認

3. **公開URLの取得**
   - Settingsタブ → Generate Domain

## 環境変数の確認

設定された環境変数を確認：

```bash
railway variables
```

## トラブルシューティング

### ログインできない場合

```bash
railway logout
railway login
```

### プロジェクトが見つからない場合

```bash
railway list
railway link <プロジェクト名>
```
