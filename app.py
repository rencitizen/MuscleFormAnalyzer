from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, flash, session, make_response
import os
import json
import uuid
import logging
import shutil
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from training_analysis import TrainingAnalyzer
from exercise_classifier import ExerciseClassifier
from workout_models import workout_db
from exercise_database import (
    EXERCISE_DATABASE, get_all_exercises, search_exercises, 
    get_exercises_by_category, get_exercise_by_id, COMMON_WEIGHTS, get_weight_suggestions
)
from auth_models import auth_manager

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
            
            # まず身体寸法を測定
            from analysis import BodyAnalyzer
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
            from analysis import BodyAnalyzer
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
        required_fields = ['date', 'exercise', 'weight', 'reps', 'sets']
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
            sets=int(data['sets']),
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

@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    """ワークアウト記録を取得するAPI"""
    try:
        user_id = session.get('user_email', 'default_user')
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

@app.route('/api/workouts/<int:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    """ワークアウト記録を削除するAPI"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        
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

@app.route('/api/progress/<exercise>')
def get_progress(exercise):
    """特定種目の進捗データを取得するAPI"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        
        progress_data = workout_db.get_exercise_progress(user_id, exercise)
        
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

@app.route('/api/charts/progress/<exercise>')
def get_chart_progress(exercise):
    """グラフ用の進捗データを取得"""
    try:
        user_id = session.get('user_email', 'default_user')
        chart_data = workout_db.get_chart_progress_data(user_id, exercise)
        return jsonify(chart_data)
    except Exception as e:
        logger.error(f"グラフデータ取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/calendar')
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

# ===== 設定管理API =====

@app.route('/settings')
def settings_page():
    """設定ページ"""
    return render_template('settings.html')

@app.route('/api/language', methods=['POST'])
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

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """設定情報を取得"""
    try:
        user_id = session.get('user_email', 'default_user')
        settings = workout_db.get_user_settings(user_id)
        return jsonify(settings)
    except Exception as e:
        logger.error(f"設定取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/personal', methods=['POST'])
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
def logout():
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
