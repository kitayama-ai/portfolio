# Railway Start Command設定方法

## Start Commandの設定場所

Start Commandは「Build」セクションではなく、「Deploy」セクションにあります。

## 設定手順

### ステップ1: Deployセクションに移動

1. 右側のサイドバーで「Deploy」をクリック
2. または、Settingsページをスクロールして「Deploy」セクションを探す

### ステップ2: Start Commandを設定

「Deploy」セクションで以下を設定：

**Start Command:**
```
cd zoom-recorder-web/backend && python3 main.py
```

または、Root Directoryを空にした場合：
```
cd zoom-recorder-web/backend && python3 main.py
```

## 現在の設定確認

### Build Command（既に設定済み）
```
cd zoom-recorder-web && pip install -r requirements.txt
```

### Start Command（設定が必要）
```
cd zoom-recorder-web/backend && python3 main.py
```

## 代替方法

もし「Deploy」セクションが見つからない場合：

### 方法1: railway.jsonを使用
`railway.json`ファイルに既に設定されているので、Railwayが自動的に読み込む可能性があります。

### 方法2: Root Directoryを `zoom-recorder-web` に設定
1. 「Source」セクションで「Root Directory」を `zoom-recorder-web` に設定
2. 「Build」セクションで「Start Command」を以下に設定：
   ```
   cd backend && python3 main.py
   ```

## 推奨設定（まとめ）

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

1. 右側のサイドバーで「Deploy」をクリック
2. 「Start Command」を設定
3. 保存
4. 再デプロイ
