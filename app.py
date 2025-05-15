from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import json
import uuid
import logging
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/videos'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'webm'}
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
app.secret_key = os.environ.get("SESSION_SECRET", "development_key")

# サンプルデータのパス
SAMPLE_METRICS_PATH = 'results/sample_metrics.json'

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """アップロードされたファイルが許可された拡張子か確認"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_sample_data():
    """サンプルデータを読み込む"""
    try:
        with open(SAMPLE_METRICS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"サンプルデータの読み込みに失敗: {e}")
        return None

@app.route('/')
def index():
    """トップページ - 動画アップロードフォーム"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """動画のアップロードと分析"""
    # 身長の取得
    try:
        height = float(request.form.get('height', 170))
        if height < 100 or height > 250:
            return jsonify({"error": "身長は100cm～250cmの範囲で入力してください"}), 400
    except ValueError:
        return jsonify({"error": "身長の値が無効です"}), 400
    
    # ファイルの確認
    if 'video' not in request.files:
        # ファイルがない場合はサンプルデータを使用
        logger.info("ファイルがアップロードされていません。サンプルデータを使用します。")
        return redirect(url_for('results', mode='sample'))
    
    file = request.files['video']
    
    if file.filename == '':
        # ファイル名が空の場合もサンプルデータを使用
        logger.info("ファイル名が空です。サンプルデータを使用します。")
        return redirect(url_for('results', mode='sample'))
    
    if file and file.filename and allowed_file(file.filename):
        # 一意のファイル名を生成
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        new_filename = f"upload_{unique_id}_{filename}"
        
        # アップロードフォルダの存在確認、なければ作成
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # ファイル保存
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)
        
        logger.info(f"ファイルをアップロードしました: {filepath}")
        
        # ここで実際の分析を行うか、サンプルデータで代用
        # Note: 現時点ではサンプルデータを使用
        
        return redirect(url_for('results', mode='sample', video_id=unique_id))
    
    return jsonify({"error": "許可されていないファイル形式です"}), 400

@app.route('/results')
def results():
    """分析結果の表示"""
    mode = request.args.get('mode', 'sample')
    video_id = request.args.get('video_id', None)
    
    # サンプルデータを読み込む
    metrics = load_sample_data()
    
    if not metrics:
        return jsonify({"error": "データの読み込みに失敗しました"}), 500
    
    return render_template('results.html', metrics=metrics, mode=mode, video_id=video_id)

@app.route('/api/metrics')
def api_metrics():
    """メトリクスデータをJSON形式で返す"""
    metrics = load_sample_data()
    
    if not metrics:
        return jsonify({"error": "データの読み込みに失敗しました"}), 500
    
    return jsonify(metrics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)