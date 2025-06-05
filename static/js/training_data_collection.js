/**
 * トレーニングデータ収集JavaScript
 * リアルタイムでポーズデータを収集し、サーバーに送信
 */

class TrainingDataCollectionManager {
    constructor() {
        this.isCollecting = false;
        this.currentExercise = null;
        this.sessionData = [];
        this.metadata = {
            height: null,
            weight: null,
            experience: 'beginner'
        };
        this.performanceData = {
            weight: 0,
            reps: 0,
            form_score: 0
        };
        
        this.consentGiven = false;
        this.checkConsentStatus();
    }
    
    /**
     * ユーザーの同意状況を確認
     */
    async checkConsentStatus() {
        try {
            const response = await fetch('/api/data_consent/status');
            const data = await response.json();
            
            this.consentGiven = data.can_collect || false;
            
            if (!this.consentGiven && data.needs_consent) {
                this.showConsentPrompt();
            }
            
            return this.consentGiven;
        } catch (error) {
            console.error('同意状況確認エラー:', error);
            return false;
        }
    }
    
    /**
     * 同意プロンプトを表示
     */
    showConsentPrompt() {
        const prompt = document.createElement('div');
        prompt.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1rem;
        `;
        
        prompt.innerHTML = `
            <div style="
                background: white;
                border-radius: 1rem;
                padding: 2rem;
                max-width: 500px;
                text-align: center;
            ">
                <h3 style="margin-bottom: 1rem; color: #001130;">
                    AI学習への協力をお願いします
                </h3>
                <p style="margin-bottom: 1.5rem; color: #666; line-height: 1.6;">
                    より正確なフォーム分析のため、匿名化されたトレーニングデータの
                    提供にご協力いただけませんか？
                </p>
                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <button onclick="this.closest('div').parentElement.remove()" 
                            style="padding: 0.75rem 1.5rem; border: 2px solid #ddd; background: white; border-radius: 0.5rem; cursor: pointer;">
                        後で決める
                    </button>
                    <button onclick="window.location.href='/data_consent'" 
                            style="padding: 0.75rem 1.5rem; background: #001130; color: white; border: none; border-radius: 0.5rem; cursor: pointer;">
                        詳細を確認
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(prompt);
        
        // 3秒後に自動で閉じる
        setTimeout(() => {
            if (document.body.contains(prompt)) {
                prompt.remove();
            }
        }, 10000);
    }
    
    /**
     * メタデータを設定
     */
    setMetadata(height, weight, experience) {
        this.metadata = {
            height: parseFloat(height),
            weight: parseFloat(weight),
            experience: experience
        };
    }
    
    /**
     * パフォーマンスデータを設定
     */
    setPerformanceData(weight, reps, formScore) {
        this.performanceData = {
            weight: parseFloat(weight),
            reps: parseInt(reps),
            form_score: parseFloat(formScore)
        };
    }
    
    /**
     * データ収集を開始
     */
    startCollection(exercise) {
        if (!this.consentGiven) {
            console.log('データ収集の同意が得られていません');
            return false;
        }
        
        this.currentExercise = exercise;
        this.isCollecting = true;
        this.sessionData = [];
        
        console.log(`データ収集開始: ${exercise}`);
        return true;
    }
    
    /**
     * データ収集を停止
     */
    stopCollection() {
        this.isCollecting = false;
        console.log('データ収集停止');
        
        if (this.sessionData.length > 0) {
            this.sendCollectedData();
        }
    }
    
    /**
     * ポーズデータを収集
     */
    collectPoseData(landmarks) {
        if (!this.isCollecting || !this.consentGiven) {
            return;
        }
        
        // MediaPipeのランドマーク形式を配列に変換
        const poseDataArray = this.convertLandmarksToArray(landmarks);
        
        if (poseDataArray && poseDataArray.length === 33) {
            this.sessionData.push({
                timestamp: Date.now(),
                pose_data: poseDataArray
            });
            
            // 最大500フレームまで保存（メモリ制限）
            if (this.sessionData.length > 500) {
                this.sessionData.shift();
            }
        }
    }
    
