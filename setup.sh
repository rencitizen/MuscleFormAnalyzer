#!/bin/bash
# setup.sh - Claude Code エンジニア組織セットアップスクリプト

echo "Claude Code エンジニア組織構築をセットアップしています..."

# ディレクトリ構造の確認
echo "✓ ディレクトリ構造を作成しました:"
echo "  - instructions/ (各役割の指示書)"
echo "  - temp/todos/ (タスク管理・通信用)"

# 作成されたファイルの確認
echo ""
echo "✓ 以下の指示書を作成しました:"
echo "  - instructions/president.md (プレジデント用)"
echo "  - instructions/boss.md (ボス用)"
echo "  - instructions/worker1.md (フロントエンド開発者用)"
echo "  - instructions/worker2.md (バックエンド開発者用)"
echo "  - instructions/worker3.md (品質管理担当者用)"

echo ""
echo "✓ 通信スクリプトを作成しました:"
echo "  - agent_send.sh (メッセージ送信用)"
echo "  - agent_receive.sh (メッセージ受信用)"

echo ""
echo "=== セットアップ完了 ==="
echo ""
echo "【使用方法】"
echo "1. 各Claude Codeインスタンスを起動"
echo "2. 各インスタンスに対応する指示書の内容をプロンプトとして設定"
echo "   例: cat instructions/president.md"
echo ""
echo "3. エージェント間通信:"
echo "   送信: ./agent_send.sh boss1 \"開発を開始してください\""
echo "   受信: ./agent_receive.sh boss1"
echo ""
echo "【TENAX FIT v3.0 開発開始方法】"
echo "プレジデントインスタンスから以下のコマンドを実行:"
echo "./agent_send.sh boss1 \"\$(cat instructions/president.md | grep -A 100 'agent_send.sh boss1' | head -n 50)\""
echo ""
echo "詳細は各指示書を参照してください。"