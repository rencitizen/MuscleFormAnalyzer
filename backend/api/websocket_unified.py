"""WebSocket endpoint for real-time unified theory analysis."""

from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Any, Optional
import json
import asyncio
import numpy as np
import cv2
import base64
import logging
from datetime import datetime

from backend.services.unified_theory_service import UnifiedTheoryService
from backend.utils.auth import verify_ws_token

logger = logging.getLogger(__name__)


class UnifiedTheoryConnectionManager:
    """Manages WebSocket connections for unified theory analysis."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_services: Dict[str, UnifiedTheoryService] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_services[user_id] = UnifiedTheoryService()
        logger.info(f"User {user_id} connected for unified theory analysis")
        
    def disconnect(self, user_id: str):
        """Remove connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_services:
            del self.user_services[user_id]
        logger.info(f"User {user_id} disconnected from unified theory analysis")
        
    async def send_analysis(self, user_id: str, analysis: Dict[str, Any]):
        """Send analysis results to specific user."""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_json(analysis)
            
    def get_service(self, user_id: str) -> Optional[UnifiedTheoryService]:
        """Get unified theory service for user."""
        return self.user_services.get(user_id)


# Global connection manager
manager = UnifiedTheoryConnectionManager()


async def unified_theory_ws(
    websocket: WebSocket,
    token: str = Query(...),
    exercise_type: str = Query(default="squat")
):
    """WebSocket endpoint for real-time unified theory analysis.
    
    Message format:
    {
        "type": "frame" | "calibration" | "user_profile" | "settings",
        "data": {
            "frame": "base64_encoded_image",  // for type="frame"
            "calibration": {...},              // for type="calibration"
            "profile": {...},                  // for type="user_profile"
            "settings": {...}                  // for type="settings"
        }
    }
    
    Response format:
    {
        "type": "analysis" | "error" | "status",
        "data": {
            // Unified theory analysis results
        },
        "timestamp": "ISO timestamp"
    }
    """
    user = None
    user_profile = {}
    calibration_data = None
    frame_count = 0
    last_analysis_time = 0
    analysis_interval = 0.1  # Analyze every 100ms
    
    try:
        # Verify token
        user = await verify_ws_token(token)
        if not user:
            await websocket.close(code=1008, reason="Invalid token")
            return
            
        user_id = user['uid']
        await manager.connect(websocket, user_id)
        
        # Send initial status
        await websocket.send_json({
            "type": "status",
            "data": {
                "message": "Connected to unified theory analysis",
                "exercise_type": exercise_type,
                "ready": True
            },
            "timestamp": datetime.now().isoformat()
        })
        
        # Get service instance
        service = manager.get_service(user_id)
        if not service:
            raise Exception("Failed to initialize unified theory service")
            
        # Message processing loop
        while True:
            try:
                # Receive message with timeout
                message = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0  # 30 second timeout
                )
                
                msg_type = message.get('type')
                msg_data = message.get('data', {})
                
                if msg_type == 'frame':
                    # Process video frame
                    frame_data = msg_data.get('frame')
                    if frame_data:
                        frame_count += 1
                        current_time = asyncio.get_event_loop().time()
                        
                        # Rate limiting
                        if current_time - last_analysis_time >= analysis_interval:
                            # Decode frame
                            frame_bytes = base64.b64decode(
                                frame_data.split(',')[1] if ',' in frame_data else frame_data
                            )
                            nparr = np.frombuffer(frame_bytes, np.uint8)
                            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            
                            if frame is not None:
                                # Perform unified analysis
                                analysis = await service.analyze_frame_unified(
                                    frame,
                                    exercise_type,
                                    user_profile,
                                    calibration_data
                                )
                                
                                # Prepare response
                                response = {
                                    "type": "analysis",
                                    "data": {
                                        "frame_number": frame_count,
                                        "success": analysis.get('success', False),
                                        "unified_scores": analysis.get('unified_scores', {}),
                                        "feedback": analysis.get('feedback', []),
                                        "physics": {
                                            "joint_angles": analysis.get('physics', {}).get('joint_angles', {}),
                                            "moment_arms": analysis.get('physics', {}).get('moment_arms', {}),
                                            "energy_efficiency": analysis.get('physics', {}).get('energy_efficiency', 0)
                                        },
                                        "biomechanics": {
                                            "current_phase": str(analysis.get('biomechanics', {}).get('current_phase', 'setup')),
                                            "muscle_activation": analysis.get('biomechanics', {}).get('muscle_activation', {}),
                                            "movement_quality": analysis.get('biomechanics', {}).get('movement_quality', {})
                                        },
                                        "optimization": {
                                            "improvement_priorities": analysis.get('optimization', {}).get('improvement_priorities', []),
                                            "optimal_form": analysis.get('optimization', {}).get('optimal_form')
                                        }
                                    },
                                    "timestamp": analysis.get('timestamp', datetime.now().isoformat())
                                }
                                
                                # Add annotated frame if available
                                if 'annotated_frame' in analysis and analysis['annotated_frame'] is not None:
                                    response['data']['annotated_frame'] = analysis['annotated_frame']
                                    
                                await manager.send_analysis(user_id, response)
                                last_analysis_time = current_time
                                
                elif msg_type == 'calibration':
                    # Update calibration data
                    calibration_data = msg_data.get('calibration', {})
                    await websocket.send_json({
                        "type": "status",
                        "data": {"message": "Calibration updated"},
                        "timestamp": datetime.now().isoformat()
                    })
                    
                elif msg_type == 'user_profile':
                    # Update user profile
                    user_profile = msg_data.get('profile', {})
                    
                    # Reinitialize optimization objectives
                    service.optimization_engine.define_objective_functions(user_profile)
                    
                    await websocket.send_json({
                        "type": "status",
                        "data": {"message": "User profile updated"},
                        "timestamp": datetime.now().isoformat()
                    })
                    
                elif msg_type == 'settings':
                    # Update analysis settings
                    settings = msg_data.get('settings', {})
                    
                    if 'exercise_type' in settings:
                        exercise_type = settings['exercise_type']
                        
                    if 'analysis_interval' in settings:
                        analysis_interval = max(0.05, settings['analysis_interval'])
                        
                    await websocket.send_json({
                        "type": "status",
                        "data": {
                            "message": "Settings updated",
                            "exercise_type": exercise_type,
                            "analysis_interval": analysis_interval
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                    
                elif msg_type == 'get_summary':
                    # Get analysis summary
                    if service.analysis_results_history:
                        summary = service._aggregate_sequence_results(
                            service.analysis_results_history[-50:],  # Last 50 frames
                            exercise_type
                        )
                        
                        await websocket.send_json({
                            "type": "summary",
                            "data": summary,
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "No analysis history available"},
                            "timestamp": datetime.now().isoformat()
                        })
                        
                elif msg_type == 'ping':
                    # Heartbeat
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except asyncio.TimeoutError:
                # Send heartbeat on timeout
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                })
                
            except json.JSONDecodeError as e:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Invalid JSON: {str(e)}"},
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Processing error: {str(e)}"},
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user['uid'] if user else 'unknown'}")
        
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Server error: {str(e)}"},
                "timestamp": datetime.now().isoformat()
            })
        except:
            pass
            
    finally:
        if user:
            manager.disconnect(user['uid'])
            
            
# Export the WebSocket route
websocket_route = unified_theory_ws