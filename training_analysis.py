"""
トレーニングフォーム分析モジュール
動画からトレーニング動作を分析し、フォームの評価と改善点を提供
"""
import os
import cv2
import numpy as np
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
import mediapipe as mp

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MediaPipe設定
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# 理想的なフォームのデータパス
IDEAL_FORMS_PATH = 'ideal_forms/'

class TrainingAnalyzer:
    """トレーニングフォーム分析クラス"""
    
    def __init__(self, exercise_type: str = 'squat'):
        """
        Args:
            exercise_type (str): 分析する種目タイプ ('squat', 'bench_press', 'deadlift', 'overhead_press')
        """
        self.exercise_type = exercise_type
        self.ideal_keypoints = self._load_ideal_keypoints()
        self.joint_angles = {}
        self.movement_path = {}
        self.movement_speed = {}
        self.phase_detection = []
        
    def _load_ideal_keypoints(self) -> Dict[str, Any]:
        """理想的なフォームのキーポイントを読み込む"""
        try:
            # 種目ごとの理想フォームJSONファイルパス
            ideal_file = os.path.join(IDEAL_FORMS_PATH, f"{self.exercise_type}_ideal.json")
            
            # ファイルが存在しない場合はデフォルト値を使用
            if not os.path.exists(ideal_file):
                logger.warning(f"理想フォームファイル {ideal_file} が見つかりません。デフォルト値を使用します。")
                return self._get_default_keypoints()
            
            with open(ideal_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"理想フォームの読み込みに失敗しました: {e}")
            return self._get_default_keypoints()
    
    def _get_default_keypoints(self) -> Dict[str, Any]:
        """デフォルトの理想キーポイントを返す"""
        # 種目ごとのデフォルト値
        defaults = {
            'squat': {
                'knee_angle_bottom': 90.0,  # 最下点での膝の角度
                'hip_angle_bottom': 80.0,   # 最下点での股関節の角度
                'back_angle': 45.0,         # 背中の角度
                'symmetry_threshold': 10.0, # 左右対称性の許容範囲
                'depth_target': 0.4,        # 深さの目標値（高さ比）
            },
            'bench_press': {
                'elbow_angle_bottom': 90.0, # 最下点での肘の角度
                'bar_path_variance': 5.0,   # バーの軌道のばらつき許容範囲
                'wrist_alignment': 5.0,     # 手首のアライメント許容範囲
                'symmetry_threshold': 8.0,  # 左右対称性の許容範囲
            },
            'deadlift': {
                'hip_angle_start': 70.0,    # 開始時の股関節の角度
                'knee_angle_start': 110.0,  # 開始時の膝の角度
                'back_angle': 55.0,         # 背中の角度
                'bar_path': 'vertical',     # バーの軌道パターン
            },
            'overhead_press': {
                'elbow_angle_bottom': 90.0, # 開始時の肘の角度
                'shoulder_alignment': 5.0,  # 肩のアライメント許容範囲
                'head_position': 'neutral', # 頭の位置
                'bar_path': 'vertical',     # バーの軌道パターン
            }
        }
        
        # デフォルト値が存在しない場合はスクワットを使用
        return defaults.get(self.exercise_type, defaults['squat'])
    
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """
        動画を分析してトレーニングフォームを評価
        
        Args:
            video_path (str): 分析する動画のファイルパス
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        if not os.path.exists(video_path):
            logger.error(f"動画ファイル {video_path} が見つかりません")
            return {"error": "動画ファイルが見つかりません"}
        
        try:
            # 現時点ではサンプル分析結果を返す
            # 実際の実装では、ここでMediaPipeを使って姿勢検出し、関節角度などを分析
            return self._generate_sample_analysis()
        except Exception as e:
            logger.error(f"動画分析中にエラーが発生しました: {e}")
            return {"error": f"分析エラー: {str(e)}"}
    
    def _generate_sample_analysis(self) -> Dict[str, Any]:
        """
        サンプル分析結果を生成（デモ用）
        
        Returns:
            Dict[str, Any]: サンプル分析結果
        """
        # BodyScaleの測定結果を読み込む（リアルシステムでは動的に取得）
        body_metrics = self._load_body_metrics()
        
        exercise_scores = {
            'squat': {
                'form_score': 82,
                'depth_score': 75, 
                'balance_score': 90,
                'tempo_score': 85,
                'issues': ['膝が内側に入る傾向がある', '最下点でやや浅い', '背中がやや丸まっている'],
                'strengths': ['安定した姿勢を維持できている', '左右のバランスが良い'],
                'rep_count': 8,
                # 体のサイズに基づいた分析を追加
                'body_metrics': body_metrics,
                'leg_length_analysis': self._analyze_leg_length(body_metrics),
                'arm_length_analysis': self._analyze_arm_length(body_metrics),
                'body_proportion_insights': self._get_proportion_insights(body_metrics)
            },
            'bench_press': {
                'form_score': 78,
                'bar_path_score': 70,
                'elbow_position_score': 85,
                'tempo_score': 80,
                'issues': ['バーの軌道にばらつきがある', '左腕より右腕が早く伸びる', 'アーチがやや弱い'],
                'strengths': ['手首のアライメントが良好', 'テンポが一定している'],
                'rep_count': 6,
                # 体のサイズに基づいた分析を追加
                'body_metrics': body_metrics,
                'arm_length_analysis': self._analyze_arm_length(body_metrics),
                'chest_width_impact': "腕の長さが平均より長いため、バーパスが長くなります。より安定したバーの軌道を意識しましょう。",
                'body_proportion_insights': self._get_proportion_insights(body_metrics)
            },
            'deadlift': {
                'form_score': 75,
                'hip_hinge_score': 80,
                'back_angle_score': 70,
                'bar_path_score': 85,
                'issues': ['背中が丸まりやすい', 'ヒップヒンジが不十分', '頭の位置が下がりがち'],
                'strengths': ['バーの軌道が良好', '最終姿勢が安定している'],
                'rep_count': 5,
                # 体のサイズに基づいた分析を追加
                'body_metrics': body_metrics,
                'leg_length_analysis': self._analyze_leg_length(body_metrics),
                'body_proportion_insights': self._get_proportion_insights(body_metrics)
            },
            'overhead_press': {
                'form_score': 80,
                'bar_path_score': 85,
                'shoulder_alignment_score': 75,
                'stability_score': 80,
                'issues': ['腰が反りがち', '左右の肩の高さが異なる', '体幹の安定性が低下しやすい'],
                'strengths': ['バーの軌道が垂直に近い', '手首の角度が適切'],
                'rep_count': 7,
                # 体のサイズに基づいた分析を追加
                'body_metrics': body_metrics,
                'arm_length_analysis': self._analyze_arm_length(body_metrics),
                'body_proportion_insights': self._get_proportion_insights(body_metrics)
            }
        }
        
        # 種目に応じた分析結果を返す
        return exercise_scores.get(self.exercise_type, exercise_scores['squat'])
        
    def _load_body_metrics(self) -> Dict[str, Any]:
        """
        BodyScaleの測定結果を読み込む
        実際のシステムでは動的に取得するが、デモ用にサンプルデータを使用
        
        Returns:
            Dict[str, Any]: 身体計測のメトリクス
        """
        try:
            # サンプルデータファイルからメトリクスを読み込む
            with open('results/sample_metrics.json', 'r', encoding='utf-8') as f:
                metrics = json.load(f)
                
            # 必要なデータだけを抽出
            return {
                'user_height_cm': metrics.get('user_height_cm', 170.0),
                'left_arm_cm': metrics.get('left_arm_cm', 61.4),
                'right_arm_cm': metrics.get('right_arm_cm', 60.9),
                'left_leg_cm': metrics.get('left_leg_cm', 91.2),
                'right_leg_cm': metrics.get('right_leg_cm', 90.8),
                'arm_length_ratio': (metrics.get('left_arm_cm', 61.4) + metrics.get('right_arm_cm', 60.9)) / (2 * metrics.get('user_height_cm', 170.0)),
                'leg_length_ratio': (metrics.get('left_leg_cm', 91.2) + metrics.get('right_leg_cm', 90.8)) / (2 * metrics.get('user_height_cm', 170.0)),
                'arm_symmetry': abs(metrics.get('left_arm_cm', 61.4) - metrics.get('right_arm_cm', 60.9)),
                'leg_symmetry': abs(metrics.get('left_leg_cm', 91.2) - metrics.get('right_leg_cm', 90.8))
            }
        except Exception as e:
            logger.error(f"身体メトリクスの読み込みに失敗: {e}")
            # デフォルト値を返す
            return {
                'user_height_cm': 170.0,
                'left_arm_cm': 61.4,
                'right_arm_cm': 60.9,
                'left_leg_cm': 91.2,
                'right_leg_cm': 90.8,
                'arm_length_ratio': 0.36,  # 平均的な値
                'leg_length_ratio': 0.54,  # 平均的な値
                'arm_symmetry': 0.5,
                'leg_symmetry': 0.4
            }
            
    def _analyze_leg_length(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """
        脚の長さに基づく分析
        
        Args:
            metrics (Dict[str, Any]): 身体メトリクス
            
        Returns:
            Dict[str, str]: 脚の長さに関する分析結果
        """
        avg_leg_length = (metrics['left_leg_cm'] + metrics['right_leg_cm']) / 2
        leg_ratio = metrics['leg_length_ratio']
        
        result = {}
        
        # 脚の長さの分析
        if leg_ratio > 0.56:  # 脚が長い
            if self.exercise_type == 'squat':
                result['form_adjustment'] = "脚が比較的長いため、足幅を少し広めにして安定性を確保してください。"
                result['depth_advice'] = "脚長が長いため、完全な深さでのスクワットには柔軟性が必要です。足関節と股関節の柔軟性を高めるストレッチを取り入れましょう。"
            elif self.exercise_type == 'deadlift':
                result['form_adjustment'] = "脚が比較的長いため、スモウスタンスやセミスモウスタンスが適している可能性があります。"
        elif leg_ratio < 0.52:  # 脚が短い
            if self.exercise_type == 'squat':
                result['form_adjustment'] = "脚が比較的短いため、標準的な足幅でのスクワットが適しています。"
                result['depth_advice'] = "脚長が短いため、深いスクワットが比較的容易にできるはずです。正しいフォームで深さを追求しましょう。"
            elif self.exercise_type == 'deadlift':
                result['form_adjustment'] = "脚が比較的短いため、コンベンショナルスタンスが適しています。"
        else:  # 平均的な脚の長さ
            result['form_adjustment'] = "体のプロポーションがバランス良く、標準的なフォームが適しています。"
            
        # 左右差の分析
        leg_asymmetry = metrics['leg_symmetry']
        if leg_asymmetry > 1.0:
            result['symmetry_issue'] = f"左右の脚の長さに{leg_asymmetry:.1f}cmの差があります。左右均等に体重をかけることを意識してください。"
            
        return result
        
    def _analyze_arm_length(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """
        腕の長さに基づく分析
        
        Args:
            metrics (Dict[str, Any]): 身体メトリクス
            
        Returns:
            Dict[str, str]: 腕の長さに関する分析結果
        """
        avg_arm_length = (metrics['left_arm_cm'] + metrics['right_arm_cm']) / 2
        arm_ratio = metrics['arm_length_ratio']
        
        result = {}
        
        # 腕の長さの分析
        if arm_ratio > 0.38:  # 腕が長い
            if self.exercise_type == 'bench_press':
                result['grip_width'] = "腕が比較的長いため、やや広めのグリップ幅が適しています。"
                result['rom_advice'] = "腕が長いため、可動域が大きくなります。肩の柔軟性を維持し、肩関節の安定性を高める補助エクササイズを取り入れましょう。"
            elif self.exercise_type == 'overhead_press':
                result['form_adjustment'] = "腕が比較的長いため、胸を張り、肘の位置に特に注意してください。"
        elif arm_ratio < 0.34:  # 腕が短い
            if self.exercise_type == 'bench_press':
                result['grip_width'] = "腕が比較的短いため、標準的な肩幅のグリップが適しています。"
                result['rom_advice'] = "腕が短いため、可動域が小さくなります。胸の筋肉をより効果的に使うため、肩甲骨を引き寄せることを意識しましょう。"
            elif self.exercise_type == 'overhead_press':
                result['form_adjustment'] = "腕が比較的短いため、より垂直なバーパスを維持しやすいでしょう。"
        else:  # 平均的な腕の長さ
            result['form_adjustment'] = "腕の長さがバランス良く、標準的なフォームが適しています。"
            
        # 左右差の分析
        arm_asymmetry = metrics['arm_symmetry']
        if arm_asymmetry > 0.8:
            result['symmetry_issue'] = f"左右の腕の長さに{arm_asymmetry:.1f}cmの差があります。バランスよく力を入れることを意識してください。"
            
        return result
        
    def _get_proportion_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """
        体のプロポーションに基づく総合的な洞察
        
        Args:
            metrics (Dict[str, Any]): 身体メトリクス
            
        Returns:
            List[str]: プロポーションに基づく洞察のリスト
        """
        insights = []
        
        # 腕と脚のバランス
        arm_leg_ratio = metrics['arm_length_ratio'] / metrics['leg_length_ratio']
        
        if arm_leg_ratio > 0.72:  # 腕が脚に対して長い
            insights.append("腕の長さが脚に対して比較的長いプロポーションです。")
            if self.exercise_type in ['squat', 'deadlift']:
                insights.append("スクワットやデッドリフトでは、背中をまっすぐに保つことに特に注意してください。")
        elif arm_leg_ratio < 0.64:  # 腕が脚に対して短い
            insights.append("腕の長さが脚に対して比較的短いプロポーションです。")
            if self.exercise_type in ['bench_press', 'overhead_press']:
                insights.append("プレス系の種目では、肩関節の安定性を確保するために肩甲骨の位置に注意してください。")
                
        # 左右対称性
        if metrics['arm_symmetry'] > 0.8 or metrics['leg_symmetry'] > 1.0:
            insights.append("左右の腕や脚に若干の非対称性があります。片側ずつのトレーニングで左右のバランスを整えることを検討してください。")
            
        # 身長に対する腕や脚の比率からの洞察
        if metrics['leg_length_ratio'] > 0.56:
            insights.append("脚長が身長に対して長めのため、筋肉発達のポテンシャルが高いと考えられます。特に下半身のトレーニングで効果を発揮できるでしょう。")
        
        # 競技種目に対する体型の適性
        if metrics['leg_length_ratio'] > 0.56 and metrics['arm_length_ratio'] < 0.34:
            insights.append("このプロポーションは走行系の競技（短距離走など）に適している可能性があります。")
        elif metrics['arm_length_ratio'] > 0.38 and metrics['leg_length_ratio'] > 0.54:
            insights.append("このプロポーションは水泳などの競技に適している可能性があります。")
        elif metrics['leg_length_ratio'] < 0.52 and metrics['arm_length_ratio'] > 0.36:
            insights.append("このプロポーションはパワーリフティングなどの競技に適している可能性があります。")
            
        # デフォルトの洞察
        if not insights:
            insights.append("体のプロポーションはバランスが取れています。多様なトレーニング方法に適応できるでしょう。")
            
        return insights
    
    def detect_exercise_type(self, video_path: str) -> str:
        """
        動画から種目タイプを自動検出（将来的な機能）
        
        Args:
            video_path (str): 分析する動画のファイルパス
            
        Returns:
            str: 検出された種目タイプ
        """
        # 現段階ではデフォルト値を返す
        # 実際の実装では、フレームからのポーズ検出と動作パターン認識をここで行う
        return self.exercise_type
    
    def generate_improvement_advice(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        分析結果から改善アドバイスを生成
        
        Args:
            analysis_results (Dict[str, Any]): 分析結果
            
        Returns:
            List[str]: 改善アドバイスのリスト
        """
        advice = []
        
        # 種目ごとのアドバイス生成ロジック
        if self.exercise_type == 'squat':
            if 'issues' in analysis_results:
                for issue in analysis_results['issues']:
                    if '膝が内側' in issue:
                        advice.append('スクワット時は膝を足の方向に向け、内側に入らないよう意識してください。足幅を少し広げるとよいでしょう。')
                    if '浅い' in issue:
                        advice.append('より深く沈み込むようにしましょう。理想的には太ももが床と平行になるまで下げることを目標にしてください。')
                    if '背中が丸' in issue:
                        advice.append('背中が丸まると怪我のリスクが高まります。胸を張り、腹筋に力を入れて背中をまっすぐに保ちましょう。')
        
        elif self.exercise_type == 'bench_press':
            if 'issues' in analysis_results:
                for issue in analysis_results['issues']:
                    if 'バーの軌道' in issue:
                        advice.append('バーの軌道を一定に保つため、天井の一点を見つめながら、胸の同じ位置にバーが触れるよう意識してください。')
                    if '左腕より右腕' in issue or '右腕より左腕' in issue:
                        advice.append('左右の腕の動きを均等にするために、軽いウェイトでフォームを修正する練習をしましょう。')
                    if 'アーチ' in issue:
                        advice.append('適度な背中のアーチは胸の筋肉の活性化に効果的です。肩甲骨を寄せて、軽いアーチを作りましょう。')
        
        elif self.exercise_type == 'deadlift':
            if 'issues' in analysis_results:
                for issue in analysis_results['issues']:
                    if '背中が丸' in issue:
                        advice.append('デッドリフトでは背中をまっすぐに保つことが非常に重要です。腹筋に力を入れ、チェストアップを意識してください。')
                    if 'ヒップヒンジ' in issue:
                        advice.append('効果的なヒップヒンジのために、お尻を後ろに引くイメージで動作を始めましょう。膝の曲げ具合よりも股関節の動きを優先してください。')
        
        elif self.exercise_type == 'overhead_press':
            if 'issues' in analysis_results:
                for issue in analysis_results['issues']:
                    if '腰が反り' in issue:
                        advice.append('オーバーヘッドプレス時に腰が反ると腰に負担がかかります。腹筋に力を入れ、骨盤を少し前傾させて腰の反りを抑えましょう。')
                    if '肩の高さ' in issue:
                        advice.append('左右の肩の高さを揃えるために、バランスボードでの片腕ダンベルプレスなど、片側ずつのトレーニングを取り入れましょう。')
        
        # 共通アドバイス
        if not advice:
            advice.append('全体的なフォームは良好です。継続して現在のフォームを維持しながら、徐々に重量を増やしていきましょう。')
        
        # テンポに関するアドバイス
        tempo_score = analysis_results.get('tempo_score', 0)
        if tempo_score < 80:
            advice.append('動作のテンポが一定でないようです。上げる時と下げる時の速度を意識して、安定したリズムを保つよう心がけましょう。')
        
        return advice
    
    def save_analysis_results(self, results: Dict[str, Any], filename: str = 'training_analysis.json') -> str:
        """
        分析結果をJSONファイルに保存
        
        Args:
            results (Dict[str, Any]): 分析結果
            filename (str): 保存先ファイル名
            
        Returns:
            str: 保存したファイルのパス
        """
        # 結果ディレクトリの存在確認
        os.makedirs('results', exist_ok=True)
        
        # フルパスの生成
        filepath = os.path.join('results', filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"分析結果を {filepath} に保存しました")
            return filepath
        
        except Exception as e:
            logger.error(f"分析結果の保存に失敗しました: {e}")
            return ""