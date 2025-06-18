# Worker3（品質管理・テスト）Phase 1タスク割り当て

## 担当: 品質管理・テスト担当者（Worker3）
## フェーズ: Phase 1 - 基盤機能品質保証

### 1. 既存システム品質状態分析（優先度: 最高）
- [ ] 既存のテストカバレッジ確認（frontend/tests, tests/ディレクトリ）
- [ ] 現在のパフォーマンスベンチマーク測定
- [ ] 既存の品質問題・技術的負債の洗い出し
- [ ] CI/CDパイプラインの確認

### 2. 科学的計算精度検証テスト（優先度: 最高）
**実装場所**: `tests/unit/test_scientific_calculations.py`

```python
import pytest
from core.scientific_calculations import ScientificCalculationEngine

class TestBMRCalculation:
    def test_bmr_male_accuracy(self):
        """男性BMR計算の精度検証"""
        # テストケース: 25歳男性, 70kg, 170cm
        # 期待値: (10 × 70) + (6.25 × 170) - (5 × 25) + 5 = 1642.5 kcal
        result = ScientificCalculationEngine.calculate_bmr(70, 170, 25, "male")
        assert result == 1642.5
    
    def test_bmr_female_accuracy(self):
        """女性BMR計算の精度検証"""
        # テストケース: 25歳女性, 55kg, 160cm
        # 期待値: (10 × 55) + (6.25 × 160) - (5 × 25) - 161 = 1264 kcal
        result = ScientificCalculationEngine.calculate_bmr(55, 160, 25, "female")
        assert result == 1264
    
    def test_bmr_edge_cases(self):
        """エッジケースのテスト"""
        # 極端な値でのテスト
        pass

class TestTDEECalculation:
    def test_activity_coefficients(self):
        """活動レベル係数の正確性"""
        bmr = 1642.5
        coefficients = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        for level, coef in coefficients.items():
            result = ScientificCalculationEngine.calculate_tdee(bmr, level)
            assert result == pytest.approx(bmr * coef, rel=1e-9)

class TestBodyFatEstimation:
    def test_tanita_formula_accuracy(self):
        """タニタ式体脂肪率推定の精度"""
        # 体脂肪率 = 1.2 × BMI + 0.23 × 年齢 - 10.8 × 性別係数 - 5.4
        # BMI = 体重(kg) / (身長(m))²
        pass
```

### 3. 安全性チェック機能テスト（優先度: 最高）
**実装場所**: `tests/unit/test_safety_checks.py`

```python
class TestSafetyChecks:
    def test_extreme_calorie_restriction_warning(self):
        """極端なカロリー制限への警告"""
        bmr = 1642.5
        dangerous_calories = 800  # BMRの48%
        result = check_calorie_safety(bmr, dangerous_calories)
        assert "危険" in result.warnings[0]
        assert result.severity == "high"
    
    def test_body_fat_goal_safety(self):
        """体脂肪率目標の健康性チェック"""
        # 女性の体脂肪率8%は危険
        result = check_body_fat_goals(8, "female")
        assert "健康リスク" in result.warnings[0]
        
        # 男性の体脂肪率5%は危険
        result = check_body_fat_goals(5, "male")
        assert "健康リスク" in result.warnings[0]
```

### 4. API統合テスト（優先度: 高）
**実装場所**: `tests/integration/test_v3_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

class TestCalculationAPI:
    def test_bmr_endpoint(self):
        """BMR計算エンドポイントのテスト"""
        response = client.post("/api/v3/calculations/bmr", json={
            "weight": 70,
            "height": 170,
            "age": 25,
            "gender": "male"
        })
        assert response.status_code == 200
        assert response.json()["bmr"] == 1642.5
    
    def test_calculation_chain(self):
        """計算チェーン全体のテスト"""
        # BMR → TDEE → 目標カロリー
        pass
```

### 5. パフォーマンステスト（優先度: 高）
**実装場所**: `tests/performance/test_calculation_performance.py`

```python
import time
import pytest

class TestPerformanceRequirements:
    def test_calculation_response_time(self):
        """計算APIレスポンス時間 <200ms"""
        start_time = time.time()
        # API呼び出し
        response = client.post("/api/v3/calculations/bmr", json=test_data)
        duration = (time.time() - start_time) * 1000
        assert duration < 200
    
    def test_concurrent_requests(self):
        """同時リクエスト処理能力"""
        # 100 req/sのテスト
        pass
```

### 6. 既存機能回帰テスト（優先度: 高）
**実装場所**: `tests/regression/test_existing_features.py`

```python
class TestExistingFeatures:
    def test_mediapipe_integration_unchanged(self):
        """MediaPipe姿勢推定が影響を受けていないことを確認"""
        pass
    
    def test_meal_analysis_functionality(self):
        """食事分析機能が正常動作することを確認"""
        pass
```

### 7. E2Eテストシナリオ（優先度: 中）
**実装場所**: `tests/e2e/test_user_journey.py`

```python
class TestUserJourney:
    def test_new_user_onboarding(self):
        """新規ユーザーのオンボーディングフロー"""
        # 1. プロフィール設定
        # 2. 科学計算結果の表示
        # 3. 安全性警告の確認
        pass
```

### 8. テストデータ管理
**実装場所**: `tests/fixtures/scientific_test_data.py`

```python
# 医学的に検証されたテストケース
TEST_CASES = [
    {
        "description": "平均的な成人男性",
        "input": {"weight": 70, "height": 170, "age": 30, "gender": "male"},
        "expected_bmr": 1605.0,
        "source": "Mifflin-St Jeor論文"
    },
    # 他のテストケース
]
```

### 品質ゲート定義
```yaml
quality_gates:
  calculation_accuracy: 100%  # 科学計算の精度
  test_coverage: 
    unit: 90%
    integration: 80%
  performance:
    api_response: <200ms
    ai_processing: <5s
  regression: 0 errors
```

### テストレポート要件
- 計算精度検証結果（誤差率0%）
- カバレッジレポート
- パフォーマンステスト結果
- 回帰テスト結果
- セキュリティスキャン結果

### 実装順序
1. 既存システムの品質ベースライン確立
2. 科学計算精度テストの実装
3. 安全性チェックテストの実装
4. API統合テストの実装
5. パフォーマンステストの実装
6. 回帰テストスイートの実行

### 成果物
- テストスイート実装
- 品質メトリクスレポート
- パフォーマンスベンチマーク結果
- 問題点と改善提案のリスト

科学的計算の正確性を最優先に品質管理を行ってください。