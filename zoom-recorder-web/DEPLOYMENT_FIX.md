# Railwayデプロイ修正

## 問題

502エラーが発生し、アプリケーションが起動していません。

## 原因

RailwayのRoot Directory設定が正しくない可能性があります。

## 解決方法

### Web UIでの設定（必須）

1. Railwayダッシュボードで「portfolio」サービスを開く
2. 「Settings」タブを開く
3. 「Source」セクションで「Root Directory」を **空** に設定（削除）
4. 「Save」をクリック

### 自動検出

Root Directoryを空にすることで、Railwayは以下を自動検出します：
- `requirements.txt`（リポジトリのルート）
- `Procfile`（リポジトリのルート）

### 確認

デプロイ完了後、以下を確認：
- 「Deployments」タブでデプロイログを確認
- エラーがないか確認
- 公開URLにアクセスして動作確認
