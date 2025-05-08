from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sys
import json
import logging
import uuid
import math
import time
import datetime
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Ensure temp directory exists
os.makedirs('/tmp', exist_ok=True)

# Ensure static video directory exists
os.makedirs('static/videos', exist_ok=True)

# Load ideal pose data
try:
    with open("ideal_pose.json", "r") as f:
        IDEAL_POSE = json.load(f)
    logger.info("Ideal pose loaded successfully")
except FileNotFoundError:
    logger.warning("ideal_pose.json not found, creating default")
    # Create a default ideal pose (will be overwritten if file is provided)
    IDEAL_POSE = {"frame": 0, "landmarks": {f"lm_{i}": {"x": 0, "y": 0, "z": 0} for i in range(33)}}
    # Save it to file
    with open("ideal_pose.json", "w") as f:
        json.dump(IDEAL_POSE, f, indent=2)

@app.route('/')
def index():
    """Home page with video upload form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process video upload and simulate analysis"""
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if not file.filename.lower().endswith(('.mp4')):
        return jsonify({'error': 'Only MP4 files are supported'}), 400
    
    # Get exercise type
    exercise_type = request.form.get('exercise_type', 'squat')
    
    # Create temporary file
    temp_file_path = os.path.join('/tmp', f"{uuid.uuid4()}.mp4")
    output_path = os.path.join('static/videos', f"processed_{uuid.uuid4()}.mp4")
    
    try:
        file.save(temp_file_path)
        logger.info(f"Saved video to {temp_file_path}")
        
        # For demonstration purposes, we'll simulate video analysis
        # In a real application, we would use MediaPipe to analyze the video here
        time.sleep(2)  # Simulate processing time
        
        # Copy the file to static directory for playback
        # In a real app, we might create a processed version with overlay
        import shutil
        shutil.copy(temp_file_path, output_path)
        
        # Redirect to results page
        return redirect(url_for('results', video=os.path.basename(output_path), exercise=exercise_type))
    
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        return jsonify({'error': f"Error analyzing video: {str(e)}"}), 500
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def generate_exercise_feedback(exercise_type, score):
    """種目ごとのフィードバックを生成する"""
    feedback = {
        'score': score,
        'assessment': "",
        'overall_feedback': "",
        'specific_feedback': [],
        'improvement_tips': []
    }
    
    # 点数に基づいて全体評価を決定（日本語）
    if score >= 85:
        feedback['assessment'] = "素晴らしいフォーム！"
        feedback['overall_feedback'] = "フォームは優れています！動作のほとんどで適切な技術を維持しています。"
    elif score >= 70:
        feedback['assessment'] = "改善の余地があるフォーム"
        feedback['overall_feedback'] = "全体的には良好ですが、いくつかの注意が必要な点があります。"
    else:
        feedback['assessment'] = "フォームの改善が必要"
        feedback['overall_feedback'] = "いくつかの重要な点でフォームの改善が必要です。以下の推奨事項に注目してください。"
    
    # 種目ごとの具体的なフィードバック
    if exercise_type == 'squat':
        feedback['specific_feedback'] = [
            "膝とつま先の位置が適切です" if score > 75 else "膝がつま先より前に出ています",
            "腰の位置が安定しています" if score > 80 else "スクワット中に腰が丸まっています",
            "深さが適切です" if score > 70 else "スクワットの深さが不十分です"
        ]
        feedback['improvement_tips'] = [
            "スクワット中は背筋をまっすぐに保ちましょう",
            "膝がつま先と同じ方向を向くようにしましょう",
            "かかとに体重をかけるようにしましょう"
        ]
    elif exercise_type == 'bench':
        feedback['specific_feedback'] = [
            "バーのパスが適切です" if score > 75 else "バーが胸の上で安定していません",
            "肘の角度が適切です" if score > 80 else "肘の角度が広すぎます",
            "肩の安定性は良好です" if score > 70 else "肩甲骨が固定できていません"
        ]
        feedback['improvement_tips'] = [
            "バーは胸の下部（乳頭の少し下）にタッチさせましょう",
            "肩甲骨をベンチに固定して安定させましょう",
            "肘を体に45度以内に保ちましょう"
        ]
    elif exercise_type == 'deadlift':
        feedback['specific_feedback'] = [
            "背中の角度が適切です" if score > 75 else "リフト中に背中が丸まっています",
            "バーのパスが効率的です" if score > 80 else "バーがシンからの距離が遠すぎます",
            "股関節のヒンジが効果的です" if score > 70 else "股関節の動きが不十分です"
        ]
        feedback['improvement_tips'] = [
            "バーはシン（すね）に近い位置に保ちましょう",
            "持ち上げる前に背中の緊張を作りましょう",
            "股関節をヒンジのように使い、リフト時に臀部を後ろに引きましょう"
        ]
    else:
        # デフォルトのフィードバック
        feedback['specific_feedback'] = [
            "姿勢の安定性は良好です" if score > 75 else "姿勢が不安定です",
            "動作の一貫性があります" if score > 80 else "動作にばらつきがあります",
            "フォームのバランスが取れています" if score > 70 else "バランスが悪いです"
        ]
        feedback['improvement_tips'] = [
            "動作を安定させるためにコア（体幹）を常に締めましょう",
            "呼吸を意識して、力を入れるタイミングで息を止めましょう",
            "動作のテンポを一定に保ちましょう"
        ]
    
    return feedback

@app.route('/results')
def results():
    """Display analysis results"""
    video_filename = request.args.get('video', '')
    exercise_type = request.args.get('exercise', 'squat')
    
    # シミュレートされたスコアを生成
    overall_score = random.randint(60, 95)
    
    # 種目に基づいたフィードバックを生成
    feedback = generate_exercise_feedback(exercise_type, overall_score)
    
    return render_template(
        'results.html',
        video_filename=video_filename,
        exercise_type=exercise_type,
        overall_score=overall_score,
        overall_assessment=feedback['assessment'],
        overall_feedback=feedback['overall_feedback'],
        specific_feedback=feedback['specific_feedback'],
        improvement_tips=feedback['improvement_tips']
    )

# API endpoint for getting pose data (would be used by the frontend)
@app.route('/api/pose_data')
def pose_data():
    """Return pose data for a given video frame"""
    video_id = request.args.get('video_id', '')
    frame = int(request.args.get('frame', 0))
    
    # In a real app, this would retrieve actual pose data from a database
    # Here we're generating simulated data
    
    # Use frame number to seed the random generation for consistent results
    random.seed(frame)
    
    # Generate simulated pose data for this frame
    landmarks = {}
    for i in range(33):
        landmarks[f"lm_{i}"] = {
            "x": random.uniform(0.1, 0.9),
            "y": random.uniform(0.1, 0.9),
            "z": random.uniform(-0.1, 0.1),
            "visibility": random.uniform(0.7, 1.0)
        }
    
    # Generate some issues for demonstration
    if frame > 15 and frame < 20:
        # Knee issue
        landmarks["lm_25"]["y"] += 0.1  # Left knee too high
        landmarks["lm_26"]["y"] += 0.1  # Right knee too high
    
    if frame > 45 and frame < 50:
        # Hip issue
        landmarks["lm_23"]["y"] -= 0.05  # Left hip too high
        landmarks["lm_24"]["y"] -= 0.05  # Right hip too high
    
    return jsonify({
        "frame": frame,
        "landmarks": landmarks,
        "has_issues": (frame > 15 and frame < 20) or (frame > 45 and frame < 50) or (frame > 75 and frame < 80)
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)