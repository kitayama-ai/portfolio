# クイックスタートガイド

## BlackHoleのインストール方法

### 方法1: ターミナルから実行（推奨）

1. **ターミナルを開く**
   - `Cmd + Space` を押して Spotlight を開く
   - 「ターミナル」と入力して Enter
   - または、アプリケーション > ユーティリティ > ターミナル

2. **以下のコマンドをコピー＆ペーストして実行**

```bash
cd "/Users/yamatokitada/マイドライブ（yamato.kitada@cyan-inc.net）/Cursor/portfolio/zoom-recorder-web"
./install_blackhole.sh
```

3. **パスワードを入力**
   - 管理者パスワードの入力が求められます
   - パスワードを入力して Enter（画面には表示されませんが、正常です）

4. **完了**
   - インストールが完了したら、システム環境設定 > サウンド > 出力 で「BlackHole 2ch」を選択

### 方法2: Cursorのターミナルから実行

1. Cursorの下部にあるターミナルパネルを開く
2. 以下のコマンドを実行：

```bash
cd zoom-recorder-web
./install_blackhole.sh
```

### 方法3: Homebrewが既にインストールされている場合

ターミナルで以下を実行：

```bash
brew install blackhole-2ch
```

## サーバーの起動方法

### GUIアプリから起動（簡単）

```bash
cd zoom-recorder-web
python3 installer/server_launcher.py
```

「サーバーを起動」ボタンをクリック

### コマンドラインから起動

```bash
cd zoom-recorder-web/backend
python3 main.py
```

## ブラウザでアクセス

サーバー起動後、ブラウザで以下にアクセス：

```
http://localhost:8000
```

## トラブルシューティング

### スクリプトが実行できない場合

```bash
chmod +x install_blackhole.sh
./install_blackhole.sh
```

### Pythonが見つからない場合

```bash
python3 --version
```

Python 3.8以上が必要です。
