#!/bin/bash
# agent_send.sh - Claude Code エージェント間通信スクリプト

# 使用方法: ./agent_send.sh <recipient> "message"
# 例: ./agent_send.sh boss1 "プロジェクトを開始してください"

if [ $# -ne 2 ]; then
    echo "使用方法: $0 <recipient> \"message\""
    echo "recipient: president, boss1, worker1, worker2, worker3"
    exit 1
fi

RECIPIENT=$1
MESSAGE=$2
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# メッセージを保存するディレクトリ
TODO_DIR="temp/todos"
mkdir -p "$TODO_DIR"

# メッセージファイル名
MESSAGE_FILE="$TODO_DIR/${RECIPIENT}_messages.txt"

# メッセージを追加
echo "[$TIMESTAMP] $MESSAGE" >> "$MESSAGE_FILE"

echo "メッセージを $RECIPIENT に送信しました: $MESSAGE"
echo "受信者は以下のコマンドでメッセージを確認できます:"
echo "cat $MESSAGE_FILE"