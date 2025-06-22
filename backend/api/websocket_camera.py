"""
WebSocket API for real-time camera feed analysis
Supports both internal and external camera streams
"""
import logging
import json
import base64
import asyncio
from typing import Optional, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.responses import HTMLResponse
import cv2
import numpy as np

from ..services.mediapipe_service import MediaPipeService
from ..api.auth import get_current_user_ws
from ..database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

class CameraStreamAnalyzer:
    """Handles real-time camera stream analysis"""
    
    def __init__(self):
        self.mediapipe_service = MediaPipeService()
        self.frame_buffer = []
        self.analysis_interval = 5  # Analyze every 5th frame
        self.frame_count = 0
        self.last_analysis_time = 0
        self.min_analysis_interval = 0.1  # Minimum 100ms between analyses
    
    async def analyze_frame(self, frame_data: str, exercise_type: str) -> Dict:
        """Analyze a single frame from camera stream"""
        try:
            # Decode base64 frame
            frame_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {"success": False, "error": "Invalid frame data"}
            
            # Process with MediaPipe
            results = self.mediapipe_service.process_frame(frame)
            
            if results.pose_landmarks:
                # Analyze pose
                analysis = self.mediapipe_service.analyze_exercise(
                    results.pose_landmarks,
                    exercise_type,
                    frame.shape[:2]
                )
                
                return {
                    "success": True,
                    "pose_detected": True,
                    "analysis": analysis,
                    "landmarks": self._serialize_landmarks(results.pose_landmarks)
                }
            
            return {
                "success": True,
                "pose_detected": False,
                "message": "No pose detected in frame"
            }
            
        except Exception as e:
            logger.error(f"Frame analysis error: {e}")
            return {"success": False, "error": str(e)}
    
    def _serialize_landmarks(self, landmarks):
        """Serialize pose landmarks for transmission"""
        return [
            {
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility
            }
            for landmark in landmarks.landmark
        ]

# Global analyzer instance
camera_analyzer = CameraStreamAnalyzer()

@router.websocket("/ws/camera/{user_id}")
async def websocket_camera_endpoint(
    websocket: WebSocket,
    user_id: str,
    exercise_type: str = Query("squat", description="Exercise type to analyze"),
    camera_type: str = Query("user", description="Camera type: 'user' for front, 'environment' for back")
):
    """
    WebSocket endpoint for real-time camera stream analysis
    
    Camera types:
    - 'user': Front-facing camera (selfie camera)
    - 'environment': Back-facing camera
    """
    await websocket.accept()
    connection_id = f"{user_id}_{camera_type}"
    active_connections[connection_id] = websocket
    
    logger.info(f"WebSocket connection established for user {user_id}, camera: {camera_type}")
    
    try:
        # Send initial configuration
        await websocket.send_json({
            "type": "config",
            "data": {
                "exercise_type": exercise_type,
                "camera_type": camera_type,
                "analysis_interval": camera_analyzer.analysis_interval,
                "supported_exercises": ["squat", "bench_press", "deadlift", "pushup", "plank"]
            }
        })
        
        frame_counter = 0
        
        while True:
            # Receive frame data
            data = await websocket.receive_json()
            
            if data["type"] == "frame":
                frame_counter += 1
                
                # Skip frames based on interval
                if frame_counter % camera_analyzer.analysis_interval == 0:
                    # Check time-based throttling
                    import time
                    current_time = time.time()
                    if current_time - camera_analyzer.last_analysis_time >= camera_analyzer.min_analysis_interval:
                        # Analyze frame
                        analysis_result = await camera_analyzer.analyze_frame(
                            data["frame"],
                            exercise_type
                        )
                        camera_analyzer.last_analysis_time = current_time
                        
                        # Send analysis result
                        await websocket.send_json({
                            "type": "analysis",
                            "data": analysis_result
                        })
                    else:
                        # Send skip notification
                        await websocket.send_json({
                            "type": "skip",
                            "data": {"reason": "throttled"}
                        })
                else:
                    # Send skip notification
                    await websocket.send_json({
                        "type": "skip",
                        "data": {"reason": "interval", "frame": frame_counter}
                    })
                
            elif data["type"] == "change_exercise":
                exercise_type = data["exercise"]
                await websocket.send_json({
                    "type": "exercise_changed",
                    "data": {"exercise": exercise_type}
                })
                
            elif data["type"] == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)}
        })
    finally:
        if connection_id in active_connections:
            del active_connections[connection_id]

@router.websocket("/ws/camera/test")
async def websocket_test_endpoint(websocket: WebSocket):
    """Test endpoint for WebSocket camera connection"""
    await websocket.accept()
    
    try:
        await websocket.send_json({
            "type": "test",
            "message": "WebSocket camera connection successful",
            "features": {
                "real_time_analysis": True,
                "multiple_exercises": True,
                "camera_switching": True,
                "pose_detection": True
            }
        })
        
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        logger.info("Test WebSocket disconnected")

