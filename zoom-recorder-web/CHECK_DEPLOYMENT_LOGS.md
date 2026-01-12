# Railwayデプロイログ確認方法

## 現在の状況

502エラーが発生しています。デプロイは完了していますが、アプリケーションが起動していない可能性があります。

## 確認手順

### ステップ1: デプロイログを確認

1. Railwayダッシュボードで「portfolio」サービスを開く
2. 「Deployments」タブを開く
3. 最新のデプロイメント（「COMPLETED」）をクリック
4. 「View logs」ボタンをクリック
5. ログを確認して、以下のエラーがないか確認：
   - `ModuleNotFoundError`
   - `ImportError`
   - `FileNotFoundError`
   - `PermissionError`
   - その他のPythonエラー

### ステップ2: 起動ログを確認

ログの最後の部分を確認して、以下のメッセージが表示されているか確認：
- `サーバーを起動します: 0.0.0.0:XXXX`
- `Python version: ...`
- `Working directory: ...`

### ステップ3: エラーの報告

エラーが見つかった場合、エラーメッセージをコピーして報告してください。

## よくあるエラーと解決方法

### ModuleNotFoundError
- 依存関係がインストールされていない
- `requirements.txt`が正しく配置されているか確認

### FileNotFoundError
- ファイルパスが間違っている
- Root Directoryの設定を確認

### PermissionError
- ファイルの実行権限がない
- Procfileの設定を確認
