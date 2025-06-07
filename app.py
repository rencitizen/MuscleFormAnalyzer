from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, flash, session, make_response
from flask_cors import CORS
import os
import json
import uuid
import logging
import shutil
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

# ログ設定を先に行う
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from analysis.training_analysis import TrainingAnalyzer

# Machine Learning Integration
try:
    from ml.api.inference import MLInferenceEngine
    ML_ENGINE = MLInferenceEngine()
    ML_AVAILABLE = True
    logger.info("機械学習エンジンが初期化されました")
except ImportError as e:
    ML_ENGINE = None
    ML_AVAILABLE = False
    logger.warning(f"機械学習モジュールが利用できません: {e}")
except Exception as e:
    ML_ENGINE = None
    ML_AVAILABLE = False
    logger.warning(f"機械学習エンジン初期化エラー: {e}")

# Training Data Collection Integration
try:
    from ml.data.training_data_collector import TrainingDataCollector
    DATA_COLLECTOR = TrainingDataCollector()
    COLLECTION_AVAILABLE = True
    logger.info("データ収集システムが初期化されました")
except ImportError as e:
    DATA_COLLECTOR = None
    COLLECTION_AVAILABLE = False
    logger.warning(f"データ収集モジュールが利用できません: {e}")
except Exception as e:
    DATA_COLLECTOR = None
    COLLECTION_AVAILABLE = False
    logger.warning(f"データ収集システム初期化エラー: {e}")
from core.exercise_classifier import ExerciseClassifier
from utils.workout_models import workout_db
from core.exercise_database import (
    EXERCISE_DATABASE, get_all_exercises, search_exercises, 
    get_exercises_by_category, get_exercise_by_id, COMMON_WEIGHTS, get_weight_suggestions
)
from utils.auth_models import AuthManager
auth_manager = AuthManager()

# Import meal analysis blueprint
try:
    from ml.api.simple_meal_analysis import meal_bp
    MEAL_ANALYSIS_AVAILABLE = True
    logger.info("食事分析モジュールが初期化されました")
except ImportError as e:
    meal_bp = None
    MEAL_ANALYSIS_AVAILABLE = False
    logger.warning(f"食事分析モジュールが利用できません: {e}")
except Exception as e:
    meal_bp = None
    MEAL_ANALYSIS_AVAILABLE = False
    logger.warning(f"食事分析モジュール初期化エラー: {e}")

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
app.config['UPLOAD_FOLDER'] = 'static/videos'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'webm'}
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.secret_key = os.environ.get("SESSION_SECRET", "development_key")

RESULTS_DIR = 'results'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register meal analysis blueprint
if MEAL_ANALYSIS_AVAILABLE and meal_bp:
    app.register_blueprint(meal_bp, url_prefix='/meal')
    logger.info("食事分析ブループリントを登録しました")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    # 認証チェック
    if not session.get('user_email'):
        return redirect('/login')
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
            
            # まず身体寸法を測定
            from core.analysis import BodyAnalyzer
            body_analyzer = BodyAnalyzer(user_height_cm=height)
            body_metrics = {}
            
            try:
                # 動画から身体寸法を分析
                import cv2
                import mediapipe as mp
                
                cap = cv2.VideoCapture(filepath)
                mp_pose = mp.solutions.pose
                pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)
                
                # 複数フレームを取得して身体寸法を測定（精度向上）
                measurements = []
                frame_count = 0
                max_frames = 5  # 最大5フレームで測定
                
                while frame_count < max_frames:
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results_pose = pose.process(frame_rgb)
                    
                    if results_pose.pose_landmarks:
                        # ランドマークを辞書形式に変換
                        landmarks = {}
                        h, w, _ = frame.shape
                        for idx, landmark in enumerate(results_pose.pose_landmarks.landmark):
                            landmarks[idx] = {
                                'x': landmark.x * w,
                                'y': landmark.y * h,
                                'z': landmark.z,
                                'visibility': landmark.visibility
                            }
                        
                        # 身体寸法を分析
                        measurement = body_analyzer.analyze_landmarks(landmarks, (w, h))
                        measurements.append(measurement)
                        frame_count += 1
                
                # 複数測定の平均値を計算
                if measurements:
                    body_metrics = {
                        'user_height_cm': height,
                        'left_arm_cm': sum(m.get('left_arm_cm', 0) for m in measurements) / len(measurements),
                        'right_arm_cm': sum(m.get('right_arm_cm', 0) for m in measurements) / len(measurements),
                        'left_leg_cm': sum(m.get('left_leg_cm', 0) for m in measurements) / len(measurements),
                        'right_leg_cm': sum(m.get('right_leg_cm', 0) for m in measurements) / len(measurements),
                        'measurements_count': len(measurements)
                    }
                    logger.info(f"身体寸法測定完了（{len(measurements)}フレーム平均）: {body_metrics}")
                        
                cap.release()
                
            except Exception as e:
                logger.warning(f"身体寸法測定中にエラー: {e}")
            
            # 身体寸法データを使ってトレーニング分析を実行
            analyzer = TrainingAnalyzer(exercise_type=exercise_type, body_metrics=body_metrics)
            results = analyzer.analyze_video(filepath)
            
            # 身長情報と身体寸法情報を結果に追加
            if 'user_data' not in results:
                results['user_data'] = {}
            results['user_data']['height_cm'] = height
            results['user_data']['body_metrics'] = body_metrics
            
            result_file = os.path.join(RESULTS_DIR, f"training_result_{unique_id}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            return redirect(url_for('training_results', mode='processed', result_file=f"training_result_{unique_id}.json"))
        
        elif analysis_type == 'body_metrics':
            # 身体寸法分析の処理
            from core.analysis import BodyAnalyzer
            body_analyzer = BodyAnalyzer(user_height_cm=height)
            try:
                # 動画から身体寸法を分析
                import cv2
                import mediapipe as mp
                
                cap = cv2.VideoCapture(filepath)
                mp_pose = mp.solutions.pose
                pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)
                
                # 最初のフレームを取得して分析
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results_pose = pose.process(frame_rgb)
                    
                    if results_pose.pose_landmarks:
                        # ランドマークを辞書形式に変換
                        landmarks = {}
                        h, w, _ = frame.shape
                        for idx, landmark in enumerate(results_pose.pose_landmarks.landmark):
                            landmarks[idx] = {
                                'x': landmark.x * w,
                                'y': landmark.y * h,
                                'z': landmark.z,
                                'visibility': landmark.visibility
                            }
                        
                        # 身体寸法を分析
                        body_results = body_analyzer.analyze_landmarks(landmarks, (w, h))
                        result_filename = f"body_metrics_{unique_id}.json"
                        result_file = os.path.join(RESULTS_DIR, result_filename)
                        body_analyzer.save_results(body_results, result_filename)
                        
                        cap.release()
                        return redirect(url_for('body_metrics_results', result_file=f"body_metrics_{unique_id}.json"))
                    else:
                        cap.release()
                        return jsonify({"error": "ポーズが検出されませんでした"}), 400
                else:
                    cap.release()
                    return jsonify({"error": "動画の読み込みに失敗しました"}), 400
                    
            except Exception as e:
                logger.error(f"身体寸法分析エラー: {e}")
                return jsonify({"error": f"分析エラー: {str(e)}"}), 500
        
        else:
            return jsonify({"error": "不明な分析タイプです"}), 400

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

