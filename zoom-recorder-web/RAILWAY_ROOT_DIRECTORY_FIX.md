# Railway Root Directory設定（必須）

## 現在の状況

502エラーが発生しています。これは、Railwayが正しいディレクトリを見つけられていないためです。

## 解決方法（Web UIで実行）

### ステップ1: Settingsを開く

1. Railwayダッシュボードで「portfolio」サービスを開く
2. 「Settings」タブをクリック

### ステップ2: Root Directoryを設定

1. 「Source」セクションを開く
2. 「Root Directory」フィールドを確認
3. **以下のいずれかを設定：**

   **オプションA（推奨）**: 空にする（削除）
   - Root Directoryフィールドを空にする
   - これにより、Railwayはリポジトリのルートから自動検出します

   **オプションB**: `zoom-recorder-web` に設定
   - Root Directoryフィールドに `zoom-recorder-web` を入力

4. 「Save」をクリック

### ステップ3: 再デプロイ

1. 「Deployments」タブを開く
2. 最新のデプロイメントの「Redeploy」ボタンをクリック
3. または、GitHubに新しいコミットをプッシュ（自動デプロイ）

## 確認

デプロイ完了後：
1. 「Deployments」タブでログを確認
2. エラーがないか確認
3. 公開URLにアクセス：https://portfolio-production-0ac7.up.railway.app

## 重要

**Root Directoryの設定が最も重要です。** これがないと、Railwayが正しいディレクトリを見つけられず、502エラーが発生します。
