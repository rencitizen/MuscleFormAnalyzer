"""
BodyScale Pose Analyzer - Flask サーバーモジュール
サーバーモードでの実行とコマンドラインモードの両方をサポート
"""
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Flaskアプリケーションの初期化
app = Flask(__name__)

@app.route('/')
def index():
    """ホームページ"""
    return """
    <html>
        <head>
            <title>BodyScale Pose Analyzer</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #333; }
                p { max-width: 600px; }
                .button {
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h1>BodyScale Pose Analyzer</h1>
            <p>このツールは、動画から姿勢推定を行い、ユーザーの身長を元に実寸法（cm単位）で体の各部位を計測します。</p>
            <p>使用方法:</p>
            <ol>
                <li>コマンドラインで <code>python main.py</code> を実行</li>
                <li>身長を入力（前回値があればそれを使用可能）</li>
                <li>分析する動画ファイルを選択</li>
                <li>分析結果が <code>results/body_metrics.json</code> に保存されます</li>
            </ol>
            <p>
                <a href="/run" class="button">コマンドラインでの実行を開始</a>
            </p>
        </body>
    </html>
    """

@app.route('/run')
def run():
    """メインスクリプトをバックグラウンドで実行"""
    # 注意: 実際の環境では非同期処理やバックグラウンドジョブがより適切
    os.system('python main.py &')
    return redirect(url_for('status'))

@app.route('/status')
def status():
    """実行状態を表示"""
    return """
    <html>
        <head>
            <title>実行状態 - BodyScale Pose Analyzer</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #333; }
                p { max-width: 600px; }
                .status { 
                    background-color: #f0f0f0;
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <h1>BodyScale Pose Analyzer - 実行状態</h1>
            <p>プログラムがバックグラウンドで起動されました。</p>
            <div class="status">
                <p>コンソールウィンドウで操作を続けてください。GUI操作の場合はポップアップウィンドウに注目してください。</p>
                <p>分析結果は <code>results/body_metrics.json</code> に保存されます。</p>
            </div>
            <p><a href="/">ホームに戻る</a></p>
        </body>
    </html>
    """

# このファイルが直接実行された場合はFlaskサーバーを起動
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)