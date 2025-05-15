"""
BodyScale Pose Analyzer - Webアプリケーションエントリーポイント
"""
from app import app  # Import Flask application

# このファイルが直接実行された場合
if __name__ == '__main__':
    # サーバーをポート5000で起動
    app.run(host='0.0.0.0', port=5000, debug=True)