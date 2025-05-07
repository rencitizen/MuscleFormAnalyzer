from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import os
import sys
import json
import logging
import uuid
import math
import time
import datetime

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
    """Simple frontend for the demo app"""
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
            
            <div class="alert alert-info">
                <strong>Note:</strong> This is a demonstration version. In a production environment, 
                video analysis would be performed using MediaPipe pose estimation.
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">How It Works</h5>
                </div>
                <div class="card-body">
                    <ol>
                        <li>Upload an MP4 video (max 150MB) of your workout</li>
                        <li>Our system extracts pose landmarks using computer vision</li>
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
                    <form action="/analyze" method="post" enctype="multipart/form-data">
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
        
        # For demonstration purposes, we'll simulate video analysis
        # In a real application, we would use MediaPipe to analyze the video here
        time.sleep(2)  # Simulate processing time
        
        # Generate sample results
        results = generate_sample_results(file.filename)
        
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
                
                <div class="alert alert-info mb-4">
                    <strong>Note:</strong> These results are simulated for demonstration purposes.
                    In a production environment, actual video analysis would be performed.
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Video Information</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Filename:</strong> {{ filename }}</p>
                        <p><strong>Analysis Date:</strong> {{ date }}</p>
                    </div>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Overall Form Assessment</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert {{ 'alert-success' if result['is_ok'] else 'alert-danger' }}">
                            <strong>{{ 'Good Form!' if result['is_ok'] else 'Form Needs Improvement' }}</strong>
                            <p>{{ result['advice'] }}</p>
                        </div>
                    </div>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Detailed Analysis</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Body Part</th>
                                    <th>Difference Score</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for body_part, score in result['diffs'].items() %}
                                <tr>
                                    <td>{{ body_parts.get(body_part, body_part) }}</td>
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
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Next Steps</h5>
                    </div>
                    <div class="card-body">
                        <p>Based on your analysis, here are some suggested improvements:</p>
                        <ul>
                            {% if not result['is_ok'] %}
                                {% if has_upper_issues %}
                                <li>Focus on improving your upper body alignment</li>
                                {% endif %}
                                {% if has_lower_issues %}
                                <li>Work on your lower body positioning</li>
                                {% endif %}
                                <li>Practice with a mirror to improve your form</li>
                                <li>Consider recording your workouts regularly to track progress</li>
                            {% else %}
                                <li>Continue with your current form</li>
                                <li>Gradually increase intensity while maintaining good form</li>
                                <li>Consider adding more advanced variations to your routine</li>
                            {% endif %}
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Determine if there are upper or lower body issues
        upper_body = ["lm_11", "lm_12", "lm_13", "lm_14", "lm_15", "lm_16"]
        lower_body = ["lm_23", "lm_24", "lm_25", "lm_26", "lm_27", "lm_28"]
        
        has_upper_issues = any(results['diffs'].get(lm, 0) > 0.05 for lm in upper_body)
        has_lower_issues = any(results['diffs'].get(lm, 0) > 0.05 for lm in lower_body)
        
        # Map landmark indices to body parts for more meaningful feedback
        body_parts = {
            "lm_0": "Nose", "lm_1": "Left eye inner", "lm_2": "Left eye", "lm_3": "Left eye outer",
            "lm_4": "Right eye inner", "lm_5": "Right eye", "lm_6": "Right eye outer",
            "lm_7": "Left ear", "lm_8": "Right ear", "lm_9": "Mouth left", "lm_10": "Mouth right",
            "lm_11": "Left shoulder", "lm_12": "Right shoulder", "lm_13": "Left elbow", "lm_14": "Right elbow",
            "lm_15": "Left wrist", "lm_16": "Right wrist", "lm_17": "Left pinky", "lm_18": "Right pinky",
            "lm_19": "Left index", "lm_20": "Right index", "lm_21": "Left thumb", "lm_22": "Right thumb",
            "lm_23": "Left hip", "lm_24": "Right hip", "lm_25": "Left knee", "lm_26": "Right knee",
            "lm_27": "Left ankle", "lm_28": "Right ankle", "lm_29": "Left heel", "lm_30": "Right heel",
            "lm_31": "Left foot index", "lm_32": "Right foot index"
        }
        
        return render_template_string(
            html, 
            filename=file.filename,
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            result=results,
            body_parts=body_parts,
            has_upper_issues=has_upper_issues,
            has_lower_issues=has_lower_issues
        )
    
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        return jsonify({'error': f"Error analyzing video: {str(e)}"}), 500
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def generate_sample_results(filename):
    """Generate sample results for demonstration purposes"""
    # In a real application, this would be based on actual video analysis
    # For the demo, we'll generate a mix of good and problematic landmarks
    
    # Use the filename to seed the random generation for consistent results
    import hashlib
    seed = int(hashlib.md5(filename.encode()).hexdigest(), 16) % 10000
    import random
    random.seed(seed)
    
    # Generate random differences with some landmarks exceeding the threshold
    diffs = {}
    is_ok = True
    
    for i in range(33):
        lm_key = f"lm_{i}"
        # Generate a random difference, with some exceeding the threshold
        # More likely to have issues in key posture landmarks (shoulders, hips, etc.)
        if i in [11, 12, 13, 14, 23, 24, 25, 26] and random.random() < 0.7:
            diff = random.uniform(0.05, 0.15)  # Above threshold (0.05)
            is_ok = False
        else:
            diff = random.uniform(0.01, 0.049)  # Below threshold
        diffs[lm_key] = diff
    
    # Generate advice based on the diffs
    advice = generate_advice(diffs)
    
    return {
        'frame': 0,
        'diffs': diffs,
        'is_ok': is_ok,
        'advice': advice
    }

def generate_advice(diffs):
    """Generate advice based on differences"""
    # List of problematic landmarks (above threshold)
    problem_landmarks = [lm for lm, diff in diffs.items() if diff > 0.05]
    
    if not problem_landmarks:
        return "Perfect form! Keep it up! Your positioning is well-aligned with the ideal pose."
    
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
        advice.append("Your form needs adjustment in both upper and lower body positioning.")
    elif upper_body_issues:
        if "lm_11" in upper_body_issues or "lm_12" in upper_body_issues:
            advice.append("Your shoulder alignment could be improved.")
        if "lm_13" in upper_body_issues or "lm_14" in upper_body_issues:
            advice.append("Try adjusting your elbow position for better form.")
        if "lm_15" in upper_body_issues or "lm_16" in upper_body_issues:
            advice.append("Your wrist positioning could use some correction.")
    elif lower_body_issues:
        if "lm_23" in lower_body_issues or "lm_24" in lower_body_issues:
            advice.append("Adjust your hip position to better match the ideal form.")
        if "lm_25" in lower_body_issues or "lm_26" in lower_body_issues:
            advice.append("Your knee position needs adjustment, consider bending more or less depending on the exercise.")
        if "lm_27" in lower_body_issues or "lm_28" in lower_body_issues:
            advice.append("Pay attention to your ankle alignment for better stability and form.")
    
    if not advice:
        # Generic advice if we couldn't generate specific feedback
        advice.append("Your form needs some adjustment. Try to match the reference position more closely.")
    
    return " ".join(advice)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)