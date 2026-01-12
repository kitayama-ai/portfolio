# Railway最終設定（Web UIで確認）

## 修正内容

### 1. Build Commandの修正
- **変更前**: `cd zoom-recorder-web && pip install -r requirements.txt`
- **変更後**: `cd zoom-recorder-web && python3 -m pip install -r requirements.txt`

### 2. 設定ファイルの更新
- `railway.json` - Build Commandを修正
- `nixpacks.toml` - pipのアップグレードを追加
- `runtime.txt` - Python 3.11を指定
- `Procfile` - Start Commandを明示

## Web UIでの設定確認

### Root Directory
**空**（リポジトリのルートを使用）

### Build Command
```
cd zoom-recorder-web && python3 -m pip install -r requirements.txt
```

### Start Command
```
cd zoom-recorder-web/backend && python3 main.py
```

## 自動デプロイ

GitHubにプッシュしたので、自動的に再デプロイが開始されます。

## 確認事項

1. 「Deployments」タブでデプロイ状況を確認
2. ログでエラーがないか確認
3. デプロイ完了後、公開URLにアクセスして動作確認

## 環境変数

「Variables」タブで以下が設定されているか確認：
- `OPENAI_API_KEY`
- `SECRET_KEY`
