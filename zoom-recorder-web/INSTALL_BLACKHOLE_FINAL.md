# BlackHoleのインストール方法（最終版）

## ⚠️ 重要な発見

GitHubのリリースページ（v0.6.1）には、DMGファイルが含まれていません。
「Source code」のみが提供されています。

## ✅ 推奨インストール方法：Homebrew

### ステップ1: Homebrewのインストール（未インストールの場合）

ターミナルで以下を実行：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

インストール中にパスワードの入力が求められます。

### ステップ2: BlackHoleのインストール

```bash
brew install blackhole-2ch
```

これで完了です！

### ステップ3: システム設定

1. システム環境設定 > サウンド > 出力 を開く
2. 「BlackHole 2ch」を選択

## 確認方法

```bash
system_profiler SPAudioDataType | grep -i blackhole
```

「BlackHole 2ch」が表示されれば成功です。

## 代替方法：公式サイトから直接ダウンロード

もしHomebrewを使いたくない場合：

1. 以下のURLにアクセス：
   https://existential.audio/blackhole/

2. 「Download」セクションから最新版をダウンロード

3. ダウンロードしたDMGファイルを開いてインストール

## トラブルシューティング

### Homebrewのインストールでエラーが出る場合

管理者権限が必要です。ターミナルで実行する際に、パスワードの入力が求められます。

### BlackHoleが表示されない場合

1. システムを再起動
2. システム環境設定 > セキュリティとプライバシー > 一般 で、BlackHoleの許可を確認
