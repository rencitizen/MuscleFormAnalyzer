from flask import Flask, render_template_string, jsonify, request
import os
import sys
import json
import math
import logging
import uuid
import tempfile
import shutil
import subprocess
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables to force CPU usage for MediaPipe
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Create Flask app
app = Flask(__name__)

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
    """Simple frontend for the API"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Muscle-Form Analyzer MVP</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            body {
                padding: 20px;
            }
            .container {
                max-width: 800px;
            }
            .mt-5 {
                margin-top: 3rem;
            }
            .mb-4 {
                margin-bottom: 1.5rem;
            }
        </style>
    </head>
    <body data-bs-theme="dark">
        <div class="container">
            <h1 class="mt-5 mb-4">Muscle-Form Analyzer MVP</h1>
            <p class="lead">Upload a workout video to analyze your exercise form.</p>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">How It Works</h5>
                </div>
                <div class="card-body">
                    <ol>
                        <li>Upload an MP4 video (max 150MB) of your workout</li>
                        <li>Our system extracts pose landmarks using MediaPipe</li>
                        <li>Your form is compared with an ideal reference pose</li>
                        <li>Get detailed feedback on your exercise technique</li>
                    </ol>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Upload Video</h5>
                </div>
                <div class="card-body">
                    <form id="uploadForm" action="/analyze" method="post" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="videoFile" class="form-label">Select a video file (MP4 format, max 150MB)</label>
                            <input class="form-control" type="file" id="videoFile" name="file" accept="video/mp4">
                        </div>
                        <button type="submit" class="btn btn-success">Analyze Form</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process video upload and analyze form"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file.filename.lower().endswith('.mp4'):
        return jsonify({'error': 'Only MP4 files are supported'}), 400
    
    # Create temporary file
    temp_file_path = os.path.join('/tmp', f"{uuid.uuid4()}.mp4")
    try:
        file.save(temp_file_path)
        
        # Run the analysis as a subprocess to isolate MediaPipe
        cmd = [
            sys.executable, "-c",
            "import os; os.environ['CUDA_VISIBLE_DEVICES']='-1'; "
            "os.environ['MEDIAPIPE_DISABLE_GPU']='1'; "
            "import cv2, mediapipe as mp, json; "
            "mp_pose = mp.solutions.pose; "
            "pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, "
            "min_detection_confidence=0.5, min_tracking_confidence=0.5); "
            f"cap = cv2.VideoCapture('{temp_file_path}'); "
            "frames = []; frame_idx = 0; "
            "while cap.isOpened(): "
            "    success, image = cap.read(); "
            "    if not success: break; "
            "    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB); "
            "    results = pose.process(image_rgb); "
            "    if results.pose_landmarks: "
            "        landmarks_dict = {}; "
            "        for i, landmark in enumerate(results.pose_landmarks.landmark): "
            "            landmarks_dict[f'lm_{i}'] = {'x': landmark.x, 'y': landmark.y, 'z': landmark.z}; "
            "        frames.append({'frame': frame_idx, 'landmarks': landmarks_dict}); "
            "    frame_idx += 1; "
            "cap.release(); "
            f"with open('/tmp/results.json', 'w') as f: json.dump(frames, f); "
        ]
        
        subprocess.run(cmd, check=True)
        
        # Load the results
        with open('/tmp/results.json', 'r') as f:
            frames = json.load(f)
        
        # Compare with ideal pose
        results = []
        for frame in frames:
            # Simple mock comparison for now - we'll expand this
            is_ok = True
            diffs = {}
            
            # Compare with ideal pose
            for lm_key, lm_value in frame['landmarks'].items():
                if lm_key in IDEAL_POSE["landmarks"]:
                    # Calculate distance
                    diff = math.sqrt(
                        (lm_value["x"] - IDEAL_POSE["landmarks"][lm_key]["x"]) ** 2 +
                        (lm_value["y"] - IDEAL_POSE["landmarks"][lm_key]["y"]) ** 2 +
                        (lm_value["z"] - IDEAL_POSE["landmarks"][lm_key]["z"]) ** 2
                    )
                    diffs[lm_key] = diff
                    
                    # Check if distance is above threshold
                    if diff > 0.05:  # Using 0.05 as threshold
                        is_ok = False
            
            # Generate basic advice
            if is_ok:
                advice = "Perfect form! Keep it up!"
            else:
                advice = "Your form needs adjustment. Try to match the reference position more closely."
            
            results.append({
                'frame': frame['frame'],
                'diffs': diffs,
                'is_ok': is_ok,
                'advice': advice
            })
        
        # Render results page
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analysis Results - Muscle-Form Analyzer MVP</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body {
                    padding: 20px;
                }
                .container {
                    max-width: 800px;
                }
                .mt-5 {
                    margin-top: 3rem;
                }
                .mb-4 {
                    margin-bottom: 1.5rem;
                }
            </style>
        </head>
        <body data-bs-theme="dark">
            <div class="container">
                <h1 class="mt-5 mb-4">Form Analysis Results</h1>
                
                <a href="/" class="btn btn-secondary mb-4">Analyze Another Video</a>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Overall Form Assessment</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert {{ 'alert-success' if results[0]['is_ok'] else 'alert-danger' }}">
                            <strong>{{ 'Good Form!' if results[0]['is_ok'] else 'Form Needs Improvement' }}</strong>
                            <p>{{ results[0]['advice'] }}</p>
                        </div>
                    </div>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Detailed Analysis</h5>
                    </div>
                    <div class="card-body">
                        <p>Frame: {{ results[0]['frame'] }}</p>
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Body Part</th>
                                    <th>Difference Score</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for body_part, score in results[0]['diffs'].items() %}
                                <tr>
                                    <td>{{ body_part.replace('_', ' ') }}</td>
                                    <td>{{ "%.4f"|format(score) }}</td>
                                    <td>
                                        <span class="badge {{ 'bg-success' if score < 0.05 else 'bg-danger' }}">
                                            {{ 'Good' if score < 0.05 else 'Needs Adjustment' }}
                                        </span>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return render_template_string(
            html, 
            results=results
        )
    
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        return jsonify({'error': f"Error analyzing video: {str(e)}"}), 500
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if os.path.exists('/tmp/results.json'):
            os.remove('/tmp/results.json')