    /**
     * MediaPipeランドマークを配列形式に変換
     */
    convertLandmarksToArray(landmarks) {
        const poseArray = [];
        
        try {
            // MediaPipeの33個のランドマークポイント
            const landmarkNames = [
                'NOSE', 'LEFT_EYE_INNER', 'LEFT_EYE', 'LEFT_EYE_OUTER',
                'RIGHT_EYE_INNER', 'RIGHT_EYE', 'RIGHT_EYE_OUTER',
                'LEFT_EAR', 'RIGHT_EAR', 'MOUTH_LEFT', 'MOUTH_RIGHT',
                'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 'RIGHT_ELBOW',
                'LEFT_WRIST', 'RIGHT_WRIST', 'LEFT_PINKY', 'RIGHT_PINKY',
                'LEFT_INDEX', 'RIGHT_INDEX', 'LEFT_THUMB', 'RIGHT_THUMB',
                'LEFT_HIP', 'RIGHT_HIP', 'LEFT_KNEE', 'RIGHT_KNEE',
                'LEFT_ANKLE', 'RIGHT_ANKLE', 'LEFT_HEEL', 'RIGHT_HEEL',
                'LEFT_FOOT_INDEX', 'RIGHT_FOOT_INDEX'
            ];
            
            for (let i = 0; i < 33; i++) {
                if (landmarks && landmarks[i]) {
                    poseArray.push([
                        landmarks[i].x || 0,
                        landmarks[i].y || 0,
                        landmarks[i].z || 0,
                        landmarks[i].visibility || 0
                    ]);
                } else {
                    // データが不足している場合はデフォルト値
                    poseArray.push([0, 0, 0, 0]);
                }
            }
            
        } catch (error) {
            console.error('ランドマーク変換エラー:', error);
            return null;
        }
        
        return poseArray;
    }
    
    /**
     * 収集データをサーバーに送信
     */
    async sendCollectedData() {
        if (!this.consentGiven || this.sessionData.length === 0) {
            return;
        }
        
        try {
            // 代表的なフレームを選択（データサイズ削減）
            const selectedFrames = this.selectRepresentativeFrames(this.sessionData, 10);
            
            for (const frame of selectedFrames) {
                const payload = {
                    exercise: this.currentExercise,
                    pose_data: frame.pose_data,
                    metadata: this.metadata,
                    performance: this.performanceData
                };
                
                const response = await fetch('/api/training_data/collect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                const result = await response.json();
                
                if (!result.success) {
                    console.error('データ送信エラー:', result.error);
                }
            }
            
            console.log(`${selectedFrames.length}フレームのデータを送信しました`);
            
        } catch (error) {
            console.error('データ送信エラー:', error);
        }
    }
    
    /**
     * 代表的なフレームを選択
     */
    selectRepresentativeFrames(sessionData, maxFrames) {
        if (sessionData.length <= maxFrames) {
            return sessionData;
        }
        
        const step = Math.floor(sessionData.length / maxFrames);
        const selected = [];
        
        for (let i = 0; i < sessionData.length; i += step) {
            if (selected.length < maxFrames) {
                selected.push(sessionData[i]);
            }
        }
        
        return selected;
    }
    
    /**
     * 収集状況を取得
     */
    getCollectionStatus() {
        return {
            isCollecting: this.isCollecting,
            consentGiven: this.consentGiven,
            currentExercise: this.currentExercise,
            sessionDataCount: this.sessionData.length
        };
    }
}

// グローバルインスタンス
window.trainingDataCollector = new TrainingDataCollectionManager();

// エクスポート（ES6モジュール対応）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TrainingDataCollectionManager;
}

/**
 * 使用例:
 * 
 * // メタデータ設定
 * trainingDataCollector.setMetadata(170, 70, 'intermediate');
 * 
 * // 収集開始
 * trainingDataCollector.startCollection('squat');
 * 
 * // ポーズデータ収集（フレームごとに呼び出し）
 * trainingDataCollector.collectPoseData(landmarksData);
 * 
 * // パフォーマンス設定
 * trainingDataCollector.setPerformanceData(60, 10, 0.85);
 * 
 * // 収集停止・送信
 * trainingDataCollector.stopCollection();
 */