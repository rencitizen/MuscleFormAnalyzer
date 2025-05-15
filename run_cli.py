#!/usr/bin/env python3
"""
BodyScale Pose Analyzer - CLI実行ファイル
コマンドラインモードでMediaPipeを使用して体のスケールを分析
"""
import sys
from main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nプログラムが中断されました。")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nエラーが発生しました: {e}")
        sys.exit(1)