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
SAMPLE_TRAINING_PATH = 'results/sample_training.json'
SAMPLE_EXERCISE_PATH = 'results/sample_exercises.json'

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
        # サンプルデータファイルが存在するか確認
        if not os.path.exists(SAMPLE_METRICS_PATH):
            # なければ作成する
            sample_data = {
                "user_height_cm": 170,
                "left_arm_cm": 62.5,
                "right_arm_cm": 62.8,
                "left_leg_cm": 91.2,
                "right_leg_cm": 91.5,
                "shoulder_width_cm": 42.3,
                "chest_width_cm": 38.6,
                "hip_width_cm": 36.2,
                "torso_length_cm": 51.4,
                "analysis_date": "2025-05-15",
                "joints_cm": {
                    "leftShoulder": {"x": 42.3, "y": 120.5, "z": 0.0},
                    "rightShoulder": {"x": 0.0, "y": 120.5, "z": 0.0},
                    "leftElbow": {"x": 62.5, "y": 95.2, "z": 5.1},
                    "rightElbow": {"x": -20.2, "y": 95.2, "z": 5.1},
                    "leftWrist": {"x": 70.8, "y": 80.3, "z": 10.2},
                    "rightWrist": {"x": -28.5, "y": 80.3, "z": 10.2},
                    "leftHip": {"x": 33.1, "y": 80.5, "z": 0.0},
                    "rightHip": {"x": 9.2, "y": 80.5, "z": 0.0},
                    "leftKnee": {"x": 35.5, "y": 45.2, "z": 7.3},
                    "rightKnee": {"x": 6.8, "y": 45.2, "z": 7.3},
                    "leftAnkle": {"x": 38.2, "y": 10.5, "z": 12.5},
                    "rightAnkle": {"x": 4.1, "y": 10.5, "z": 12.5}
                }
            }
            os.makedirs(os.path.dirname(SAMPLE_METRICS_PATH), exist_ok=True)
            with open(SAMPLE_METRICS_PATH, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2)
            return sample_data
        
        # 存在する場合はファイルから読み込む
        with open(SAMPLE_METRICS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"サンプルデータの読み込みに失敗: {e}")
        return None
        
def load_training_sample():
    """トレーニング分析のサンプルデータを読み込む"""
    try:
        # サンプルデータファイルが存在するか確認
        if not os.path.exists(SAMPLE_TRAINING_PATH):
            # なければ作成する
            sample_data = {
                "exercise_type": "squat",
                "user_height_cm": 170,
                "repetitions": 8,
                "form_score": 85,
                "depth_score": 88,
                "max_depth": 82.5,
                "asymmetry_index": 3.2,
                "joint_angles": {
                    "left_knee": {
                        "min": 75.2,
                        "max": 178.3,
                        "range": 103.1
                    },
                    "right_knee": {
                        "min": 72.8,
                        "max": 177.9,
                        "range": 105.1
                    },
                    "left_hip": {
                        "min": 65.4,
                        "max": 172.1,
                        "range": 106.7
                    },
                    "right_hip": {
                        "min": 66.2,
                        "max": 171.8,
                        "range": 105.6
                    }
                },
                "body_metrics": {
                    "left_arm_cm": 62.5,
                    "right_arm_cm": 62.8,
                    "left_leg_cm": 91.2,
                    "right_leg_cm": 91.5,
                    "height_cm": 170,
                    "arm_length_ratio": 0.369,
                    "leg_length_ratio": 0.537
                },
                "leg_length_analysis": {
                    "form_adjustment": "脚の長さに合わせたスタンス幅を調整してください。",
                    "depth_advice": "膝と足首の動きを連動させて効率的な動作を心がけましょう。",
                    "symmetry_issue": None
                },
                "arm_length_analysis": {
                    "grip_width": "肩幅よりやや広めのグリップ幅が最適です。",
                    "rom_advice": "肘を適切に曲げて、可動域を最大限に活用しましょう。",
                    "symmetry_issue": None
                },
                "chest_width_impact": "胸の幅が標準的なため、通常のフォームで問題ありません。",
                "body_proportion_insights": [
                    "腕長と脚長のバランスが良好です。",
                    "全身の可動域を最大化するために、柔軟性トレーニングを取り入れると効果的です。",
                    "姿勢を意識して、関節の動きを適切にコントロールしましょう。"
                ],
                "analysis_date": "2025-05-15"
            }
            os.makedirs(os.path.dirname(SAMPLE_TRAINING_PATH), exist_ok=True)
            with open(SAMPLE_TRAINING_PATH, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2)
            return sample_data
        
        # 存在する場合はファイルから読み込む
        with open(SAMPLE_TRAINING_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"トレーニング分析サンプルデータの読み込みに失敗: {e}")
        return None