@app.route('/body_metrics_results')
def body_metrics_results():
    """身体寸法測定結果ページ"""
    result_file = request.args.get('result_file')
    
    if result_file:
        try:
            result_path = os.path.join(RESULTS_DIR, result_file)
            with open(result_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return render_template('body_metrics.html', data=data)
        except Exception as e:
            logger.error(f"Error loading body metrics data: {e}")
            return render_template('body_metrics.html', error="データの読み込みに失敗しました")
    else:
        return render_template('body_metrics.html', error="結果ファイルが指定されていません")

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

# ===== トレーニング記録機能のルート =====

@app.route('/workout_log')
def workout_log():
    """トレーニング記録メインページ"""
    return render_template('workout_record.html')

@app.route('/workout_record')
def workout_record():
    """トレーニング記録専用ページ"""
    return render_template('workout_record.html')

@app.route('/add_workout', methods=['POST'])
def add_workout():
    """ワークアウト記録を追加するAPI"""
    try:
        data = request.get_json()
        
        # ユーザーIDを取得（セッションまたは入力から）
        user_id = data.get('user_id') or session.get('user_email', 'default_user')
        
        # ユーザーIDが設定されていない場合は簡易設定
        if user_id == 'default_user':
            user_email = data.get('user_email', f'user_{uuid.uuid4().hex[:8]}@local.app')
            session['user_email'] = user_email
            user_id = user_email
            
        # シンプルなユーザー管理（外部キー制約なしで直接保存）
        
        # 必須フィールドの検証
        required_fields = ['date', 'exercise', 'weight', 'reps']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}は必須です'}), 400
        
        # ユーザープロファイルを作成/更新
        workout_db.create_user_profile(user_id, data.get('height_cm'))
        
        # ワークアウト記録を追加
        workout_id = workout_db.add_workout(
            user_id=user_id,
            date=data['date'],
            exercise=data['exercise'],
            exercise_name=data.get('exercise_name', data['exercise']),
            weight_kg=float(data['weight']),
            reps=int(data['reps']),
            notes=data.get('notes'),
            form_analysis_ref=data.get('form_analysis_ref')
        )
        
        if workout_id:
            return jsonify({
                'success': True,
                'message': 'ワークアウト記録を追加しました',
                'workout_id': workout_id
            })
        else:
            return jsonify({'error': 'データベースエラーが発生しました'}), 500
            
    except Exception as e:
        logger.error(f"ワークアウト追加エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_workouts', methods=['GET'])
def get_workouts():
    """ワークアウト記録を取得するAPI"""
    try:
        user_id = session.get('user_email', 'default_user')
        view_type = request.args.get('view', 'detailed')  # detailed または summary
        
        if view_type == 'summary':
            # 部位別集計データを取得
            summary = workout_db.get_workouts_summary_by_category(user_id)
            
            # 日付を文字列に変換
            for item in summary:
                if item.get('latest_date'):
                    item['latest_date'] = item['latest_date'].strftime('%Y-%m-%d')
            
            return jsonify({'summary': summary})
        else:
            # 詳細データを取得
            limit = int(request.args.get('limit', 50))
            workouts = workout_db.get_workouts_by_user(user_id, limit)
            
            # 日付を文字列に変換
            for workout in workouts:
                if workout.get('date'):
                    workout['date'] = workout['date'].strftime('%Y-%m-%d')
                if workout.get('created_at'):
                    workout['created_at'] = workout['created_at'].isoformat()
                if workout.get('updated_at'):
                    workout['updated_at'] = workout['updated_at'].isoformat()
            
            return jsonify({'workouts': workouts})
        
    except Exception as e:
        logger.error(f"ワークアウト取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_workouts_by_category/<category>', methods=['GET'])
def get_workouts_by_category(category):
    """特定部位のワークアウト記録を取得するAPI"""
    try:
        user_id = session.get('user_email', 'default_user')
        workouts = workout_db.get_workouts_by_category(user_id, category)
        
        # 日付を文字列に変換
        for workout in workouts:
            if workout.get('date'):
                workout['date'] = workout['date'].strftime('%Y-%m-%d')
            if workout.get('created_at'):
                workout['created_at'] = workout['created_at'].isoformat()
            if workout.get('updated_at'):
                workout['updated_at'] = workout['updated_at'].isoformat()
        
        return jsonify({'workouts': workouts})
        
    except Exception as e:
        logger.error(f"カテゴリ別ワークアウト取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete_workout/<int:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    """ワークアウト記録を削除するAPI"""
    try:
        user_id = session.get('user_email', 'default_user')
        
        success = workout_db.delete_workout(workout_id, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'ワークアウト記録を削除しました'
            })
        else:
            return jsonify({'error': '記録が見つからないか削除できませんでした'}), 404
            
    except Exception as e:
        logger.error(f"ワークアウト削除エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_chart_progress/<exercise>')
def get_chart_progress(exercise):
    """特定種目の進捗データを取得するAPI"""
    try:
        user_id = session.get('user_email', 'default_user')
        
        progress_data = workout_db.get_exercise_progress(user_id, exercise)
        
        # データが存在しない場合の処理
        if not progress_data:
            return jsonify({'dates': [], 'weights': []})
        
        # 日付を文字列に変換
        for record in progress_data:
            if record.get('date'):
                record['date'] = record['date'].strftime('%Y-%m-%d')
        
        return jsonify({'progress': progress_data})
        
    except Exception as e:
        logger.error(f"進捗データ取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/max_weights')
def get_max_weights():
    """各種目の最大重量を取得するAPI"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        
        max_weights = workout_db.get_max_weights(user_id)
        
        return jsonify({'max_weights': max_weights})
        
    except Exception as e:
        logger.error(f"最大重量取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

# ===== 機械学習API =====

@app.route('/api/ml/analyze_pose', methods=['POST'])
def ml_analyze_pose():
    """機械学習によるポーズ分析API"""
    try:
        data = request.get_json()
        landmarks = data.get('landmarks', {})
        
        if not landmarks:
            return jsonify({'error': 'ランドマークデータが必要です'}), 400
        
        if ML_AVAILABLE and ML_ENGINE:
            result = ML_ENGINE.analyze_pose(landmarks)
        else:
            # フォールバック: 基本的な分析
            result = {
                'success': True,
                'exercise_type': 'unknown',
                'confidence': 0.5,
                'quality': 'basic',
                'analysis': {
                    'form_score': 70,
                    'feedback': ['基本的な分析を実行中'],
                    'corrections': []
                },
                'timestamp': datetime.now().isoformat(),
                'note': '機械学習エンジンが利用できません'
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"ML分析エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/batch_analyze', methods=['POST'])
def ml_batch_analyze():
    """セッション全体のバッチ分析API"""
    try:
        data = request.get_json()
        session_data = data.get('session_data', [])
        
        if not session_data:
            return jsonify({'error': 'セッションデータが必要です'}), 400
        
        if ML_AVAILABLE and ML_ENGINE:
            result = ML_ENGINE.batch_analyze(session_data)
        else:
            # フォールバック: 基本的な統計
            result = {
                'success': True,
                'session_summary': {
                    'total_frames': len(session_data),
                    'dominant_exercise': 'unknown',
                    'average_confidence': 0.5,
                    'session_quality': 'basic'
                },
                'timestamp': datetime.now().isoformat(),
                'note': '機械学習エンジンが利用できません'
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"MLバッチ分析エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/model_info')
def ml_model_info():
    """機械学習モデル情報取得API"""
    try:
        if ML_AVAILABLE and ML_ENGINE:
            result = ML_ENGINE.get_model_info()
        else:
            result = {
                'is_initialized': False,
                'model_type': 'none',
                'supported_exercises': [],
                'note': '機械学習エンジンが利用できません',
                'timestamp': datetime.now().isoformat()
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"MLモデル情報取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/train', methods=['POST'])
def ml_train_model():
    """モデル学習API（管理者用）"""
    try:
        data = request.get_json()
        days = data.get('days', 30)
        
        # 実際のプロダクション環境では認証が必要
        # セキュリティチェック
        
        if not ML_AVAILABLE:
            return jsonify({
                'success': False,
                'error': '機械学習モジュールが利用できません'
            }), 400
        
        # バックグラウンドでの学習実行（実際の実装では非同期処理を推奨）
        try:
            from ml.scripts.train_model import ModelTrainer
            trainer = ModelTrainer()
            result = trainer.full_training_pipeline(days)
            
            return jsonify(result)
            
        except ImportError:
            return jsonify({
                'success': False,
                'error': '学習スクリプトモジュールが利用できません'
            }), 500
        
    except Exception as e:
        logger.error(f"ML学習エラー: {e}")
        return jsonify({'error': str(e)}), 500

# ===== New ML Model APIs =====

@app.route('/api/ml/classify_exercise', methods=['POST'])
def ml_classify_exercise():
    """Exercise classification API"""
    try:
        from ml.models.exercise_classifier import ExerciseClassifier
        
        data = request.get_json()
        landmarks = data.get('landmarks', [])
        
        if not landmarks:
            return jsonify({'error': 'Landmarks data required'}), 400
        
        # Initialize classifier
        classifier = ExerciseClassifier(use_ml=False)  # Start with rule-based
        
        # Classify single frame
        result = classifier.classify_exercise(landmarks)
        
        return jsonify({
            'success': True,
            'exercise': result['exercise'],
            'confidence': result['confidence'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Exercise classification error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/detect_phases', methods=['POST'])
def ml_detect_phases():
    """Phase detection API"""
    try:
        from ml.models.phase_detector import PhaseDetector, analyze_exercise_phases
        
        data = request.get_json()
        landmark_sequence = data.get('landmark_sequence', [])
        exercise_type = data.get('exercise_type', 'squat')
        fps = data.get('fps', 30.0)
        
        if not landmark_sequence:
            return jsonify({'error': 'Landmark sequence required'}), 400
        
        # Convert to numpy arrays
        import numpy as np
        landmark_arrays = []
        for frame in landmark_sequence:
            if isinstance(frame, list) and len(frame) == 33:
                landmark_arrays.append(np.array(frame))
        
        if not landmark_arrays:
            return jsonify({'error': 'Invalid landmark data format'}), 400
        
        # Analyze phases
        results = analyze_exercise_phases(
            landmark_arrays,
            exercise_type,
            fps
        )
        
        return jsonify({
            'success': True,
            **results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Phase detection error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/evaluate_form', methods=['POST'])
def ml_evaluate_form():
    """Form evaluation API"""
    try:
        from ml.models.form_evaluator import FormEvaluator, evaluate_exercise_sequence
        
        data = request.get_json()
        landmarks = data.get('landmarks', None)
        landmark_sequence = data.get('landmark_sequence', None)
        exercise_type = data.get('exercise_type', 'squat')
        phase = data.get('phase', None)
        
        if landmarks:
            # Single frame evaluation
            import numpy as np
            landmarks_array = np.array(landmarks)
            
            evaluator = FormEvaluator(exercise_type)
            result = evaluator.evaluate_form(landmarks_array, phase)
            
            return jsonify({
                'success': True,
                'type': 'single_frame',
                **result,
                'timestamp': datetime.now().isoformat()
            })
            
        elif landmark_sequence:
            # Sequence evaluation
            import numpy as np
            landmark_arrays = []
            for frame in landmark_sequence:
                if isinstance(frame, list) and len(frame) == 33:
                    landmark_arrays.append(np.array(frame))
            
            if not landmark_arrays:
                return jsonify({'error': 'Invalid landmark sequence format'}), 400
            
            results = evaluate_exercise_sequence(
                landmark_arrays,
                exercise_type
            )
            
            return jsonify({
                'success': True,
                'type': 'sequence',
                **results,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Either landmarks or landmark_sequence required'}), 400
        
    except Exception as e:
        logger.error(f"Form evaluation error: {e}")
        return jsonify({'error': str(e)}), 500

# ===== データ収集API =====

@app.route('/data_consent')
def data_consent_page():
    """データ利用同意ページ"""
    return render_template('data_consent.html')

@app.route('/training_data')
def training_data():
    """データ管理ページ（エイリアス）"""
    return render_template('training_data_management.html')

@app.route('/training_data_management')
def training_data_management():
    """データ管理ページ"""
    return render_template('training_data_management.html')

@app.route('/data_preprocessing')
def data_preprocessing_page():
    """データ前処理ページ"""
    return render_template('data_preprocessing.html')

@app.route('/exercise_database')
def exercise_database_page():
    """エクササイズデータベースページ"""
    return render_template('exercise_database.html')

@app.route('/meal_analysis')
def meal_analysis_page():
    """食事分析ページ"""
    return render_template('meal_analysis.html')

@app.route('/nutrition_tracking')
def nutrition_tracking_page():
    """栄養トラッキングページ"""
    return render_template('nutrition_tracking.html')

@app.route('/api/data_consent', methods=['POST'])
def record_data_consent():
    """データ利用同意を記録"""
    try:
        data = request.get_json()
        consent_given = data.get('consent_given', False)
        purpose_acknowledged = data.get('purpose_acknowledged', False)
        
        user_id = session.get('user_email', 'default_user')
        
        if COLLECTION_AVAILABLE and DATA_COLLECTOR:
            success = DATA_COLLECTOR.record_user_consent(
                user_id=user_id,
                consent_given=consent_given,
                purpose_acknowledged=purpose_acknowledged
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '同意を記録しました',
                    'consent_given': consent_given
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '同意の記録に失敗しました'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'データ収集システムが利用できません'
            }), 503
            
    except Exception as e:
        logger.error(f"同意記録エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data_consent/status')
def get_consent_status():
    """ユーザーの同意状況を取得"""
    try:
        user_id = session.get('user_email', 'default_user')
        
        if COLLECTION_AVAILABLE and DATA_COLLECTOR:
            consent_status = DATA_COLLECTOR.check_user_consent(user_id)
            return jsonify(consent_status)
        else:
            return jsonify({
                'has_consent': False,
                'needs_consent': False,
                'can_collect': False,
                'error': 'データ収集システムが利用できません'
            })
            
    except Exception as e:
        logger.error(f"同意状況確認エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training_data/collect', methods=['POST'])
def collect_training_data():
    """トレーニングデータを収集"""
    try:
        data = request.get_json()
        
        # 必須フィールドの確認
        required_fields = ['exercise', 'pose_data', 'metadata', 'performance']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field}が必要です'}), 400
        
        user_id = session.get('user_email', 'default_user')
        
        if COLLECTION_AVAILABLE and DATA_COLLECTOR:
            result = DATA_COLLECTOR.collect_training_data(
                user_id=user_id,
                exercise=data['exercise'],
                pose_data=data['pose_data'],
                metadata=data['metadata'],
                performance=data['performance']
            )
            
            if result.get('success'):
                return jsonify(result)
            else:
                return jsonify(result), 400
        else:
            return jsonify({
                'success': False,
                'error': 'データ収集システムが利用できません'
            }), 503
            
    except Exception as e:
        logger.error(f"データ収集エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training_data/opt_out', methods=['POST'])
def opt_out_data_collection():
    """データ収集からオプトアウト"""
    try:
        user_id = session.get('user_email', 'default_user')
        
        if COLLECTION_AVAILABLE and DATA_COLLECTOR:
            success = DATA_COLLECTOR.record_opt_out(user_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'オプトアウトを記録しました'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'オプトアウトの記録に失敗しました'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'データ収集システムが利用できません'
            }), 503
            
    except Exception as e:
        logger.error(f"オプトアウトエラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training_data/stats')
def get_collection_stats():
    """データ収集統計を取得（管理者用）"""
    try:
        # 実際の運用では管理者認証が必要
        
        if COLLECTION_AVAILABLE and DATA_COLLECTOR:
            stats = DATA_COLLECTOR.get_collection_stats()
            return jsonify(stats)
        else:
            return jsonify({
                'error': 'データ収集システムが利用できません'
            }), 503
            
    except Exception as e:
        logger.error(f"統計取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training_data/export')
def export_training_data():
    """トレーニングデータをエクスポート（管理者用）"""
    try:
        # パラメータ取得
        exercise_filter = request.args.get('exercise')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        format_type = request.args.get('format', 'csv')
        
        # 実際の運用では管理者認証が必要
        
        if COLLECTION_AVAILABLE and DATA_COLLECTOR:
            exported_data = DATA_COLLECTOR.export_training_data(
                exercise_filter=exercise_filter,
                date_from=date_from,
                date_to=date_to,
                format=format_type
            )
            
            # レスポンスヘッダー設定
            if format_type.lower() == 'csv':
                response = make_response(exported_data)
                response.headers['Content-Type'] = 'text/csv'
                response.headers['Content-Disposition'] = 'attachment; filename=training_data.csv'
            else:
                response = make_response(exported_data)
                response.headers['Content-Type'] = 'application/json'
                response.headers['Content-Disposition'] = 'attachment; filename=training_data.json'
            
            return response
        else:
            return jsonify({
                'error': 'データ収集システムが利用できません'
            }), 503
            
    except Exception as e:
        logger.error(f"データエクスポートエラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training_data/delete_user_data', methods=['DELETE'])
def delete_user_training_data():
    """ユーザーのトレーニングデータを削除（GDPR対応）"""
    try:
        user_id = session.get('user_email', 'default_user')
        
        if COLLECTION_AVAILABLE and DATA_COLLECTOR:
            success = DATA_COLLECTOR.delete_user_data(user_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'ユーザーデータを削除しました'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'データ削除に失敗しました'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'データ収集システムが利用できません'
            }), 503
            
    except Exception as e:
        logger.error(f"ユーザーデータ削除エラー: {e}")
        return jsonify({'error': str(e)}), 500

# ===== データ前処理API =====

@app.route('/api/preprocessing/run', methods=['POST'])
def run_preprocessing_pipeline():
    """前処理パイプラインの実行"""
    try:
        data = request.get_json()
        exercise_filter = data.get('exercise_filter')
        data_limit = data.get('limit', 500)
        augmentation_factor = data.get('augmentation_factor', 2)
        
        if COLLECTION_AVAILABLE and DATA_COLLECTOR:
            # 前処理パイプラインを実行
            try:
                from ml.scripts.preprocessing import TrainingDataPreprocessor
                
                preprocessor = TrainingDataPreprocessor()
                
                # 1. 生データの読み込み
                raw_data = preprocessor.load_raw_data(
                    exercise_filter=exercise_filter,
                    limit=data_limit
                )
                
                if not raw_data:
                    return jsonify({
                        'success': False,
                        'error': '処理対象のデータが見つかりません'
                    }), 400
                
                # 2. データクリーニング
                cleaned_data = preprocessor.clean_data(raw_data)
                
                # 3. 特徴量エンジニアリング
                featured_data = preprocessor.extract_features(cleaned_data)
                
                # 4. 正規化
                normalized_data = preprocessor.normalize_data(featured_data)
                
                # 5. データ拡張
                augmented_data = preprocessor.augment_data(
                    normalized_data, 
                    augmentation_factor=augmentation_factor
                )
                
                # 6. 保存
                preprocessor.save_processed_data(augmented_data)
                
                return jsonify({
                    'success': True,
                    'message': '前処理パイプラインが完了しました',
                    'statistics': {
                        'raw_samples': len(raw_data),
                        'cleaned_samples': len(cleaned_data),
                        'featured_samples': len(featured_data),
                        'final_samples': len(augmented_data),
                        'processing_date': datetime.now().isoformat()
                    }
                })
                
            except ImportError:
                return jsonify({
                    'success': False,
                    'error': '前処理モジュールが利用できません'
                }), 500
                
        else:
            return jsonify({
                'success': False,
                'error': 'データ収集システムが利用できません'
            }), 503
            
    except Exception as e:
        logger.error(f"前処理パイプラインエラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/preprocessing/validate', methods=['POST'])
def validate_processed_data():
    """処理済みデータの品質検証"""
    try:
        data = request.get_json()
        data_dir = data.get('data_dir', 'ml/data/processed')
        
        try:
            from ml.scripts.data_validation import DataQualityValidator
            
            validator = DataQualityValidator()
            validation_report = validator.validate_processed_data(data_dir)
            
            return jsonify({
                'success': True,
                'validation_report': validation_report
            })
            
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'データ検証モジュールが利用できません'
            }), 500
            
    except Exception as e:
        logger.error(f"データ検証エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/preprocessing/feature_engineering', methods=['POST'])
def run_feature_engineering():
    """高度な特徴量エンジニアリングの実行"""
    try:
        data = request.get_json()
        pose_data = data.get('pose_data')
        exercise = data.get('exercise', 'squat')
        metadata = data.get('metadata', {})
        
        if not pose_data:
            return jsonify({
                'success': False,
                'error': 'ポーズデータが必要です'
            }), 400
        
        try:
            from ml.scripts.feature_engineering import AdvancedFeatureEngineer
            
            engineer = AdvancedFeatureEngineer()
            
            # フォーム品質特徴量の抽出
            form_features = engineer.extract_form_quality_features(
                pose_data, exercise, metadata
            )
            
            # 時系列特徴量の抽出（複数フレームの場合）
            temporal_features = {}
            if isinstance(pose_data[0], list) and len(pose_data) > 1:
                temporal_features = engineer.extract_temporal_features(
                    pose_data, exercise
                )
            
            # 特徴量を統合
            all_features = {**form_features, **temporal_features}
            
            return jsonify({
                'success': True,
                'features': all_features,
                'feature_count': len(all_features),
                'exercise': exercise
            })
            
        except ImportError:
            return jsonify({
                'success': False,
                'error': '特徴量エンジニアリングモジュールが利用できません'
            }), 500
            
    except Exception as e:
        logger.error(f"特徴量エンジニアリングエラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/preprocessing/status')
def get_preprocessing_status():
    """前処理パイプラインの状況確認"""
    try:
        status = {
            'available_modules': {
                'preprocessing': False,
                'feature_engineering': False,
                'data_validation': False
            },
            'processed_data_status': {},
            'recommendations': []
        }
        
        # モジュールの利用可能性チェック
        try:
            from ml.scripts.preprocessing import TrainingDataPreprocessor
            status['available_modules']['preprocessing'] = True
        except ImportError:
            pass
        
        try:
            from ml.scripts.feature_engineering import AdvancedFeatureEngineer
            status['available_modules']['feature_engineering'] = True
        except ImportError:
            pass
        
        try:
            from ml.scripts.data_validation import DataQualityValidator
            status['available_modules']['data_validation'] = True
        except ImportError:
            pass
        
        # 処理済みデータの存在確認
        processed_dir = 'ml/data/processed'
        datasets = ['train.csv', 'val.csv', 'test.csv']
        
        for dataset in datasets:
            file_path = os.path.join(processed_dir, dataset)
            status['processed_data_status'][dataset] = {
                'exists': os.path.exists(file_path),
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat() if os.path.exists(file_path) else None
            }
        
        # 推奨事項の生成
        if not any(status['available_modules'].values()):
            status['recommendations'].append('前処理モジュールが利用できません。依存関係を確認してください。')
        
        if not any(ds['exists'] for ds in status['processed_data_status'].values()):
            status['recommendations'].append('処理済みデータが見つかりません。前処理パイプラインを実行してください。')
        
        # データ収集統計も含める
        if COLLECTION_AVAILABLE and DATA_COLLECTOR:
            collection_stats = DATA_COLLECTOR.get_collection_stats()
            status['collection_stats'] = collection_stats
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"前処理状況確認エラー: {e}")
        return jsonify({'error': str(e)}), 500

# ===== データ可視化API =====

@app.route('/dashboard')
def dashboard():
    """統計ダッシュボードページ"""
    return render_template('dashboard.html')

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """ダッシュボード統計データを取得"""
    try:
        user_id = session.get('user_email', 'default_user')
        stats = workout_db.get_dashboard_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"ダッシュボード統計取得エラー: {e}")
        return jsonify({'error': str(e)}), 500



@app.route('/get_calendar_data')
def get_calendar_data():
    """カレンダー用のトレーニングデータを取得"""
    try:
        user_id = session.get('user_email', 'default_user')
        year = request.args.get('year', default=datetime.now().year, type=int)
        month = request.args.get('month', default=datetime.now().month, type=int)
        calendar_data = workout_db.get_calendar_data(user_id, year, month)
        return jsonify(calendar_data)
    except Exception as e:
        logger.error(f"カレンダーデータ取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

# ===== Firebase認証システム =====

@app.route('/login')
def login_page():
    """ログインページ"""
    # 既にログインしている場合はリダイレクト
    if session.get('user_email'):
        return redirect('/')
    return render_template('login.html')

@app.route('/register')
def register_page():
    """新規登録ページ"""
    # 既にログインしている場合はリダイレクト
    if session.get('user_email'):
        return redirect('/')
    return render_template('register.html')

@app.route('/firebase-config')
def firebase_config():
    """Firebase設定を提供"""
    config = {
        'apiKey': os.environ.get('FIREBASE_API_KEY'),
        'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.environ.get('FIREBASE_PROJECT_ID'),
        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.environ.get('FIREBASE_APP_ID')
    }
    return jsonify(config)

@app.route('/firebase-login', methods=['POST'])
def firebase_login():
    """Firebase IDトークンでログイン"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'success': False, 'error': 'IDトークンが必要です'}), 400
        
        # Firebase IDトークンの検証（実装時にfirebase_authを使用）
        # 現在は簡易実装
        session['firebase_token'] = id_token
        
        # メールアドレスをセッションに保存（実際の実装では検証済みトークンから取得）
        email = data.get('email', 'firebase_user@example.com')
        session['user_email'] = email
        session['auth_method'] = 'firebase'
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Firebase ログインエラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/firebase-register', methods=['POST'])
def firebase_register():
    """Firebase IDトークンで新規登録"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        email = data.get('email')
        
        if not id_token or not email:
            return jsonify({'success': False, 'error': 'IDトークンとメールが必要です'}), 400
        
        # ユーザープロファイルを作成
        workout_db.create_user_profile(email)
        
        return jsonify({'success': True, 'message': 'アカウントを作成しました'})
        
    except Exception as e:
        logger.error(f"Firebase 登録エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def traditional_login():
    """従来のメール・パスワードログイン"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'メールとパスワードが必要です'}), 400
        
        # 既存の認証システムを使用
        auth_result = auth_manager.authenticate_user_simple(email, password)
        
        if auth_result.get('success'):
            session['user_email'] = email
            session['auth_method'] = 'traditional'
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'メールアドレスまたはパスワードが正しくありません'}), 401
            
    except Exception as e:
        logger.error(f"ログインエラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/register', methods=['POST'])
def traditional_register():
    """従来のメール・パスワード新規登録"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'メールとパスワードが必要です'}), 400
        
        # 既存の認証システムを使用
        auth_result = auth_manager.create_user(email, password)
        
        if auth_result.get('success'):
            # ユーザープロファイルを作成
            workout_db.create_user_profile(email)
            return jsonify({'success': True, 'message': 'アカウントを作成しました'})
        else:
            return jsonify({'success': False, 'error': auth_result.get('error', '登録に失敗しました')}), 400
            
    except Exception as e:
        logger.error(f"登録エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/logout')
def logout_page():
    """ログアウトページ"""
    auth_method = session.get('auth_method')
    
    if auth_method == 'firebase':
        # Firebase セッション削除
        session.pop('firebase_token', None)
    
    # セッションクリア
    session.pop('user_email', None)
    session.pop('auth_method', None)
    
    return redirect('/login')

@app.route('/forgot-password')
def forgot_password_page():
    """パスワードリセットページ"""
    return render_template('forgot_password.html')

# ===== 設定管理API =====

@app.route('/settings')
def settings_page():
    """設定ページ"""
    # 認証チェック
    if not session.get('user_email'):
        return redirect('/login')
    return render_template('settings.html')

@app.route('/set_language', methods=['POST'])
def set_language():
    """言語設定API"""
    try:
        data = request.get_json()
        language = data.get('language', 'ja')
        session['language'] = language
        return jsonify({'status': 'success', 'language': language})
    except Exception as e:
        logger.error(f"言語設定エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_settings', methods=['GET'])
def get_settings():
    """設定情報を取得"""
    try:
        user_id = session.get('user_email', 'default_user')
        settings = workout_db.get_user_settings(user_id)
        return jsonify(settings)
    except Exception as e:
        logger.error(f"設定取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/save_personal_settings', methods=['POST'])
def save_personal_settings():
    """個人情報設定を保存"""
    try:
        user_id = session.get('user_email', 'default_user')
        data = request.get_json()
        
        success = workout_db.save_user_settings(user_id, data)
        if success:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': '保存に失敗しました'}), 500
    except Exception as e:
        logger.error(f"個人情報保存エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/data', methods=['GET'])
def export_user_data():
    """ユーザーデータをエクスポート"""
    try:
        user_id = session.get('user_email', 'default_user')
        data = workout_db.export_user_data(user_id)
        
        response = make_response(jsonify(data))
        response.headers['Content-Disposition'] = 'attachment; filename=bodyscale_data.json'
        response.headers['Content-Type'] = 'application/json'
        return response
    except Exception as e:
        logger.error(f"データエクスポートエラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/clear', methods=['POST'])
def clear_user_data():
    """ユーザーデータを削除"""
    try:
        user_id = session.get('user_email', 'default_user')
        success = workout_db.clear_user_data(user_id)
        if success:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': '削除に失敗しました'}), 500
    except Exception as e:
        logger.error(f"データ削除エラー: {e}")
        return jsonify({'error': str(e)}), 500

# ===== 種目データベースAPI =====

@app.route('/api/exercises/categories')
def get_exercise_categories():
    """部位別カテゴリー一覧を取得"""
    try:
        categories = []
        for category_key, category in EXERCISE_DATABASE.items():
            categories.append({
                'id': category_key,
                'name': category['name'],
                'icon': category['icon'],
                'subcategories': list(category['subcategories'].keys())
            })
        return jsonify({'categories': categories})
    except Exception as e:
        logger.error(f"カテゴリー取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/exercises/category/<category>')
def get_exercises_by_category_api(category):
    """部位別で種目を取得"""
    try:
        exercises = get_exercises_by_category(category)
        return jsonify({'exercises': exercises})
    except Exception as e:
        logger.error(f"カテゴリー別種目取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/exercises/search')
def search_exercises_api():
    """種目検索API"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'exercises': []})
        
        exercises = search_exercises(query)
        return jsonify({'exercises': exercises})
    except Exception as e:
        logger.error(f"種目検索エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/exercises/all')
def get_all_exercises_api():
    """全種目を取得"""
    try:
        exercises = get_all_exercises()
        return jsonify({'exercises': exercises})
    except Exception as e:
        logger.error(f"全種目取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/weights/suggestions')
def get_weight_suggestions_api():
    """重量選択候補を取得"""
    try:
        current_weight = request.args.get('current', type=float)
        count = request.args.get('count', 20, type=int)
        
        weights = get_weight_suggestions(current_weight, count)
        return jsonify({'weights': weights})
    except Exception as e:
        logger.error(f"重量候補取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

# ===== リアルタイムポーズ分析API =====

@app.route('/api/analyze', methods=['POST'])
def analyze_pose():
    """リアルタイムポーズ分析API"""
    try:
        data = request.get_json()
        
        # 必須フィールドの検証
        if not data or 'landmarks' not in data:
            return jsonify({'error': 'ランドマークデータが必要です'}), 400
        
        landmarks = data['landmarks']
        exercise_type = data.get('exercise_type', 'squat')
        frame_number = data.get('frame_number', 0)
        
        # 角度計算
        angles = {}
        
        # MediaPipeのランドマークインデックス
        LEFT_SHOULDER = 11
        LEFT_ELBOW = 13
        LEFT_WRIST = 15
        LEFT_HIP = 23
        LEFT_KNEE = 25
        LEFT_ANKLE = 27
        RIGHT_SHOULDER = 12
        RIGHT_ELBOW = 14
        RIGHT_WRIST = 16
        RIGHT_HIP = 24
        RIGHT_KNEE = 26
        RIGHT_ANKLE = 28
        
        # 膝角度の計算
        if all(str(i) in landmarks for i in [LEFT_HIP, LEFT_KNEE, LEFT_ANKLE]):
            angles['left_knee'] = calculate_angle(
                landmarks[str(LEFT_HIP)],
                landmarks[str(LEFT_KNEE)],
                landmarks[str(LEFT_ANKLE)]
            )
        
        if all(str(i) in landmarks for i in [RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE]):
            angles['right_knee'] = calculate_angle(
                landmarks[str(RIGHT_HIP)],
                landmarks[str(RIGHT_KNEE)],
                landmarks[str(RIGHT_ANKLE)]
            )
        
        # 股関節角度の計算
        if all(str(i) in landmarks for i in [LEFT_SHOULDER, LEFT_HIP, LEFT_KNEE]):
            angles['left_hip'] = calculate_angle(
                landmarks[str(LEFT_SHOULDER)],
                landmarks[str(LEFT_HIP)],
                landmarks[str(LEFT_KNEE)]
            )
        
        if all(str(i) in landmarks for i in [RIGHT_SHOULDER, RIGHT_HIP, RIGHT_KNEE]):
            angles['right_hip'] = calculate_angle(
                landmarks[str(RIGHT_SHOULDER)],
                landmarks[str(RIGHT_HIP)],
                landmarks[str(RIGHT_KNEE)]
            )
        
        # 肘角度の計算（ベンチプレス用）
        if exercise_type == 'bench_press':
            if all(str(i) in landmarks for i in [LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST]):
                angles['left_elbow'] = calculate_angle(
                    landmarks[str(LEFT_SHOULDER)],
                    landmarks[str(LEFT_ELBOW)],
                    landmarks[str(LEFT_WRIST)]
                )
            
            if all(str(i) in landmarks for i in [RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST]):
                angles['right_elbow'] = calculate_angle(
                    landmarks[str(RIGHT_SHOULDER)],
                    landmarks[str(RIGHT_ELBOW)],
                    landmarks[str(RIGHT_WRIST)]
                )
        
        # 背中の傾き計算
        if all(str(i) in landmarks for i in [LEFT_SHOULDER, LEFT_HIP]):
            back_angle = calculate_back_angle(
                landmarks[str(LEFT_SHOULDER)],
                landmarks[str(LEFT_HIP)]
            )
            angles['back_angle'] = back_angle
        
        # フォーム評価
        form_score = evaluate_form(angles, exercise_type)
        
        # フィードバック生成
        feedback = generate_feedback(angles, exercise_type)
        
        # 結果を返す
        result = {
            'success': True,
            'frame_number': frame_number,
            'exercise_type': exercise_type,
            'angles': angles,
            'form_score': form_score,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"ポーズ分析エラー: {e}")
        return jsonify({'error': str(e)}), 500

def calculate_angle(point1, point2, point3):
    """3点から角度を計算"""
    import numpy as np
    
    # ベクトルを計算
    a = np.array([point1['x'], point1['y']])
    b = np.array([point2['x'], point2['y']])
    c = np.array([point3['x'], point3['y']])
    
    ba = a - b
    bc = c - b
    
    # 角度を計算
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)

def calculate_back_angle(shoulder, hip):
    """背中の傾きを計算"""
    import numpy as np
    
    # 垂直線からの角度を計算
    dx = hip['x'] - shoulder['x']
    dy = hip['y'] - shoulder['y']
    
    angle = np.degrees(np.arctan2(dx, dy))
    return abs(angle)

def evaluate_form(angles, exercise_type):
    """フォームスコアを評価"""
    score = 100
    
    if exercise_type == 'squat':
        # スクワットの評価基準
        if 'left_knee' in angles and 'right_knee' in angles:
            avg_knee_angle = (angles['left_knee'] + angles['right_knee']) / 2
            
            # 理想的な膝角度は90度
            if avg_knee_angle < 80:
                score -= 20  # 深すぎる
            elif avg_knee_angle > 100:
                score -= 15  # 浅すぎる
        
        # 背中の傾き評価
        if 'back_angle' in angles:
            if angles['back_angle'] > 45:
                score -= 15  # 前傾しすぎ
    
    elif exercise_type == 'bench_press':
        # ベンチプレスの評価基準
        if 'left_elbow' in angles and 'right_elbow' in angles:
            avg_elbow_angle = (angles['left_elbow'] + angles['right_elbow']) / 2
            
            # 理想的な肘角度は90度
            if avg_elbow_angle < 70:
                score -= 15  # 深すぎる
            elif avg_elbow_angle > 110:
                score -= 10  # 浅すぎる
    
    elif exercise_type == 'deadlift':
        # デッドリフトの評価基準
        if 'back_angle' in angles:
            if angles['back_angle'] > 60:
                score -= 20  # 背中が丸まりすぎ
        
        if 'left_hip' in angles and 'right_hip' in angles:
            avg_hip_angle = (angles['left_hip'] + angles['right_hip']) / 2
            if avg_hip_angle < 90:
                score -= 10  # 股関節が開きすぎ
    
    return max(0, score)

def generate_feedback(angles, exercise_type):
    """フィードバックメッセージを生成"""
    feedback = []
    
    if exercise_type == 'squat':
        if 'left_knee' in angles and 'right_knee' in angles:
            avg_knee_angle = (angles['left_knee'] + angles['right_knee']) / 2
            
            if avg_knee_angle < 80:
                feedback.append("膝が深く曲がりすぎています。股関節の柔軟性を確認してください。")
            elif avg_knee_angle > 100:
                feedback.append("もう少し深くしゃがみましょう。太ももが床と平行になるまで下げます。")
        
        if 'back_angle' in angles and angles['back_angle'] > 45:
            feedback.append("上体が前傾しすぎています。胸を張って背筋を伸ばしましょう。")
    
    elif exercise_type == 'bench_press':
        if 'left_elbow' in angles and 'right_elbow' in angles:
            avg_elbow_angle = (angles['left_elbow'] + angles['right_elbow']) / 2
            
            if avg_elbow_angle < 70:
                feedback.append("バーを下げすぎています。肘は90度程度で止めましょう。")
            elif avg_elbow_angle > 110:
                feedback.append("可動域が狭いです。もう少しバーを下げましょう。")
    
    elif exercise_type == 'deadlift':
        if 'back_angle' in angles and angles['back_angle'] > 60:
            feedback.append("背中が丸まっています。胸を張って背筋を伸ばしましょう。")
    
    if not feedback:
        feedback.append("良いフォームです！この調子で続けましょう。")
    
    return feedback

# ===== 認証機能 =====

def get_current_user():
    """現在ログイン中のユーザーを取得"""
    session_token = session.get('session_token')
    if session_token:
        return auth_manager.get_user_from_session(session_token)
    return None

@app.route('/api/auth/register', methods=['POST'])
def register():
    """ユーザー登録"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # 入力検証
        if not email or not password:
            return jsonify({'error': 'メールアドレスとパスワードは必須です'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'パスワードは6文字以上である必要があります'}), 400
        
        # ユーザー作成
        result = auth_manager.create_user(email, password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'アカウントが作成されました。メール認証は省略して直接ログインできます。'
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"登録エラー: {e}")
        return jsonify({'error': 'アカウント作成に失敗しました'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """ユーザーログイン"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # メール認証をスキップして直接認証
        result = auth_manager.authenticate_user_simple(email, password)
        
        if result['success']:
            # セッション作成
            session_token = auth_manager.create_session(result['user']['id'])
            if session_token:
                session['session_token'] = session_token
                session['user_email'] = result['user']['email']
                session.permanent = True
                
                return jsonify({
                    'success': True,
                    'message': 'ログインしました',
                    'user': result['user']
                })
            else:
                return jsonify({'error': 'セッション作成に失敗しました'}), 500
        else:
            return jsonify({'error': result['error']}), 401
            
    except Exception as e:
        logger.error(f"ログインエラー: {e}")
        return jsonify({'error': 'ログインに失敗しました'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """ログアウト"""
    try:
        session_token = session.get('session_token')
        if session_token:
            auth_manager.delete_session(session_token)
        
        session.clear()
        return jsonify({'success': True, 'message': 'ログアウトしました'})
        
    except Exception as e:
        logger.error(f"ログアウトエラー: {e}")
        return jsonify({'error': 'ログアウトに失敗しました'}), 500

@app.route('/api/auth/user', methods=['GET'])
def get_user_info():
    """現在のユーザー情報を取得"""
    try:
        user = get_current_user()
        if user:
            return jsonify({'user': user})
        else:
            return jsonify({'user': None})
            
    except Exception as e:
        logger.error(f"ユーザー情報取得エラー: {e}")
        return jsonify({'error': 'ユーザー情報の取得に失敗しました'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
