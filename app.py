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
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
app.secret_key = os.environ.get("SESSION_SECRET", "development_key")

# サンプルデータのパス
SAMPLE_METRICS_PATH = 'results/sample_metrics.json'
SAMPLE_TRAINING_PATH = 'results/sample_training_analysis.json'
SAMPLE_EXERCISE_PATH = 'results/sample_exercise_classification.json'

# 結果保存先ディレクトリ
RESULTS_DIR = 'results'

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
        
def load_training_sample():
    """トレーニング分析のサンプルデータを読み込む"""
    try:
        with open(SAMPLE_TRAINING_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"トレーニング分析サンプルデータの読み込みに失敗: {e}")
        return None

def load_exercise_classification_sample():
    """運動分類のサンプルデータを読み込む"""
    try:
        with open(SAMPLE_EXERCISE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"運動分類サンプルデータの読み込みに失敗: {e}")
        return None

@app.route('/')
def index():
    """トップページ - 動画アップロードフォーム"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """動画のアップロードと分析"""
    # 分析タイプの確認
    analysis_type = request.form.get('analysis_type', 'body_metrics')
    
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
        if analysis_type == 'training':
            return redirect(url_for('training_results', mode='sample'))
        elif analysis_type == 'exercise_classification':
            return redirect(url_for('exercise_results', mode='sample'))
        else:
            return redirect(url_for('results', mode='sample'))
    
    file = request.files['video']
    
    if file.filename == '':
        # ファイル名が空の場合もサンプルデータを使用
        logger.info("ファイル名が空です。サンプルデータを使用します。")
        if analysis_type == 'training':
            return redirect(url_for('training_results', mode='sample'))
        elif analysis_type == 'exercise_classification':
            return redirect(url_for('exercise_results', mode='sample'))
        else:
            return redirect(url_for('results', mode='sample'))
    
    if file and file.filename and allowed_file(file.filename):
        # 一意のファイル名を生成
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        new_filename = f"upload_{unique_id}_{filename}"
        
        # アップロードフォルダの存在確認、なければ作成
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # 結果フォルダの存在確認、なければ作成
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        # ファイル保存
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)
        
        logger.info(f"ファイルをアップロードしました: {filepath}")
        
        # 選択された分析タイプに基づいて処理
        if analysis_type == 'training':
            # トレーニングフォーム分析
            exercise_type = request.form.get('exercise_type', 'squat')
            analyzer = TrainingAnalyzer(exercise_type=exercise_type)
            # 実際のシステムでは、ここで動画分析を実行
            # results = analyzer.analyze_video(filepath)
            # analyzer.save_analysis_results(results)
            
            # 現時点ではサンプルデータを使用
            return redirect(url_for('training_results', mode='sample', video_id=unique_id, exercise=exercise_type))
        elif analysis_type == 'exercise_classification':
            # 運動分類分析
            try:
                # 結果ファイルの名前を設定
                result_filename = f'exercise_classification_{unique_id}.json'
                result_path = os.path.join(RESULTS_DIR, result_filename)
                
                # 運動分類器を初期化
                classifier = ExerciseClassifier()
                
                # 動画処理と分類を実行
                processed_data = classifier.process_video(filepath, result_path)
                
                # 分類結果のサマリを生成
                classification_summary = classifier.get_summary()
                
                # サマリをJSONとして保存
                summary_filename = f'exercise_summary_{unique_id}.json'
                summary_path = os.path.join(RESULTS_DIR, summary_filename)
                
                with open(summary_path, 'w') as f:
                    json.dump(classification_summary, f, indent=2)
                
                logger.info(f"運動分類完了: {classification_summary['dominant_exercise']}")
                
                # 結果ページにリダイレクト
                return redirect(url_for('exercise_results', mode='processed', 
                                      video_id=unique_id, 
                                      result_file=result_filename,
                                      summary_file=summary_filename))
            except Exception as e:
                logger.error(f"運動分類処理中にエラーが発生しました: {e}")
                # エラーの場合はサンプルデータを使用
                return redirect(url_for('exercise_results', mode='sample'))
        else:
            # 身体計測分析
            # 現時点ではサンプルデータを使用
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

@app.route('/training_results')
def training_results():
    """トレーニング分析結果の表示"""
    mode = request.args.get('mode', 'sample')
    video_id = request.args.get('video_id', None)
    exercise = request.args.get('exercise', 'squat')
    
    # トレーニング分析データを読み込む
    training_data = load_training_sample()
    
    if not training_data:
        return jsonify({"error": "トレーニング分析データの読み込みに失敗しました"}), 500
    
    # 身体測定データも読み込む
    body_metrics = load_sample_data()
    
    if not body_metrics:
        return jsonify({"error": "身体測定データの読み込みに失敗しました"}), 500
    
    # 両方のデータを統合して、正しい参照構造を持つようにする
    left_arm_cm = body_metrics.get('left_arm_cm', 60)
    right_arm_cm = body_metrics.get('right_arm_cm', 60)
    left_leg_cm = body_metrics.get('left_leg_cm', 90) 
    right_leg_cm = body_metrics.get('right_leg_cm', 90)
    height_cm = body_metrics.get('user_height_cm', 170)
    
    # 平均値と比率を計算
    arm_length_avg = (left_arm_cm + right_arm_cm) / 2
    leg_length_avg = (left_leg_cm + right_leg_cm) / 2
    arm_length_ratio = arm_length_avg / height_cm if height_cm > 0 else 0.35
    leg_length_ratio = leg_length_avg / height_cm if height_cm > 0 else 0.53
    
    training_data['body_metrics'] = {
        'left_arm_cm': left_arm_cm,
        'right_arm_cm': right_arm_cm,
        'left_leg_cm': left_leg_cm,
        'right_leg_cm': right_leg_cm,
        'height_cm': height_cm,
        'arm_length_ratio': arm_length_ratio,
        'leg_length_ratio': leg_length_ratio
    }
    
    return render_template('training_results.html', 
                          training=training_data, 
                          metrics=body_metrics,
                          mode=mode, 
                          video_id=video_id,
                          exercise=exercise)
    
@app.route('/api/metrics')
def api_metrics():
    """メトリクスデータをJSON形式で返す"""
    metrics = load_sample_data()
    
    if not metrics:
        return jsonify({"error": "データの読み込みに失敗しました"}), 500
    
    return jsonify(metrics)
    
@app.route('/api/training')
def api_training():
    """トレーニング分析データをJSON形式で返す"""
    training = load_training_sample()
    
    if not training:
        return jsonify({"error": "トレーニング分析データの読み込みに失敗しました"}), 500
    
    return jsonify(training)

@app.route('/exercise_results')
def exercise_results():
    """運動分類結果の表示"""
    mode = request.args.get('mode', 'sample')
    video_id = request.args.get('video_id', None)
    result_file = request.args.get('result_file', None)
    summary_file = request.args.get('summary_file', None)
    
    # 分類データとサマリを読み込む
    if mode == 'processed' and result_file and summary_file:
        # 処理済みファイルを読み込む
        try:
            result_path = os.path.join(RESULTS_DIR, result_file)
            with open(result_path, 'r', encoding='utf-8') as f:
                classification_data = json.load(f)
            
            summary_path = os.path.join(RESULTS_DIR, summary_file)
            with open(summary_path, 'r', encoding='utf-8') as f:
                classification_summary = json.load(f)
        except Exception as e:
            logger.error(f"運動分類データの読み込みに失敗: {e}")
            # エラーの場合はサンプルデータを使用
            classification_data = load_exercise_classification_sample()
            classification_summary = {
                "dominant_exercise": "サンプルデータ",
                "confidence": 0.85,
                "class_distribution": {"squat": 0.85, "rest": 0.15},
                "frame_count": 120,
                "processing_time": 2.5
            }
    else:
        # サンプルデータを読み込む
        classification_data = load_exercise_classification_sample()
        classification_summary = {
            "dominant_exercise": "サンプルデータ",
            "confidence": 0.85,
            "class_distribution": {"squat": 0.85, "rest": 0.15},
            "frame_count": 120,
            "processing_time": 2.5
        }
    
    if not classification_data:
        return jsonify({"error": "運動分類データの読み込みに失敗しました"}), 500
    
    # 身体測定データも読み込む（表示に使用）
    body_metrics = load_sample_data()
    
    if not body_metrics:
        return jsonify({"error": "身体測定データの読み込みに失敗しました"}), 500
    
    # 必要なデータ構造を確保する
    if not isinstance(body_metrics, dict):
        body_metrics = {}
    
    return render_template('exercise_results.html', 
                          classification=classification_data,
                          summary=classification_summary,
                          metrics=body_metrics,
                          mode=mode, 
                          video_id=video_id)

@app.route('/api/exercise_classification')
def api_exercise_classification():
    """運動分類データをJSON形式で返す"""
    classification = load_exercise_classification_sample()
    
    if not classification:
        return jsonify({"error": "運動分類データの読み込みに失敗しました"}), 500
    
    return jsonify(classification)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)