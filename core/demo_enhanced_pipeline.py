"""
Demo script showing how to use the enhanced form analysis pipeline
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional
import argparse
import json
import os

from enhanced_analysis import EnhancedBodyAnalyzer
from realtime_feedback import RealtimeSafetyMonitor, SafetyAlert

class EnhancedFormAnalysisDemo:
    """Demo class for the enhanced form analysis system"""
    
    def __init__(self, user_height_cm: float, exercise_type: str):
        """
        Args:
            user_height_cm: User's height in cm
            exercise_type: Type of exercise to analyze
        """
        self.analyzer = EnhancedBodyAnalyzer(user_height_cm, exercise_type)
        self.safety_monitor = RealtimeSafetyMonitor()
        
        # MediaPipe setup
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
    def analyze_video_realtime(self, video_path: str, show_visualization: bool = True):
        """
        Analyze video with real-time feedback
        
        Args:
            video_path: Path to video file
            show_visualization: Show live visualization window
        """
        print(f"Analyzing video: {video_path}")
        print(f"Exercise type: {self.analyzer.exercise_type}")
        print(f"User height: {self.analyzer.user_height_cm} cm")
        print("-" * 50)
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        
        # Initialize pose detection
        with self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as pose:
            
            frame_count = 0
            
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    break
                
                # Process frame
                results = self._process_single_frame(image, pose, frame_count, fps)
                
                if results and show_visualization:
                    # Create visualization
                    viz_image = self._create_realtime_visualization(
                        image, results, pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    )
                    
                    # Show frame
                    cv2.imshow('Enhanced Form Analysis', viz_image)
                    
                    # Handle key press
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord(' '):  # Pause on spacebar
                        cv2.waitKey(0)
                
                frame_count += 1
                
                # Print periodic updates
                if frame_count % 30 == 0:
                    self._print_analysis_update(results)
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Print final summary
        self._print_final_summary()
    
    def _process_single_frame(self, image: np.ndarray, pose: Any, 
                            frame_idx: int, fps: float) -> Optional[dict]:
        """Process a single frame through the pipeline"""
        
        # Use the analyzer's frame processing
        results = self.analyzer._process_frame(image, pose, frame_idx, fps)
        
        if results:
            # Add safety monitoring
            safety_alerts = self.safety_monitor.check_form_safety(
                results['landmarks_cm'],
                self.analyzer.exercise_type.value if self.analyzer.exercise_type else 'unknown',
                results.get('phase', 'unknown')
            )
            
            results['safety_alerts'] = safety_alerts
            
            # Handle critical safety alerts
            for alert in safety_alerts:
                if alert.severity == 'danger':
                    print(f"\n🚨 DANGER: {alert.issue} - {alert.immediate_action}")
                elif alert.severity == 'warning':
                    print(f"\n⚠️  WARNING: {alert.issue} - {alert.immediate_action}")
        
        return results
    
    def _create_realtime_visualization(self, image: np.ndarray, 
                                     analysis_results: dict,
                                     pose_results: Any) -> np.ndarray:
        """Create enhanced visualization with all analysis data"""
        
        viz_image = image.copy()
        h, w = viz_image.shape[:2]
        
        # Draw pose skeleton
        if pose_results and pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                viz_image,
                pose_results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
        
        # Create info panel background
        panel_height = 250
        info_panel = np.zeros((panel_height, w, 3), dtype=np.uint8)
        info_panel[:] = (40, 40, 40)  # Dark gray background
        
        # Add form score
        score = analysis_results.get('form_score', 0)
        score_color = self._get_score_color(score)
        cv2.putText(info_panel, f"Form Score: {score:.0f}/100", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, score_color, 2)
        
        # Add exercise phase
        phase = analysis_results.get('phase', 'unknown')
        cv2.putText(info_panel, f"Phase: {phase.upper()}", 
                   (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Add scale confidence
        confidence = analysis_results.get('scale_confidence', 0)
        conf_color = (0, 255, 0) if confidence > 0.8 else (0, 255, 255) if confidence > 0.6 else (0, 0, 255)
        cv2.putText(info_panel, f"Tracking Confidence: {confidence:.1%}", 
                   (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.6, conf_color, 1)
        
        # Add measurements
        measurements = analysis_results.get('measurements', {})
        x_offset = w // 2
        y_offset = 40
        for key, value in list(measurements.items())[:4]:  # Show first 4 measurements
            text = f"{key.replace('_', ' ').title()}: {value} cm"
            cv2.putText(info_panel, text, 
                       (x_offset, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            y_offset += 30
        
        # Add safety alerts
        safety_alerts = analysis_results.get('safety_alerts', [])
        if safety_alerts:
            # Draw alert box
            alert_box = np.zeros((100, w, 3), dtype=np.uint8)
            primary_alert = safety_alerts[0]  # Show most severe alert
            
            alert_color = {
                'danger': (0, 0, 255),
                'warning': (0, 165, 255),
                'caution': (0, 255, 255)
            }.get(primary_alert.severity, (255, 255, 255))
            
            # Flash effect for danger
            if primary_alert.severity == 'danger':
                if (analysis_results['frame_idx'] // 15) % 2 == 0:
                    alert_box[:] = alert_color
            else:
                alert_box[:20] = alert_color
                alert_box[-20:] = alert_color
                alert_box[:, :20] = alert_color
                alert_box[:, -20:] = alert_color
            
            # Add alert text
            cv2.putText(alert_box, f"{primary_alert.severity.upper()}: {primary_alert.issue}", 
                       (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(alert_box, primary_alert.immediate_action, 
                       (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            
            # Overlay alert box
            viz_image[h-100:h] = cv2.addWeighted(viz_image[h-100:h], 0.3, alert_box, 0.7, 0)
        
        # Add form feedback
        feedback_y = 150
        for feedback in analysis_results.get('form_feedback', [])[:2]:  # Show top 2 feedback
            severity = feedback.get('severity', 'info')
            color = {
                'critical': (0, 0, 255),
                'warning': (0, 165, 255),
                'info': (255, 255, 0)
            }.get(severity, (255, 255, 255))
            
            message = feedback.get('message', '')
            if len(message) > 50:
                message = message[:47] + "..."
            
            cv2.putText(info_panel, f"• {message}", 
                       (20, feedback_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            feedback_y += 25
            
            suggestion = feedback.get('improvement_suggestion', '')
            if suggestion and len(suggestion) > 0:
                if len(suggestion) > 50:
                    suggestion = suggestion[:47] + "..."
                cv2.putText(info_panel, f"  → {suggestion}", 
                           (30, feedback_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
                feedback_y += 25
        
        # Combine visualization
        combined = np.vstack([viz_image, info_panel])
        
        return combined
    
    def _get_score_color(self, score: float) -> tuple:
        """Get color based on form score"""
        if score >= 80:
            return (0, 255, 0)  # Green
        elif score >= 60:
            return (0, 255, 255)  # Yellow
        elif score >= 40:
            return (0, 165, 255)  # Orange
        else:
            return (0, 0, 255)  # Red
    
    def _print_analysis_update(self, results: Optional[dict]):
        """Print periodic analysis updates"""
        if not results:
            return
            
        print(f"\nFrame {results['frame_idx']} - "
              f"Score: {results.get('form_score', 0):.0f}/100, "
              f"Phase: {results.get('phase', 'unknown')}")
    
    def _print_final_summary(self):
        """Print final analysis summary"""
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        
        # Get safety summary
        safety_summary = self.safety_monitor.get_safety_summary()
        
        print(f"\nSafety Summary:")
        print(f"  Total Alerts: {safety_summary['total_alerts']}")
        print(f"  By Severity:")
        for severity, count in safety_summary['by_severity'].items():
            print(f"    - {severity.capitalize()}: {count}")
        
        if safety_summary['most_common_issues']:
            print(f"\n  Most Common Issues:")
            for issue_data in safety_summary['most_common_issues']:
                print(f"    - {issue_data['issue']}: {issue_data['count']} times")
        
        print("\nRecommendations:")
        if safety_summary['by_severity']['danger'] > 0:
            print("  ⚠️  Critical form issues detected. Consider working with a trainer.")
        elif safety_summary['by_severity']['warning'] > 5:
            print("  ⚠️  Multiple form warnings. Focus on the suggested corrections.")
        else:
            print("  ✅ Good form overall! Keep up the great work.")


def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description='Enhanced Form Analysis Demo')
    parser.add_argument('video_path', help='Path to video file')
    parser.add_argument('--height', type=float, required=True, help='User height in cm')
    parser.add_argument('--exercise', default='squat', 
                       choices=['squat', 'deadlift', 'bench_press', 'pushup', 
                               'pullup', 'lunge', 'overhead_press'],
                       help='Type of exercise')
    parser.add_argument('--no-viz', action='store_true', 
                       help='Disable visualization window')
    
    args = parser.parse_args()
    
    # Create demo instance
    demo = EnhancedFormAnalysisDemo(args.height, args.exercise)
    
    # Run analysis
    demo.analyze_video_realtime(
        args.video_path,
        show_visualization=not args.no_viz
    )


if __name__ == "__main__":
    # Example usage
    print("Enhanced Form Analysis Pipeline Demo")
    print("-" * 50)
    
    # You can run this script with:
    # python demo_enhanced_pipeline.py video.mp4 --height 170 --exercise squat
    
    # For testing without command line args:
    if len(os.sys.argv) == 1:
        print("\nExample usage:")
        print("python demo_enhanced_pipeline.py video.mp4 --height 170 --exercise squat")
        print("\nRunning demo with sample parameters...")
        
        demo = EnhancedFormAnalysisDemo(170, 'squat')
        print("\nDemo initialized successfully!")
        print("Components:")
        print("- Enhanced scaling with multiple reference points")
        print("- Advanced noise reduction filters")
        print("- Exercise-specific form evaluation")
        print("- Real-time safety monitoring")
        print("- Form scoring (0-100)")
    else:
        main()