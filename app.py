from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import json
import uuid
import logging
import shutil
from werkzeug.utils import secure_filename
from training_analysis import TrainingAnalyzer
from exercise_classifier import ExerciseClassifier

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/videos'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'webm'}
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.secret_key = os.environ.get("SESSION_SECRET", "development_key")

RESULTS_DIR = 'results'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    analysis_type = request.form.get('analysis_type', 'body_metrics')
    try:
        height = float(request.form.get('height', 170))
    except ValueError:
        return jsonify({"error": "身長の値が無効です"}), 400

    file = request.files.get('video')
    if not file or file.filename == '':
        logger.info("ファイルなし、サンプル使用")
        return redirect(url_for('training_results', mode='sample'))

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        new_filename = f"upload_{unique_id}_{filename}"
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(RESULTS_DIR, exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)
        logger.info(f"アップロード完了: {filepath}")

        if analysis_type == 'training':
            exercise_type = request.form.get('exercise_type', 'squat')
            analyzer = TrainingAnalyzer(exercise_type=exercise_type)
            results = analyzer.analyze_video(filepath, user_height=height)
            result_file = os.path.join(RESULTS_DIR, f"training_result_{unique_id}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            return redirect(url_for('training_results', mode='processed', result_file=f"training_result_{unique_id}.json"))

    return jsonify({"error": "不正なファイル形式"}), 400

@app.route('/training_results')
def training_results():
    mode = request.args.get('mode', 'sample')
    result_file = request.args.get('result_file')
    if mode == 'processed' and result_file:
        result_path = os.path.join(RESULTS_DIR, result_file)
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            return jsonify({"error": "結果ファイルが見つかりません"}), 404
    elif mode == 'sample':
        # サンプルデータを読み込む
        sample_file = os.path.join(RESULTS_DIR, 'sample_training.json')
        if os.path.exists(sample_file):
            with open(sample_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            return jsonify({"error": "サンプルデータが見つかりません"}), 404
    else:
        return jsonify({"error": "無効なモードです"}), 400
    # メトリクスデータも読み込む
    metrics_file = os.path.join(RESULTS_DIR, 'sample_metrics.json')
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r', encoding='utf-8') as f:
            metrics = json.load(f)
    else:
        metrics = {}
    
    return render_template('training_results.html', training=data, metrics=metrics)

@app.route('/exercise_results')
def exercise_results():
    mode = request.args.get('mode', 'sample')
    result_file = request.args.get('result_file')
    
    # 最初にサマリーデータの初期値を設定
    classification_summary = {
        "dominant_exercise": "squat",
        "confidence": 0.85,
        "class_distribution": {"squat": 75, "rest": 15, "unknown": 10},
        "frame_count": 300,
        "processing_time": 2.5
    }
    
    if mode == 'processed' and result_file:
        result_path = os.path.join(RESULTS_DIR, result_file)
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                classification_data = json.load(f)
                
            # 処理済みデータからサマリーを更新
            classification_summary.update({
                "dominant_exercise": classification_data.get("dominant_exercise", "squat"),
                "confidence": classification_data.get("confidence_score", 85) / 100,
                "class_distribution": classification_data.get("exercise_distribution", 
                                     {"squat": 75, "rest": 15, "unknown": 10}),
                "frame_count": classification_data.get("total_frames", 300)
            })
        else:
            return jsonify({"error": "結果ファイルが見つかりません"}), 404
    elif mode == 'sample':
        # サンプルデータを読み込む
        sample_file = os.path.join(RESULTS_DIR, 'sample_exercises.json')
        if not os.path.exists(sample_file):
            # バックアップファイル名も試す
            sample_file = os.path.join(RESULTS_DIR, 'sample_exercise_classification.json')
            
        if os.path.exists(sample_file):
            with open(sample_file, 'r', encoding='utf-8') as f:
                classification_data = json.load(f)
                
            # サマリーデータを更新
            classification_summary.update({
                "dominant_exercise": classification_data.get("dominant_exercise", "squat"),
                "confidence": classification_data.get("confidence_score", 85) / 100,
                "class_distribution": classification_data.get("exercise_distribution", 
                                     {"squat": 75, "rest": 15, "unknown": 10}),
                "frame_count": classification_data.get("total_frames", 300)
            })
        else:
            return jsonify({"error": "サンプルデータが見つかりません"}), 404
    else:
        return jsonify({"error": "無効なモードです"}), 400
        
    # 必要なデータがあることを確認して、メトリクスデータも追加
    metrics_file = os.path.join(RESULTS_DIR, 'sample_metrics.json')
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r', encoding='utf-8') as f:
            metrics = json.load(f)
    else:
        metrics = {}
    
    return render_template('exercise_results.html', 
                          classification=classification_data,
                          summary=classification_summary,
                          metrics=metrics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
