# Railway Python環境修正

## エラー内容

```
/usr/bin/python3: No module named pip
```

## 原因

システムのPython3にpipがインストールされていない、またはNixpacksが正しくPython環境をセットアップできていない。

## 修正内容

### 1. Pythonバージョンの明示
- `python3` → `python3.11` に変更
- `.python-version` ファイルを追加

### 2. pipの確実なインストール
- `python3.11 -m ensurepip --upgrade` を追加
- pipを確実にインストールしてから使用

### 3. 設定ファイルの更新
- `nixpacks.toml` - Python 3.11を明示的に指定
- `railway.json` - ビルドコマンドを修正
- `Procfile` - Python 3.11を使用

## 修正後のコマンド

### Build Command
```
cd zoom-recorder-web && python3.11 -m ensurepip --upgrade && python3.11 -m pip install --upgrade pip && python3.11 -m pip install -r requirements.txt
```

### Start Command
```
cd zoom-recorder-web/backend && python3.11 main.py
```

## Web UIでの設定確認

Railwayダッシュボードで以下を確認：

### Build Command
上記のBuild Commandが設定されているか確認

### Start Command
上記のStart Commandが設定されているか確認

## 自動デプロイ

GitHubにプッシュしたので、自動的に再デプロイが開始されます。

## 確認事項

1. 「Deployments」タブでデプロイ状況を確認
2. ログでエラーがないか確認
3. デプロイ完了後、公開URLにアクセスして動作確認
