import os
import json
import logging
import shutil
import uuid
from typing import Dict, List, Optional, Union
import math

import cv2
import mediapipe as mp
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile, Form, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Muscle-Form Analyzer MVP",
    description="API for analyzing workout form using MediaPipe pose estimation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Create temporary directory if it doesn't exist
os.makedirs("/tmp", exist_ok=True)

# Set environment variable to force CPU usage
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"

# Initialize MediaPipe Pose with CPU options
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    enable_segmentation=False
)

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

# Define models
class Landmark(BaseModel):
    x: float
    y: float
    z: float

class PoseFrame(BaseModel):
    frame: int
    landmarks: Dict[str, Landmark]

class ExtractResponse(BaseModel):
    frames: List[PoseFrame]

class CompareInput(BaseModel):
    frames: List[PoseFrame]

class LandmarkDiff(BaseModel):
    value: float
    is_ok: bool

class CompareResponse(BaseModel):
    frame: int
    diffs: Dict[str, float]
    is_ok: bool
    advice: str

# Helper functions
def extract_landmarks_from_video(video_path: str) -> List[PoseFrame]:
    """
    Extract pose landmarks from each frame of the video
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_idx = 0
    
    # Check if video opened successfully
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="Failed to open video file")
    
    # Check if video is too long (> 60 seconds)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    if duration > 60:
        cap.release()
        raise HTTPException(status_code=400, detail="Video is too long (max 60 seconds)")
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        
        # Convert the BGR image to RGB and process it with MediaPipe Pose
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        
        if results.pose_landmarks:
            # Extract landmarks
            landmarks_dict = {}
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                landmarks_dict[f"lm_{i}"] = {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z
                }
            
            # Create frame data
            frame_data = PoseFrame(
                frame=frame_idx,
                landmarks=landmarks_dict
            )
            frames.append(frame_data)
        else:
            # If no landmarks detected, add empty frame with index
            logger.warning(f"No landmarks detected in frame {frame_idx}")
            empty_landmarks = {f"lm_{i}": {"x": 0, "y": 0, "z": 0} for i in range(33)}
            frames.append(PoseFrame(frame=frame_idx, landmarks=empty_landmarks))
        
        frame_idx += 1
    
    cap.release()
    return frames

def calculate_euclidean_distance(lm1: Dict, lm2: Dict) -> float:
    """
    Calculate Euclidean distance between two landmarks
    """
    return math.sqrt(
        (lm1["x"] - lm2["x"]) ** 2 +
        (lm1["y"] - lm2["y"]) ** 2 +
        (lm1["z"] - lm2["z"]) ** 2
    )

def compare_with_ideal_pose(landmarks: Dict[str, Landmark]) -> Dict[str, Union[Dict, bool, str]]:
    """
    Compare extracted landmarks with ideal pose
    """
    diffs = {}
    all_ok = True
    threshold = 0.05
    
    # Compare each landmark with ideal pose
    for lm_key, lm_value in landmarks.items():
        if lm_key in IDEAL_POSE["landmarks"]:
            # Convert Pydantic model to dict for calculation
            lm_dict = {"x": lm_value.x, "y": lm_value.y, "z": lm_value.z}
            
            # Calculate distance
            diff = calculate_euclidean_distance(lm_dict, IDEAL_POSE["landmarks"][lm_key])
            diffs[lm_key] = diff
            
            # Check if distance is above threshold
            if diff > threshold:
                all_ok = False
    
    # Generate advice based on differences
    advice = generate_advice(diffs, threshold)
    
    return {
        "diffs": diffs,
        "is_ok": all_ok,
        "advice": advice
    }

def generate_advice(diffs: Dict[str, float], threshold: float) -> str:
    """
    Generate advice based on landmark differences
    """
    # List of problematic landmarks (above threshold)
    problem_landmarks = [lm for lm, diff in diffs.items() if diff > threshold]
    
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

# API endpoints
@app.post("/api/extract", response_model=ExtractResponse)
async def extract_landmarks(file: UploadFile = File(...)):
    """
    Extract pose landmarks from uploaded video file
    """
    try:
        # Validate file size (max 150MB)
        size_limit = 150 * 1024 * 1024  # 150MB in bytes
        content = await file.read()
        if len(content) > size_limit:
            raise HTTPException(status_code=400, detail="File too large (max 150MB)")
        
        # Check file extension
        if not file.filename.lower().endswith(".mp4"):
            raise HTTPException(status_code=400, detail="Only MP4 files are supported")
        
        # Create a unique filename
        temp_file_path = f"/tmp/{uuid.uuid4()}.mp4"
        
        # Save the uploaded file temporarily
        with open(temp_file_path, "wb") as f:
            f.write(content)
        
        # Extract landmarks from the video
        frames = extract_landmarks_from_video(temp_file_path)
        
        # Remove the temporary file
        os.remove(temp_file_path)
        
        return ExtractResponse(frames=frames)
    
    except Exception as e:
        # Make sure to clean up temporary files in case of errors
        temp_file_path_local = locals().get('temp_file_path')
        if temp_file_path_local and os.path.exists(temp_file_path_local):
            os.remove(temp_file_path_local)
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

@app.post("/api/compare", response_model=List[CompareResponse])
async def compare_landmarks(data: CompareInput):
    """
    Compare extracted landmarks with ideal pose
    """
    try:
        results = []
        for frame in data.frames:
            comparison = compare_with_ideal_pose(frame.landmarks)
            results.append(
                CompareResponse(
                    frame=frame.frame,
                    diffs=comparison["diffs"],
                    is_ok=comparison["is_ok"],
                    advice=comparison["advice"]
                )
            )
        return results
    except Exception as e:
        logger.error(f"Error comparing landmarks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error comparing landmarks: {str(e)}")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the Muscle-Form Analyzer MVP API")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down, cleaning up temporary files")
    # Clean up any remaining temporary files
    for filename in os.listdir("/tmp"):
        if filename.endswith(".mp4") or filename.endswith(".json"):
            os.remove(os.path.join("/tmp", filename))

# Run the server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
