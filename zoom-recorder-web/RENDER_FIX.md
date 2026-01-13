# Renderビルドエラー修正

## 問題

ビルドコマンドで以下のエラーが発生していました：

```
bash: 行 1: cd: zoom-recorder-web: そのようなファイルまたはディレクトリはありません
```

## 原因

Root Directoryが `zoom-recorder-web` に設定されている場合、Build CommandとStart Commandは既にそのディレクトリ内で実行されます。
そのため、`cd zoom-recorder-web` は不要で、パスが重複していました。

## 修正内容

### render.yaml
- **Build Command**: `cd zoom-recorder-web && pip install -r requirements.txt` 
  → `pip install -r requirements.txt`
- **Start Command**: `cd zoom-recorder-web/backend && python main.py` 
  → `cd backend && python main.py`
- **rootDir**: `zoom-recorder-web` を明示的に追加

### Render Web UIでの設定

Renderダッシュボードで以下を確認・修正してください：

1. **Settings** → **Build & Deploy** セクション
2. **Root Directory**: `zoom-recorder-web` に設定されているか確認
3. **Build Command**: `pip install -r requirements.txt` に変更
4. **Start Command**: `cd backend && python main.py` に変更
5. 「Save Changes」をクリック
6. 「Manual Deploy」で再デプロイ

## 修正後の動作

- Root Directoryが `zoom-recorder-web` なので、ビルドは既にそのディレクトリ内で実行されます
- Build Commandは `requirements.txt` を直接参照できます
- Start Commandは `backend` ディレクトリに移動してから実行されます
