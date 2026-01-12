#!/bin/bash
# BlackHole自動インストールスクリプト

set -e

echo "🎵 BlackHole 2ch のインストールを開始します..."

# Homebrewがインストールされているか確認
if command -v brew &> /dev/null; then
    echo "✅ Homebrewが見つかりました"
    echo "📦 BlackHoleをインストール中..."
    brew install blackhole-2ch
    echo "✅ BlackHoleのインストールが完了しました"
else
    echo "⚠️  Homebrewが見つかりません"
    echo "📥 BlackHoleを直接ダウンロードします..."
    
    # 一時ディレクトリ
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # 最新リリースのURLを取得
    echo "🔍 最新バージョンを確認中..."
    LATEST_URL=$(curl -s https://api.github.com/repos/ExistentialAudio/BlackHole/releases/latest | \
        grep -o '"browser_download_url": "[^"]*2ch.dmg"' | \
        head -1 | \
        cut -d'"' -f4)
    
    if [ -z "$LATEST_URL" ]; then
        echo "❌ ダウンロードURLの取得に失敗しました"
        echo "手動でインストールしてください: https://github.com/ExistentialAudio/BlackHole/releases"
        exit 1
    fi
    
    echo "📥 ダウンロード中: $LATEST_URL"
    curl -L -o BlackHole.dmg "$LATEST_URL"
    
    # DMGをマウント
    echo "📂 DMGをマウント中..."
    hdiutil attach BlackHole.dmg -quiet -nobrowse -mountpoint /Volumes/BlackHole
    
    # パッケージを探す
    if [ -f /Volumes/BlackHole/BlackHole.pkg ]; then
        PKG_PATH="/Volumes/BlackHole/BlackHole.pkg"
    else
        PKG_PATH=$(find /Volumes/BlackHole -name "*.pkg" | head -1)
    fi
    
    if [ -z "$PKG_PATH" ] || [ ! -f "$PKG_PATH" ]; then
        echo "❌ パッケージファイルが見つかりません"
        hdiutil detach /Volumes/BlackHole -quiet 2>&1 || true
        exit 1
    fi
    
    echo "🔧 インストール中（管理者権限が必要です）..."
    sudo installer -pkg "$PKG_PATH" -target /
    
    # アンマウント
    hdiutil detach /Volumes/BlackHole -quiet 2>&1 || true
    
    # クリーンアップ
    cd /
    rm -rf "$TEMP_DIR"
    
    echo "✅ BlackHoleのインストールが完了しました"
fi

# インストール確認
echo ""
echo "🔍 インストールを確認中..."
if system_profiler SPAudioDataType 2>/dev/null | grep -qi blackhole; then
    echo "✅ BlackHoleが正常にインストールされました！"
    echo ""
    echo "📝 次のステップ:"
    echo "   1. システム環境設定 > サウンド > 出力 を開く"
    echo "   2. 「BlackHole 2ch」を選択"
    echo "   3. Zoom録画ツールを使用開始"
else
    echo "⚠️  BlackHoleがシステムに認識されていません"
    echo "   システムを再起動してから再度確認してください"
fi
