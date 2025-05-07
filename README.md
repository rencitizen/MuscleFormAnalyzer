# Muscle-Form Analyzer MVP

A FastAPI-based workout form analyzer that compares uploaded exercise videos with ideal postures using MediaPipe.

## Overview

This project provides a backend API for analyzing workout form in uploaded videos. It uses MediaPipe to extract joint coordinates from each frame of a video and compares them with ideal reference poses to provide feedback on form quality.

## Features

- Extract pose landmarks from workout videos (MP4 format)
- Compare extracted landmarks with ideal reference poses
- Provide feedback and advice on form differences
- Support for videos up to 60 seconds (720p/30fps, max 150MB)

## Technical Stack

- Python 3.11
- FastAPI
- OpenCV (opencv-python==4.10.0.82)
- MediaPipe (mediapipe==0.10.9)
- NumPy
- Uvicorn (ASGI server)

## API Endpoints

### POST /extract

Extracts pose landmarks from an uploaded video file.

**Request:**
- `file` (MP4 video file, multipart/form-data)

**Response:**
```json
{
  "frames": [
    {
      "frame": 0,
      "landmarks": {
        "lm_0": {"x": 0.5, "y": 0.3, "z": 0.0},
        "lm_1": {"x": 0.48, "y": 0.29, "z": 0.01},
        ...
      }
    },
    ...
  ]
}
