# Railway Root Directory エラー修正

## エラー内容

```
Root Directory `zoom-recorder-web/backend` does not exist
```

## 原因

Railwayはリポジトリのルート（`portfolio`）から相対パスでRoot Directoryを探します。
リポジトリのルートが `portfolio` で、その中に `zoom-recorder-web` がある場合、パスは正しいはずですが、Railwayが認識できていない可能性があります。

## 解決方法

### 方法1: Root Directoryを空にする（推奨）

1. Railwayダッシュボードで「Settings」タブを開く
2. 「Root Directory」の入力フィールドを**空にする**
3. 「Save」をクリック
4. 「Build」セクションで以下を設定：
   - **Build Command**: `cd zoom-recorder-web && pip install -r requirements.txt`
   - **Start Command**: `cd zoom-recorder-web/backend && python3 main.py`

### 方法2: Root Directoryを `zoom-recorder-web` に変更

1. 「Settings」タブで「Root Directory」を以下に変更：
   ```
   zoom-recorder-web
   ```
2. 「Build」セクションで以下を設定：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && python3 main.py`

### 方法3: railway.jsonの設定を確認

`railway.json`の設定が正しいか確認：
- Build Command: `cd zoom-recorder-web && pip install -r requirements.txt`
- Start Command: `cd zoom-recorder-web/backend && python3 main.py`

## 推奨設定

### Root Directory
**空**（リポジトリのルートを使用）

### Build Command
```
cd zoom-recorder-web && pip install -r requirements.txt
```

### Start Command
```
cd zoom-recorder-web/backend && python3 main.py
```

## 次のステップ

1. 上記の設定を適用
2. 再デプロイを実行
3. ログを確認してエラーがないか確認