@router.get("/camera/permissions")
async def get_camera_permissions():
    """
    Get camera permission requirements and browser compatibility
    """
    return {
        "requirements": {
            "permissions": ["camera"],
            "secure_context": True,  # HTTPS required
            "browser_support": {
                "chrome": "47+",
                "firefox": "36+",
                "safari": "11+",
                "edge": "12+"
            }
        },
        "camera_constraints": {
            "video": {
                "facingMode": {
                    "user": "Front camera (selfie)",
                    "environment": "Back camera"
                },
                "width": {"ideal": 1280, "max": 1920},
                "height": {"ideal": 720, "max": 1080},
                "frameRate": {"ideal": 30, "max": 60}
            }
        },
        "troubleshooting": {
            "camera_not_found": [
                "Check if camera is connected",
                "Grant camera permissions in browser",
                "Ensure HTTPS connection",
                "Try different browser"
            ],
            "permission_denied": [
                "Click on camera icon in address bar",
                "Allow camera access for this site",
                "Check system privacy settings"
            ]
        }
    }

@router.get("/camera/demo")
async def camera_demo_page():
    """
    Demo page for testing camera functionality
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera Test - TENAX FIT</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            video { width: 100%; max-width: 600px; border: 2px solid #333; }
            button { margin: 10px; padding: 10px 20px; font-size: 16px; }
            #status { margin: 20px 0; padding: 10px; background: #f0f0f0; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>TENAX FIT Camera Test</h1>
        <div id="status">Camera status: Not started</div>
        
        <video id="video" autoplay playsinline></video>
        
        <div>
            <button onclick="startCamera('user')">Front Camera</button>
            <button onclick="startCamera('environment')">Back Camera</button>
            <button onclick="stopCamera()">Stop Camera</button>
            <button onclick="switchCamera()">Switch Camera</button>
        </div>
        
        <div id="info">
            <h3>Detected Devices:</h3>
            <ul id="devices"></ul>
        </div>
        
        <script>
            let stream = null;
            let currentFacingMode = 'user';
            
            // List available devices
            async function listDevices() {
                try {
                    const devices = await navigator.mediaDevices.enumerateDevices();
                    const videoDevices = devices.filter(device => device.kind === 'videoinput');
                    
                    const devicesList = document.getElementById('devices');
                    devicesList.innerHTML = '';
                    
                    videoDevices.forEach((device, index) => {
                        const li = document.createElement('li');
                        li.textContent = device.label || `Camera ${index + 1}`;
                        devicesList.appendChild(li);
                    });
                    
                    updateStatus(`Found ${videoDevices.length} camera(s)`, 'success');
                } catch (error) {
                    updateStatus('Error listing devices: ' + error.message, 'error');
                }
            }
            
            async function startCamera(facingMode) {
                try {
                    // Stop existing stream
                    if (stream) {
                        stopCamera();
                    }
                    
                    currentFacingMode = facingMode;
                    updateStatus(`Starting ${facingMode} camera...`);
                    
                    const constraints = {
                        video: {
                            facingMode: facingMode,
                            width: { ideal: 1280 },
                            height: { ideal: 720 }
                        }
                    };
                    
                    stream = await navigator.mediaDevices.getUserMedia(constraints);
                    const video = document.getElementById('video');
                    video.srcObject = stream;
                    
                    updateStatus(`${facingMode} camera active`, 'success');
                    
                    // Update device list
                    await listDevices();
                    
                } catch (error) {
                    updateStatus('Camera error: ' + error.message, 'error');
                    console.error('Camera error:', error);
                }
            }
            
            function stopCamera() {
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                    stream = null;
                    document.getElementById('video').srcObject = null;
                    updateStatus('Camera stopped');
                }
            }
            
            function switchCamera() {
                const newFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';
                startCamera(newFacingMode);
            }
            
            function updateStatus(message, type = '') {
                const status = document.getElementById('status');
                status.textContent = 'Camera status: ' + message;
                status.className = type;
            }
            
            // Check browser support
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                updateStatus('Camera API not supported in this browser', 'error');
            } else {
                updateStatus('Camera API supported. Click a button to start.', 'success');
                listDevices();
            }
            
            // WebSocket test
            function testWebSocket() {
                const ws = new WebSocket('ws://localhost:8000/api/form/ws/camera/test');
                
                ws.onopen = () => {
                    console.log('WebSocket connected');
                    ws.send('Hello from camera test');
                };
                
                ws.onmessage = (event) => {
                    console.log('WebSocket message:', event.data);
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)