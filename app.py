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
            results = analyzer.analyze_video(filepath)  # user_heightパラメーターを削除
            # 身長情報を結果に追加
            if 'user_data' not in results:
                results['user_data'] = {}
            results['user_data']['height_cm'] = height
            result_file = os.path.join(RESULTS_DIR, f"training_result_{unique_id}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            return redirect(url_for('training_results', mode='processed', result_file=f"training_result_{unique_id}.json"))

    return jsonify({"error": "不正なファイル形式"}), 400

@app.route('/training_results')
def training_results():
    """
    トレーニング分析ページ (簡易版に置き換え)
    """
    # パラメータを取得
    mode = request.args.get('mode', 'sample')
    exercise_type = request.args.get('exercise_type', 'squat')
    result_file = request.args.get('result_file')
    
    # パラメータを引き継いでシンプル版にリダイレクト
    redirect_url = f'/simple_training?mode={mode}'
    
    if exercise_type:
        redirect_url += f'&exercise_type={exercise_type}'
        
    if result_file:
        redirect_url += f'&result_file={result_file}'
        
    return redirect(redirect_url)

@app.route('/exercise_results')
def exercise_results():
    """
    運動分類ページ (簡易版に置き換え)
    """
    # シンプル版を直接表示
    mode = request.args.get('mode', 'sample')
    result_file = request.args.get('result_file')
    
    # サンプルデータを準備
    sample_data = {
        "dominant_exercise": "スクワット",
        "confidence_score": 85,
        "repetitions": 8,
        "exercise_distribution": {
            "squat": 75,
            "deadlift": 15,
            "lunge": 8,
            "unknown": 2
        },
        "segments": [
            {
                "start_frame": 0,
                "end_frame": 120,
                "exercise": "squat",
                "confidence": 88
            }
        ]
    }
    
    # サンプルファイルがあれば読み込む
    sample_file = os.path.join(RESULTS_DIR, 'sample_exercises.json')
    if os.path.exists(sample_file):
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
        except:
            pass  # エラーが起きたら既存のサンプルデータを使用
            
    # シンプルな HTML を直接返す
    return f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>運動分類結果</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
    </head>
    <body class="bg-dark text-light">
        <div class="container py-5">
            <div class="card bg-dark text-light mb-4">
                <div class="card-header">
                    <h2>運動分類結果</h2>
                    <a href="/" class="btn btn-outline-light">ホームに戻る</a>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h4>基本情報</h4>
                            <p>主要運動種目: {sample_data.get('dominant_exercise', 'スクワット')}</p>
                            <p>信頼度: {sample_data.get('confidence_score', 85)}%</p>
                            <p>レップ数: {sample_data.get('repetitions', 8)}</p>
                        </div>
                        <div class="col-md-6">
                            <h4>運動内訳</h4>
                            <ul>
                                <li>スクワット: {sample_data.get('exercise_distribution', {}).get('squat', 75)}%</li>
                                <li>デッドリフト: {sample_data.get('exercise_distribution', {}).get('deadlift', 15)}%</li>
                                <li>ランジ: {sample_data.get('exercise_distribution', {}).get('lunge', 8)}%</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <a href="/" class="btn btn-primary">ホームに戻る</a>
        </div>
    </body>
    </html>
    """

@app.route('/test')
def test_route():
    """テスト用の簡単なページ"""
    return """
    <html>
    <head><title>テストページ</title></head>
    <body>
        <h1>テストページ - 正常に動作しています</h1>
        <p>以下のリンクをクリックしてください：</p>
        <ul>
            <li><a href="/training_results?mode=sample">トレーニング分析</a></li>
            <li><a href="/exercise_results?mode=sample">運動分類</a></li>
            <li><a href="/simple_training?mode=sample">シンプルトレーニング分析</a></li>
        </ul>
    </body>
    </html>
    """

@app.route('/simple_training')
def simple_training():
    """シンプルなトレーニング分析ページ"""
    mode = request.args.get('mode', 'sample')
    exercise_type = request.args.get('exercise_type', 'squat')
    result_file = request.args.get('result_file', '')
    
    if mode == 'processed' and result_file and os.path.exists(os.path.join(RESULTS_DIR, result_file)):
        # 処理済みファイルを読み込む
        try:
            with open(os.path.join(RESULTS_DIR, result_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded processed data: {result_file}")
        except Exception as e:
            logger.error(f"Error loading processed file: {e}")
            data = {}
    elif mode == 'sample':
        # 選択されたトレーニング種目に対応するサンプルを読み込む
        exercise_files = {
            'squat': 'sample_training_squat.json',
            'bench_press': 'sample_training_bench.json',
            'deadlift': 'sample_training_deadlift.json',
            'overhead_press': 'sample_training_overhead.json'
        }
        
        # 対応するサンプルファイルを検索
        sample_file = os.path.join(RESULTS_DIR, exercise_files.get(exercise_type, 'sample_training.json'))
        
        # ファイルが存在しない場合はデフォルトのサンプルファイルを使用
        if not os.path.exists(sample_file):
            sample_file = os.path.join(RESULTS_DIR, 'sample_training.json')
            
        # サンプルファイルを読み込む
        if os.path.exists(sample_file):
            try:
                with open(sample_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded sample data: {sample_file}")
            except Exception as e:
                logger.error(f"Error loading sample file: {e}")
                data = {}
        else:
            # サンプルデータがない場合は種目に基づいた基本データを作成
            exercise_names = {
                'squat': 'スクワット',
                'bench_press': 'ベンチプレス',
                'deadlift': 'デッドリフト',
                'overhead_press': 'オーバーヘッドプレス'
            }
            data = {
                "exercise_type": exercise_type,
                "exercise_name": exercise_names.get(exercise_type, "不明なエクササイズ"),
                "rep_count": 8,
                "form_score": 85,
                "depth_score": 80,
                "tempo_score": 75,
                "balance_score": 82,
                "stability_score": 78,
                "issues": ["膝が内側に入る", "背中が丸まる"],
                "strengths": ["姿勢が安定している"],
                "advice": ["膝をつま先と同じ方向に向けましょう", "背中をまっすぐに保ちましょう"],
                "body_metrics": {
                    "height_cm": 170,
                    "left_arm_cm": 62.5,
                    "right_arm_cm": 62.8
                }
            }
    else:
        # それ以外のモードの場合は基本的なデータを返す
        data = {
            "exercise_type": exercise_type,
            "exercise_name": "分析データなし",
            "rep_count": 0,
            "form_score": 0
        }
    
    return render_template('simple_training.html', training=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
