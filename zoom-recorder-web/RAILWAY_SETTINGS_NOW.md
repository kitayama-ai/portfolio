# Railway設定（今すぐ実行）

## 必須設定（Web UIで実行）

### ステップ1: Root Directoryを設定

1. Railwayダッシュボードで「portfolio」サービスを開く
2. 「Settings」タブを開く
3. 「Source」セクションで「Root Directory」を以下に設定：
   ```
   zoom-recorder-web
   ```
4. 「Save」をクリック

### ステップ2: Build Commandを設定

1. 「Build」セクションを開く
2. 「Custom Build Command」に以下を設定：
   ```
   pip install --upgrade pip && pip install -r requirements.txt
   ```
3. 「Save」をクリック

### ステップ3: Start Commandを設定

1. 右側サイドバーで「Deploy」をクリック
2. 「Start Command」に以下を設定：
   ```
   cd backend && python main.py
   ```
3. 「Save」をクリック

## 自動デプロイ

設定を保存すると、自動的に再デプロイが開始されます。

## 確認

1. 「Deployments」タブでデプロイ状況を確認
2. ログでエラーがないか確認
3. デプロイ完了後、公開URLにアクセス

## 重要

**Root Directoryを `zoom-recorder-web` に設定することが最も重要です。**
これがないと、Railwayが正しいディレクトリを見つけられません。
