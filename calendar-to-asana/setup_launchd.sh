#!/bin/bash
# launchdに登録するスクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="$SCRIPT_DIR/com.calendar-to-asana.plist"
MAIN_PY="$SCRIPT_DIR/main.py"

# plistファイルのパスを更新
sed -i '' "s|REPLACE_WITH_FULL_PATH_TO_MAIN_PY|$MAIN_PY|g" "$PLIST_FILE"

# LaunchAgentsディレクトリにコピー
cp "$PLIST_FILE" ~/Library/LaunchAgents/

# launchdに読み込み
launchctl load ~/Library/LaunchAgents/com.calendar-to-asana.plist

echo "launchdに登録しました"
echo "削除する場合は: launchctl unload ~/Library/LaunchAgents/com.calendar-to-asana.plist"
