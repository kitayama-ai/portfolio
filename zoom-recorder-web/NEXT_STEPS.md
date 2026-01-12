# 再起動後の次のステップ

## ✅ 完了したこと

- [x] Homebrewのインストール
- [x] BlackHole 2chのインストール
- [x] システム再起動（実行中）

## 📋 再起動後にやること

### ステップ1: BlackHoleのインストール確認

ターミナルで以下を実行：

```bash
system_profiler SPAudioDataType | grep -i blackhole
```

「BlackHole 2ch」が表示されれば成功です。

### ステップ2: システム環境設定でBlackHoleを選択

1. **システム環境設定**を開く
2. **サウンド** > **出力** を開く
3. **「BlackHole 2ch」**を選択
4. これでZoomの音声がBlackHole経由で録音できるようになります

### ステップ3: 環境変数の設定

プロジェクトルート（`zoom-recorder-web`）に`.env`ファイルを作成：

```bash
cd zoom-recorder-web
```

`.env`ファイルを作成して、以下を設定：

```env
# OpenAI API（必須）
OPENAI_API_KEY=sk-your-api-key-here

# Slack（オプション）
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_CHANNEL=#meeting-notes

# JWT秘密鍵（本番環境では強力なランダム文字列に変更）
SECRET_KEY=your-secret-key-change-in-production
```

### ステップ4: 依存パッケージのインストール

```bash
cd zoom-recorder-web
pip install -r requirements.txt
```

### ステップ5: サーバーの起動

#### 方法1: GUIアプリから起動（推奨）

```bash
cd zoom-recorder-web
python3 installer/server_launcher.py
```

「サーバーを起動」ボタンをクリック

#### 方法2: コマンドラインから起動

```bash
cd zoom-recorder-web/backend
python3 main.py
```

### ステップ6: ブラウザでアクセス

サーバー起動後、ブラウザで以下にアクセス：

```
http://localhost:8000
```

### ステップ7: 初回ログイン

1. 「新規登録」をクリック
2. ユーザー名、メールアドレス、パスワードを入力
3. 登録後、自動的にログインされます

### ステップ8: 設定の確認

1. 右上の⚙️ボタンをクリック
2. **録画フォルダ**と**ドキュメントフォルダ**を設定
3. 必要に応じてGoogleドキュメント連携を有効化

### ステップ9: 動作確認

1. Zoomで会議に参加
2. ブラウザで「Zoom状態」が「会議中」になることを確認
3. 「録画開始」ボタンをクリック
4. 録画が開始されることを確認

## 🔍 トラブルシューティング

### BlackHoleが表示されない場合

```bash
# システムを再起動
sudo reboot
```

### サーバーが起動しない場合

```bash
# Pythonのバージョン確認
python3 --version

# 依存パッケージの再インストール
pip install -r requirements.txt --upgrade
```

### ポート8000が既に使用されている場合

`backend/main.py`の最後の行を変更：

```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # ポートを変更
```

## 📝 メモ

- プロジェクト名: `zoom-recorder-web`
- GitHubリポジトリ: `https://github.com/kitayama-ai/portfolio`
- プロジェクトパス: `/Users/yamatokitada/マイドライブ（yamato.kitada@cyan-inc.net）/Cursor/portfolio/zoom-recorder-web`

## 🎯 次の開発タスク

- [ ] 動作テスト
- [ ] エラー修正（あれば）
- [ ] 機能追加（必要に応じて）
