#!/bin/bash

# Railway設定スクリプト

set -e

echo "🚀 Railway設定を開始します..."

cd "$(dirname "$0")"

# Railway CLIがインストールされているか確認
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLIがインストールされていません"
    echo "インストール中..."
    brew install railway
fi

# ログイン確認
if ! railway whoami &> /dev/null; then
    echo "🔐 Railwayにログインが必要です"
    echo "ブラウザが開きます。GitHubアカウントでログインしてください..."
    railway login
    
    echo "ログインが完了したら、Enterキーを押してください..."
    read
fi

echo "✅ ログイン確認完了"

# プロジェクトリストを表示
echo ""
echo "📋 利用可能なプロジェクト:"
railway list

echo ""
echo "プロジェクト名またはIDを入力してください:"
read PROJECT_NAME

# プロジェクトにリンク
if [ -n "$PROJECT_NAME" ]; then
    echo "🔗 プロジェクトにリンク中..."
    railway link "$PROJECT_NAME" 2>&1 || railway link
fi

# 現在のプロジェクト情報を表示
echo ""
echo "📊 現在のプロジェクト情報:"
railway status

# 環境変数を設定
echo ""
echo "📝 環境変数を設定中..."

# .envファイルから環境変数を読み込む
if [ -f ".env" ]; then
    echo ".envファイルから環境変数を読み込みます..."
    
    # OPENAI_API_KEY
    if grep -q "OPENAI_API_KEY=" .env; then
        OPENAI_KEY=$(grep "OPENAI_API_KEY=" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'")
        if [ -n "$OPENAI_KEY" ] && [ "$OPENAI_KEY" != "sk-your-api-key-here" ]; then
            echo "  - OPENAI_API_KEYを設定中..."
            railway variables set OPENAI_API_KEY="$OPENAI_KEY" 2>&1 || echo "  ⚠️  OPENAI_API_KEYの設定に失敗しました"
        fi
    fi
    
    # SECRET_KEY
    if grep -q "SECRET_KEY=" .env; then
        SECRET_KEY=$(grep "SECRET_KEY=" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'")
        if [ -n "$SECRET_KEY" ] && [ "$SECRET_KEY" != "your-secret-key-change-in-production" ]; then
            echo "  - SECRET_KEYを設定中..."
            railway variables set SECRET_KEY="$SECRET_KEY" 2>&1 || echo "  ⚠️  SECRET_KEYの設定に失敗しました"
        else
            # デフォルトのSECRET_KEYを生成
            NEW_SECRET=$(openssl rand -hex 32)
            echo "  - SECRET_KEYを生成して設定中..."
            railway variables set SECRET_KEY="$NEW_SECRET" 2>&1 || echo "  ⚠️  SECRET_KEYの設定に失敗しました"
        fi
    fi
else
    echo "⚠️  .envファイルが見つかりません"
    echo "環境変数を手動で設定してください:"
    echo "  railway variables set OPENAI_API_KEY=sk-your-api-key-here"
    echo "  railway variables set SECRET_KEY=your-secret-key-here"
fi

# 設定された環境変数を表示
echo ""
echo "📋 設定された環境変数:"
railway variables

echo ""
echo "✅ 設定が完了しました！"
echo ""
echo "次のステップ:"
echo "1. RailwayダッシュボードでRoot Directoryを 'zoom-recorder-web/backend' に設定"
echo "2. デプロイを確認: railway logs"
echo "3. 公開URLを取得: railway domain"
