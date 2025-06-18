#!/bin/bash
# agent_receive.sh - Claude Code エージェントメッセージ受信スクリプト

# 使用方法: ./agent_receive.sh <role>
# 例: ./agent_receive.sh boss1

if [ $# -ne 1 ]; then
    echo "使用方法: $0 <role>"
    echo "role: president, boss1, worker1, worker2, worker3"
    exit 1
fi

ROLE=$1
TODO_DIR="temp/todos"
MESSAGE_FILE="$TODO_DIR/${ROLE}_messages.txt"

if [ -f "$MESSAGE_FILE" ]; then
    echo "=== $ROLE への受信メッセージ ==="
    cat "$MESSAGE_FILE"
    echo ""
    echo "メッセージを既読にしますか？ (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        mv "$MESSAGE_FILE" "$MESSAGE_FILE.read"
        echo "メッセージを既読にしました"
    fi
else
    echo "$ROLE への新しいメッセージはありません"
fi