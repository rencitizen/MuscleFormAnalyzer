// TENAX FIT v3.0 - Pose Analysis Web Worker

// 角度計算関数
function calculateAngle(a, b, c) {
  const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
  let angle = Math.abs(radians * 180.0 / Math.PI);
  if (angle > 180.0) {
    angle = 360 - angle;
  }
  return angle;
}

// 距離計算関数
function calculateDistance(a, b) {
  return Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2));
}

// フォーム分析関数
function analyzeForm(landmarks, worldLandmarks) {
  const issues = [];
  const suggestions = [];
  let formScore = 100;

  // キーポイントの取得
  const points = {
    nose: landmarks[0],
    leftShoulder: landmarks[11],
    rightShoulder: landmarks[12],
    leftElbow: landmarks[13],
    rightElbow: landmarks[14],
    leftWrist: landmarks[15],
    rightWrist: landmarks[16],
    leftHip: landmarks[23],
    rightHip: landmarks[24],
    leftKnee: landmarks[25],
    rightKnee: landmarks[26],
    leftAnkle: landmarks[27],
    rightAnkle: landmarks[28]
  };

  // 1. 肩の水平バランスチェック
  const shoulderDiff = Math.abs(points.leftShoulder.y - points.rightShoulder.y);
  if (shoulderDiff > 0.05) {
    issues.push('肩の高さが不均等です');
    suggestions.push('両肩を同じ高さに保ちましょう');
    formScore -= 10;
  }

  // 2. 腰の水平バランスチェック
  const hipDiff = Math.abs(points.leftHip.y - points.rightHip.y);
  if (hipDiff > 0.05) {
    issues.push('腰の高さが不均等です');
    suggestions.push('骨盤を水平に保ちましょう');
    formScore -= 10;
  }

  // 3. 姿勢の垂直性チェック
  const midShoulder = {
    x: (points.leftShoulder.x + points.rightShoulder.x) / 2,
    y: (points.leftShoulder.y + points.rightShoulder.y) / 2
  };
  const midHip = {
    x: (points.leftHip.x + points.rightHip.x) / 2,
    y: (points.leftHip.y + points.rightHip.y) / 2
  };
  
  const postureDiff = Math.abs(midShoulder.x - midHip.x);
  if (postureDiff > 0.1) {
    issues.push('上体が前後に傾いています');
    suggestions.push('背筋を真っ直ぐに保ちましょう');
    formScore -= 15;
  }

  // 4. 膝の角度チェック（スクワットなどの場合）
  if (worldLandmarks) {
    const leftKneeAngle = calculateAngle(
      worldLandmarks[23], // 左腰
      worldLandmarks[25], // 左膝
      worldLandmarks[27]  // 左足首
    );
    const rightKneeAngle = calculateAngle(
      worldLandmarks[24], // 右腰
      worldLandmarks[26], // 右膝
      worldLandmarks[28]  // 右足首
    );

    // スクワットの深さチェック
    if (leftKneeAngle < 90 || rightKneeAngle < 90) {
      issues.push('膝が深く曲がりすぎています');
      suggestions.push('膝の角度を90度以上に保ちましょう');
      formScore -= 20;
    }

    // 左右の膝角度の差
    const kneeAngleDiff = Math.abs(leftKneeAngle - rightKneeAngle);
    if (kneeAngleDiff > 10) {
      issues.push('左右の膝の角度が異なります');
      suggestions.push('両膝を同じ角度で曲げましょう');
      formScore -= 15;
    }
  }

  // 5. 腕の位置チェック
  const armSpread = calculateDistance(points.leftWrist, points.rightWrist);
  const shoulderWidth = calculateDistance(points.leftShoulder, points.rightShoulder);
  
  if (armSpread < shoulderWidth * 0.8) {
    issues.push('腕の幅が狭すぎます');
    suggestions.push('腕を肩幅程度に開きましょう');
    formScore -= 10;
  } else if (armSpread > shoulderWidth * 2.5) {
    issues.push('腕の幅が広すぎます');
    suggestions.push('腕の幅を適切に調整しましょう');
    formScore -= 10;
  }

  // 6. 頭部の位置チェック
  const headAlignment = Math.abs(points.nose.x - midShoulder.x);
  if (headAlignment > 0.1) {
    issues.push('頭が左右に傾いています');
    suggestions.push('頭を中央に保ちましょう');
    formScore -= 5;
  }

  return {
    formScore: Math.max(0, formScore),
    issues,
    suggestions,
    metrics: {
      shoulderBalance: 100 - (shoulderDiff * 1000),
      hipBalance: 100 - (hipDiff * 1000),
      posture: 100 - (postureDiff * 500),
      symmetry: 100 - (kneeAngleDiff || 0)
    }
  };
}

// メッセージハンドラー
self.addEventListener('message', (event) => {
  const { type, landmarks, worldLandmarks } = event.data;

  if (type === 'analyze') {
    try {
      const analysis = analyzeForm(landmarks, worldLandmarks);
      self.postMessage(analysis);
    } catch (error) {
      self.postMessage({
        error: 'Analysis failed',
        message: error.message
      });
    }
  }
});