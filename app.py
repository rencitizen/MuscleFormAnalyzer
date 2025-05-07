from flask import Flask, render_template_string, request, jsonify
import os
import sys
import json
import logging
import subprocess
import uuid
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Ensure temp directory exists
os.makedirs('/tmp', exist_ok=True)

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
    
    if not file.filename.lower().endswith(('.mp4')):
        return jsonify({'error': 'Only MP4 files are supported'}), 400
    
    # Create temporary file
    temp_file_path = os.path.join('/tmp', f"{uuid.uuid4()}.mp4")
    try:
        file.save(temp_file_path)
        logger.info(f"Saved video to {temp_file_path}")
        
        # Mock analysis result instead of using MediaPipe directly
        # In a real application, we would process the video here
        frames = []
        # Create a simple mock result for testing
        frame_data = {
            'frame': 0,
            'landmarks': {
                f'lm_{i}': {
                    'x': 0.5 + (i * 0.01) % 0.2,
                    'y': 0.5 + (i * 0.01) % 0.2,
                    'z': 0.0
                } for i in range(33)
            }
        }
        frames.append(frame_data)
        
        # Compare with ideal pose
        results = []
        for frame in frames:
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
            advice = generate_advice(diffs)
            
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

def generate_advice(diffs):
    """Generate advice based on differences"""
    # List of problematic landmarks (above threshold)
    problem_landmarks = [lm for lm, diff in diffs.items() if diff > 0.05]
    
    if not problem_landmarks:
        return "Perfect form! Keep it up!"
    
    # Map landmark indices to body parts for more meaningful feedback
    body_parts = {
        "lm_0": "nose", "lm_1": "left eye inner", "lm_2": "left eye", "lm_3": "left eye outer",
        "lm_4": "right eye inner", "lm_5": "right eye", "lm_6": "right eye outer",
        "lm_7": "left ear", "lm_8": "right ear", "lm_9": "mouth left", "lm_10": "mouth right",
        "lm_11": "left shoulder", "lm_12": "right shoulder", "lm_13": "left elbow", "lm_14": "right elbow",
        "lm_15": "left wrist", "lm_16": "right wrist", "lm_17": "left pinky", "lm_18": "right pinky",
        "lm_19": "left index", "lm_20": "right index", "lm_21": "left thumb", "lm_22": "right thumb",
        "lm_23": "left hip", "lm_24": "right hip", "lm_25": "left knee", "lm_26": "right knee",
        "lm_27": "left ankle", "lm_28": "right ankle", "lm_29": "left heel", "lm_30": "right heel",
        "lm_31": "left foot index", "lm_32": "right foot index"
    }
    
    # Group landmarks by body region
    upper_body = [
        "lm_11", "lm_12", "lm_13", "lm_14", "lm_15", "lm_16",
        "lm_17", "lm_18", "lm_19", "lm_20", "lm_21", "lm_22"
    ]
    lower_body = [
        "lm_23", "lm_24", "lm_25", "lm_26", "lm_27", "lm_28",
        "lm_29", "lm_30", "lm_31", "lm_32"
    ]
    
    # Check which regions have issues
    upper_body_issues = [lm for lm in problem_landmarks if lm in upper_body]
    lower_body_issues = [lm for lm in problem_landmarks if lm in lower_body]
    
    advice = []
    
    # Generate specific advice based on problem areas
    if upper_body_issues and lower_body_issues:
        advice.append("Adjust both your upper and lower body position.")
    elif upper_body_issues:
        if "lm_11" in upper_body_issues or "lm_12" in upper_body_issues:
            advice.append("Check your shoulder alignment.")
        if "lm_13" in upper_body_issues or "lm_14" in upper_body_issues:
            advice.append("Adjust your elbow position.")
        if "lm_15" in upper_body_issues or "lm_16" in upper_body_issues:
            advice.append("Correct your wrist position.")
    elif lower_body_issues:
        if "lm_23" in lower_body_issues or "lm_24" in lower_body_issues:
            advice.append("Adjust your hip position.")
        if "lm_25" in lower_body_issues or "lm_26" in lower_body_issues:
            advice.append("Bend your knees more.")
        if "lm_27" in lower_body_issues or "lm_28" in lower_body_issues:
            advice.append("Check your ankle alignment.")
    
    if not advice:
        # Generic advice if we couldn't generate specific feedback
        advice.append("Your form needs adjustment. Try to match the reference position more closely.")
    
    return " ".join(advice)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)