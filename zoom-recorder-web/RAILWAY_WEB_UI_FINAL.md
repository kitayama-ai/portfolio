# Railway Web UI最終設定（必須）

## 現在の状態

✅ 設定ファイルを修正してGitHubにプッシュ済み
⏳ Web UIでの設定確認が必要

## Web UIで設定すべき項目（重要）

### 1. Root Directory（Sourceセクション）

**設定値**: `zoom-recorder-web`

1. 「Settings」タブ → 「Source」セクション
2. 「Root Directory」を `zoom-recorder-web` に設定
3. 「Save」をクリック

### 2. Build Command（Buildセクション）

**設定値**:
```
pip install --upgrade pip && pip install -r requirements.txt
```

1. 「Settings」タブ → 「Build」セクション
2. 「Custom Build Command」に上記のコマンドを設定
3. 「Save」をクリック

### 3. Start Command（Deployセクション）

**設定値**:
```
cd backend && python main.py
```

1. 「Settings」タブ → 右側サイドバーで「Deploy」をクリック
2. 「Start Command」に上記のコマンドを設定
3. 「Save」をクリック

## 設定の理由

Root Directoryを `zoom-recorder-web` に設定することで：
- Railwayは `zoom-recorder-web/requirements.txt` を自動検出
- Build Commandは `zoom-recorder-web` ディレクトリ内で実行される
- Start Commandは `zoom-recorder-web/backend` から実行される

## 自動デプロイ

設定を保存すると、自動的に再デプロイが開始されます。

## 確認事項

1. 「Deployments」タブでデプロイ状況を確認
2. ログでエラーがないか確認
3. デプロイ完了後、公開URLにアクセスして動作確認
