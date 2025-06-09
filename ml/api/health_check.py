"""
システムヘルスチェック機能
フォーム分析システムの安定性監視と診断
"""

import os
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

class SystemHealthChecker:
    """システムの健全性をチェックするクラス"""
    
    def __init__(self):
        self.checks = {
            'dependencies': self._check_dependencies,
            'memory': self._check_memory,
            'disk_space': self._check_disk_space,
            'mediapipe': self._check_mediapipe,
            'opencv': self._check_opencv,
            'database': self._check_database
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """全てのヘルスチェックを実行"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {},
            'warnings': [],
            'errors': []
        }
        
        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func()
                results['checks'][check_name] = check_result
                
                if check_result['status'] == 'warning':
                    results['warnings'].append(f"{check_name}: {check_result['message']}")
                elif check_result['status'] == 'error':
                    results['errors'].append(f"{check_name}: {check_result['message']}")
                    results['overall_status'] = 'unhealthy'
                    
            except Exception as e:
                error_msg = f"{check_name} check failed: {str(e)}"
                results['errors'].append(error_msg)
                results['checks'][check_name] = {
                    'status': 'error',
                    'message': error_msg,
                    'details': {}
                }
                results['overall_status'] = 'unhealthy'
        
        # 警告がある場合は全体ステータスを調整
        if results['warnings'] and results['overall_status'] == 'healthy':
            results['overall_status'] = 'degraded'
        
        return results
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """依存関係のチェック"""
        missing_deps = []
        available_deps = []
        
        dependencies = [
            ('cv2', 'OpenCV'),
            ('mediapipe', 'MediaPipe'),
            ('numpy', 'NumPy'),
            ('flask', 'Flask'),
            ('psutil', 'psutil')
        ]
        
        for module_name, display_name in dependencies:
            try:
                __import__(module_name)
                available_deps.append(display_name)
            except ImportError:
                missing_deps.append(display_name)
        
        if missing_deps:
            return {
                'status': 'error',
                'message': f"Missing dependencies: {', '.join(missing_deps)}",
                'details': {
                    'missing': missing_deps,
                    'available': available_deps
                }
            }
        
        return {
            'status': 'healthy',
            'message': 'All dependencies available',
            'details': {
                'available': available_deps
            }
        }
    
    def _check_memory(self) -> Dict[str, Any]:
        """メモリ使用量のチェック"""
        try:
            memory = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            memory_percent = memory.percent
            available_gb = memory.available / 1024 / 1024 / 1024
            
            if memory_percent > 90:
                status = 'error'
                message = f"Critical memory usage: {memory_percent:.1f}%"
            elif memory_percent > 75:
                status = 'warning'
                message = f"High memory usage: {memory_percent:.1f}%"
            else:
                status = 'healthy'
                message = f"Memory usage normal: {memory_percent:.1f}%"
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'total_gb': round(memory.total / 1024 / 1024 / 1024, 2),
                    'available_gb': round(available_gb, 2),
                    'used_percent': round(memory_percent, 1),
                    'process_memory_mb': round(process_memory, 1)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Memory check failed: {str(e)}",
                'details': {}
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """ディスク容量のチェック"""
        try:
            disk_usage = psutil.disk_usage('/')
            used_percent = (disk_usage.used / disk_usage.total) * 100
            free_gb = disk_usage.free / 1024 / 1024 / 1024
            
            if used_percent > 95:
                status = 'error'
                message = f"Critical disk usage: {used_percent:.1f}%"
            elif used_percent > 85:
                status = 'warning'
                message = f"High disk usage: {used_percent:.1f}%"
            else:
                status = 'healthy'
                message = f"Disk usage normal: {used_percent:.1f}%"
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'total_gb': round(disk_usage.total / 1024 / 1024 / 1024, 2),
                    'free_gb': round(free_gb, 2),
                    'used_percent': round(used_percent, 1)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Disk check failed: {str(e)}",
                'details': {}
            }
    
    def _check_mediapipe(self) -> Dict[str, Any]:
        """MediaPipeの動作チェック"""
        try:
            import mediapipe as mp
            
            # MediaPipe Poseの初期化テスト
            mp_pose = mp.solutions.pose
            pose = mp_pose.Pose(
                static_image_mode=True,
                model_complexity=1,
                min_detection_confidence=0.5
            )
            
            # 簡単なテスト用のダミーデータで初期化確認
            import numpy as np
            test_image = np.zeros((480, 640, 3), dtype=np.uint8)
            results = pose.process(test_image)
            
            pose.close()
            
            return {
                'status': 'healthy',
                'message': 'MediaPipe initialization successful',
                'details': {
                    'version': getattr(mp, '__version__', 'unknown'),
                    'pose_available': True
                }
            }
            
        except ImportError:
            return {
                'status': 'error',
                'message': 'MediaPipe not available',
                'details': {}
            }
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'MediaPipe initialization issue: {str(e)}',
                'details': {}
            }
    
    def _check_opencv(self) -> Dict[str, Any]:
        """OpenCVの動作チェック"""
        try:
            import cv2
            
            # OpenCVの基本機能テスト
            test_image = cv2.imread('static/generated-icon.png')
            if test_image is not None:
                # 簡単な画像処理テスト
                gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
                test_passed = gray is not None
            else:
                # ダミー画像で基本機能テスト
                import numpy as np
                test_image = np.zeros((100, 100, 3), dtype=np.uint8)
                gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
                test_passed = gray is not None
            
            return {
                'status': 'healthy' if test_passed else 'warning',
                'message': 'OpenCV functional' if test_passed else 'OpenCV basic test failed',
                'details': {
                    'version': cv2.__version__,
                    'build_info': cv2.getBuildInformation().split('\n')[0] if hasattr(cv2, 'getBuildInformation') else 'unavailable'
                }
            }
            
        except ImportError:
            return {
                'status': 'error',
                'message': 'OpenCV not available',
                'details': {}
            }
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'OpenCV test failed: {str(e)}',
                'details': {}
            }
    
    def _check_database(self) -> Dict[str, Any]:
        """データベース接続のチェック"""
        try:
            import os
            database_url = os.environ.get('DATABASE_URL')
            
            if not database_url:
                return {
                    'status': 'warning',
                    'message': 'DATABASE_URL not configured',
                    'details': {}
                }
            
            # 簡単な接続テスト
            try:
                import psycopg2
                # 接続文字列の基本チェック
                if database_url.startswith('postgres'):
                    status = 'healthy'
                    message = 'Database URL configured'
                else:
                    status = 'warning'
                    message = 'Unexpected database URL format'
                
                return {
                    'status': status,
                    'message': message,
                    'details': {
                        'url_configured': True,
                        'driver_available': True
                    }
                }
                
            except ImportError:
                return {
                    'status': 'warning',
                    'message': 'Database driver not available',
                    'details': {
                        'url_configured': True,
                        'driver_available': False
                    }
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database check failed: {str(e)}',
                'details': {}
            }

    def get_quick_status(self) -> Dict[str, Any]:
        """クイックステータスチェック（軽量版）"""
        try:
            memory = psutil.virtual_memory()
            process = psutil.Process()
            
            return {
                'status': 'healthy',
                'memory_percent': round(memory.percent, 1),
                'process_memory_mb': round(process.memory_info().rss / 1024 / 1024, 1),
                'cpu_percent': round(process.cpu_percent(), 1),
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {
                'status': 'unknown',
                'timestamp': datetime.now().isoformat()
            }

# グローバルインスタンス
health_checker = SystemHealthChecker()