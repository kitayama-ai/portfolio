# Railway設定の簡素化

## 問題

複雑なビルドコマンドが原因でエラーが発生していました。

## 解決方法

RailwayのデフォルトのNixpacks検出を使用し、設定を簡素化しました。

## 変更内容

### 1. nixpacks.tomlを削除
- Railwayのデフォルト検出に任せる

### 2. railway.jsonを簡素化
- カスタムビルドコマンドを削除
- Nixpacksのデフォルト検出を使用

### 3. requirements.txtを修正
- `passlib[bcrypt]` → `bcrypt` に変更（bcryptを直接使用）

### 4. Procfileを簡素化
- `python3.11` → `python` に変更（Railwayが自動検出）

## Web UIでの設定

### Root Directory
**空**（リポジトリのルートを使用）

### Build Command
**削除**（デフォルト検出を使用）

### Start Command
**削除**（Procfileを使用）

または、以下のように設定：
```
cd zoom-recorder-web/backend && python main.py
```

## 自動デプロイ

GitHubにプッシュしたので、自動的に再デプロイが開始されます。

## 確認事項

1. 「Deployments」タブでデプロイ状況を確認
2. ログでエラーがないか確認
3. デプロイ完了後、公開URLにアクセスして動作確認
