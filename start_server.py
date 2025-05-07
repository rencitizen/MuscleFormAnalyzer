import uvicorn
import sys
import os

# Disable GPU usage for MediaPipe
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"

def main():
    """Run the FastAPI application directly with Uvicorn"""
    print("Starting Muscle-Form Analyzer MVP API...")
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)

if __name__ == "__main__":
    main()