#!/bin/bash

# Railwayデプロイスクリプト

set -e

echo "🚀 Railwayデプロイを開始します..."

# ディレクトリに移動
cd "$(dirname "$0")"

# Railway CLIがインストールされているか確認
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLIがインストールされていません"
    echo "インストール中..."
    brew install railway
fi

# ログイン状態を確認
if ! railway whoami &> /dev/null; then
    echo "🔐 Railwayにログインが必要です"
    echo "ブラウザが開きます。GitHubアカウントでログインしてください..."
    railway login
    
    # ログイン完了を待つ
    echo "ログインが完了したら、Enterキーを押してください..."
    read
fi

echo "✅ ログイン確認完了"

# プロジェクトが存在するか確認
if ! railway status &> /dev/null; then
    echo "📦 新しいプロジェクトを作成します..."
    railway init
else
    echo "✅ 既存のプロジェクトを使用します"
fi

# 環境変数の確認
echo "📝 環境変数を確認中..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEYが設定されていません"
    echo "環境変数を設定してください:"
    echo "  railway variables set OPENAI_API_KEY=sk-your-api-key-here"
    echo "  railway variables set SECRET_KEY=your-secret-key-here"
    exit 1
fi

# デプロイ
echo "🚀 デプロイを開始します..."
cd backend
railway up

echo "✅ デプロイが完了しました！"
echo "公開URLを確認するには: railway domain"
