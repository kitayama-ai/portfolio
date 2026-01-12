# BlackHoleのインストール方法（簡単版）

## ⚠️ 重要な注意

GitHubのリリースページで「Source code (zip)」や「Source code (tar.gz)」は**ダウンロードしないでください**。

これらはソースコードで、インストールには使えません。

## ✅ 正しいダウンロード方法

### 方法1: 自動インストールスクリプト（推奨・一番簡単）

Cursorのターミナルで以下を実行：

```bash
cd zoom-recorder-web
./install_blackhole.sh
```

これで自動的に正しいファイルをダウンロードしてインストールします。

### 方法2: 手動でDMGファイルをダウンロード

1. 以下のURLにアクセス：
   https://github.com/ExistentialAudio/BlackHole/releases/latest

2. **「Assets」セクションを展開**（クリックして開く）

3. **「BlackHole-2ch.dmg」** というファイルを探してダウンロード
   - ⚠️ 「Source code」はダウンロードしない
   - ✅ 「.dmg」ファイルをダウンロード

4. ダウンロードしたDMGファイルを開く

5. 表示された「BlackHole.pkg」をダブルクリックしてインストール

6. インストール後、システム環境設定 > サウンド > 出力 で「BlackHole 2ch」を選択

## 確認方法

インストールが成功したか確認：

```bash
system_profiler SPAudioDataType | grep -i blackhole
```

「BlackHole 2ch」が表示されれば成功です。
