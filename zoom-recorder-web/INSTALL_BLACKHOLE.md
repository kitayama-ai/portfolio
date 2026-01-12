# BlackHoleのインストール手順

Zoom録画ツールを使用するには、BlackHole（仮想オーディオデバイス）のインストールが必要です。

## 方法1: Homebrewを使用（推奨）

### 1. Homebrewのインストール（未インストールの場合）

ターミナルで以下のコマンドを実行：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

インストール中にパスワードの入力が求められる場合があります。

### 2. BlackHoleのインストール

```bash
brew install blackhole-2ch
```

### 3. システム設定

1. システム環境設定 > サウンド > 出力 を開く
2. 「BlackHole 2ch」を選択
3. Zoomで会議に参加する前に、この設定を確認してください

## 方法2: 公式サイトから直接ダウンロード

1. 以下のURLにアクセス：
   https://github.com/ExistentialAudio/BlackHole/releases

2. 最新バージョンの「BlackHole-2ch.dmg」をダウンロード

3. ダウンロードしたDMGファイルを開き、BlackHole.pkgを実行

4. インストールウィザードに従ってインストール

5. システム環境設定 > サウンド > 出力 で「BlackHole 2ch」を選択

## 確認方法

インストール後、以下のコマンドで確認できます：

```bash
system_profiler SPAudioDataType | grep -i blackhole
```

「BlackHole 2ch」が表示されれば、インストール成功です。

## トラブルシューティング

### BlackHoleが表示されない場合

1. システムを再起動
2. システム環境設定 > セキュリティとプライバシー > 一般 で、BlackHoleの許可を確認
3. 必要に応じて、BlackHoleを再インストール

### 録画時に音声が取得できない場合

1. システム環境設定 > サウンド > 出力 で「BlackHole 2ch」が選択されているか確認
2. Zoomの音声出力設定を確認
3. 録画を開始する前に、BlackHoleが選択されていることを確認