def load_exercise_classification_sample():
    """運動分類のサンプルデータを読み込む"""
    try:
        # サンプルデータファイルが存在するか確認
        if not os.path.exists(SAMPLE_EXERCISE_PATH):
            # なければ作成する
            sample_data = {
                "dominant_exercise": "squat",
                "confidence_score": 85,
                "exercise_distribution": {
                    "squat": 75,
                    "deadlift": 15,
                    "lunge": 8,
                    "unknown": 2
                },
                "total_frames": 300,
                "segments": [
                    {
                        "start_frame": 0,
                        "end_frame": 30,
                        "exercise": "unknown",
                        "confidence": 45
                    },
                    {
                        "start_frame": 31,
                        "end_frame": 120,
                        "exercise": "squat",
                        "confidence": 88,
                        "repetitions": 3
                    },
                    {
                        "start_frame": 121,
                        "end_frame": 150,
                        "exercise": "rest",
                        "confidence": 92
                    },
                    {
                        "start_frame": 151,
                        "end_frame": 240,
                        "exercise": "squat",
                        "confidence": 90,
                        "repetitions": 3
                    },
                    {
                        "start_frame": 241,
                        "end_frame": 270,
                        "exercise": "deadlift",
                        "confidence": 75,
                        "repetitions": 2
                    },
                    {
                        "start_frame": 271,
                        "end_frame": 300,
                        "exercise": "unknown",
                        "confidence": 40
                    }
                ],
                "performance_metrics": {
                    "squat": {
                        "joint_rom": {
                            "left_knee": 105.2,
                            "right_knee": 104.8,
                            "left_hip": 110.3,
                            "right_hip": 109.7
                        },
                        "movement_speed": {
                            "average": 0.85,
                            "max": 1.2,
                            "consistency": 0.92
                        },
                        "form_score": 82
                    },
                    "deadlift": {
                        "joint_rom": {
                            "left_knee": 75.3,
                            "right_knee": 74.9,
                            "left_hip": 95.2,
                            "right_hip": 94.6,
                            "left_shoulder": 45.2,
                            "right_shoulder": 44.8
                        },
                        "movement_speed": {
                            "average": 0.72,
                            "max": 0.95,
                            "consistency": 0.88
                        },
                        "form_score": 78
                    }
                },
                "analysis_date": "2025-05-15"
            }
            os.makedirs(os.path.dirname(SAMPLE_EXERCISE_PATH), exist_ok=True)
            with open(SAMPLE_EXERCISE_PATH, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2)
            return sample_data
        
        # 存在する場合はファイルから読み込む
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
    
    # 身体プロポーションに基づく分析を追加
    exercise_type = training_data.get('exercise_type', 'squat')
    
    # 脚の長さに基づく分析
    training_data['leg_length_analysis'] = {
        'form_adjustment': '脚の長さに合わせたスタンス幅を調整してください。',
        'depth_advice': '膝と足首の動きを連動させて効率的な動作を心がけましょう。',
        'symmetry_issue': None
    }
    
    # 腕の長さに基づく分析
    training_data['arm_length_analysis'] = {
        'grip_width': '肩幅よりやや広めのグリップ幅が最適です。',
        'rom_advice': '肘を適切に曲げて、可動域を最大限に活用しましょう。',
        'symmetry_issue': None
    }
    
    # 胸幅の影響
    training_data['chest_width_impact'] = '胸の幅が標準的なため、通常のフォームで問題ありません。'
    
    # 体型プロポーションの洞察
    training_data['body_proportion_insights'] = [
        '腕長と脚長のバランスが良好です。',
        '全身の可動域を最大化するために、柔軟性トレーニングを取り入れると効果的です。',
        '姿勢を意識して、関節の動きを適切にコントロールしましょう。'
    ]
    
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
        # サマリーデータを作成
        if classification_data:
            classification_summary = {
                "dominant_exercise": classification_data.get("dominant_exercise", "squat"),
                "confidence": classification_data.get("confidence_score", 85) / 100,
                "class_distribution": classification_data.get("exercise_distribution", {"squat": 75, "rest": 15, "unknown": 10}),
                "frame_count": classification_data.get("total_frames", 300),
                "processing_time": 2.5
            }
        else:
            classification_summary = {
                "dominant_exercise": "squat",
                "confidence": 0.85,
                "class_distribution": {"squat": 75, "rest": 15, "unknown": 10},
                "frame_count": 300,
                "processing_time": 2.5
            }
    
    # 既に条件チェック済みなので削除
    
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