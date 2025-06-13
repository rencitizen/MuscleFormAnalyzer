-- database/v3_schema.sql
-- TENAX FIT v3.0 データベーススキーマ拡張
-- 既存のテーブルに科学的分析機能を追加

-- ユーザーテーブルに新しいカラムを追加
ALTER TABLE users ADD COLUMN IF NOT EXISTS comprehensive_analysis JSONB;
ALTER TABLE users ADD COLUMN IF NOT EXISTS safety_preferences JSONB DEFAULT '{"max_deficit_percent": 20, "min_rest_days": 1}';
ALTER TABLE users ADD COLUMN IF NOT EXISTS nutrition_goals JSONB;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_v3_analysis_date TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS metabolic_type VARCHAR(50);

-- 科学的計算結果テーブル
CREATE TABLE IF NOT EXISTS scientific_calculations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    calculation_date TIMESTAMP DEFAULT NOW(),
    calculation_type VARCHAR(50) NOT NULL, -- 'bmr', 'tdee', 'body_composition'
    
    -- BMR計算結果
    bmr_mifflin DECIMAL(6,2),
    bmr_harris_benedict DECIMAL(6,2),
    bmr_katch_mcardle DECIMAL(6,2),
    bmr_cunningham DECIMAL(6,2),
    bmr_average DECIMAL(6,2),
    
    -- TDEE計算結果
    tdee DECIMAL(6,2),
    tdee_with_neat DECIMAL(6,2),
    activity_level VARCHAR(20),
    neat_factor DECIMAL(3,2) DEFAULT 1.0,
    
    -- 体組成
    bmi DECIMAL(4,2),
    bmi_category VARCHAR(20),
    estimated_body_fat DECIMAL(4,2),
    lean_body_mass DECIMAL(5,2),
    fat_mass DECIMAL(5,2),
    ffmi DECIMAL(4,2),
    normalized_ffmi DECIMAL(4,2),
    
    -- メタデータ
    input_data JSONB NOT NULL,
    calculation_method JSONB,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_scientific_calc_user_date ON scientific_calculations(user_id, calculation_date DESC);
CREATE INDEX idx_scientific_calc_type ON scientific_calculations(calculation_type);

-- 栄養計画テーブル
CREATE TABLE IF NOT EXISTS nutrition_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan_name VARCHAR(100),
    goal_type VARCHAR(50) NOT NULL, -- 'cutting', 'bulking', 'maintenance', 'recomp'
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- カロリー目標
    target_calories INTEGER NOT NULL,
    calorie_adjustment INTEGER, -- TDEEからの調整値
    
    -- マクロ栄養素（グラム）
    protein_g INTEGER NOT NULL,
    carbs_g INTEGER NOT NULL,
    fats_g INTEGER NOT NULL,
    fiber_g INTEGER,
    sugar_limit_g INTEGER,
    
    -- マクロ比率（％）
    protein_ratio DECIMAL(3,1),
    carbs_ratio DECIMAL(3,1),
    fats_ratio DECIMAL(3,1),
    
    -- タンパク質詳細
    protein_per_kg DECIMAL(3,2),
    protein_timing JSONB, -- 摂取タイミング
    
    -- 微量栄養素推奨
    micronutrient_recommendations JSONB,
    
    -- 食事タイミング
    meal_timing JSONB,
    meal_frequency INTEGER DEFAULT 4,
    
    -- 水分摂取
    daily_water_ml INTEGER,
    
    -- メタデータ
    created_by VARCHAR(50) DEFAULT 'v3_engine',
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_nutrition_plans_user_active ON nutrition_plans(user_id, is_active);
CREATE INDEX idx_nutrition_plans_dates ON nutrition_plans(start_date, end_date);

-- トレーニングプログラムテーブル
CREATE TABLE IF NOT EXISTS training_programs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    program_name VARCHAR(100),
    experience_level VARCHAR(20) NOT NULL, -- 'beginner', 'intermediate', 'advanced'
    goal VARCHAR(50) NOT NULL, -- 'strength', 'hypertrophy', 'endurance', 'general'
    
    -- プログラム構造
    split_type VARCHAR(50), -- 'full_body', 'upper_lower', 'ppl', etc.
    frequency_days INTEGER NOT NULL,
    duration_minutes INTEGER,
    
    -- プログラム詳細
    program_structure JSONB NOT NULL, -- ワークアウトの詳細構造
    exercises JSONB, -- エクササイズリスト
    
    -- プログレッション
    progression_plan JSONB,
    periodization_type VARCHAR(50),
    current_week INTEGER DEFAULT 1,
    total_weeks INTEGER,
    
    -- パラメータ
    training_parameters JSONB, -- sets, reps, rest, intensity
    
    -- 安全ガイドライン
    safety_guidelines JSONB,
    warmup_routine JSONB,
    cooldown_routine JSONB,
    
    -- ステータス
    is_active BOOLEAN DEFAULT TRUE,
    start_date DATE,
    end_date DATE,
    
    -- メタデータ
    equipment_required VARCHAR(50),
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_training_programs_user_active ON training_programs(user_id, is_active);
CREATE INDEX idx_training_programs_level_goal ON training_programs(experience_level, goal);

-- 安全性ログテーブル
CREATE TABLE IF NOT EXISTS safety_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    check_date TIMESTAMP DEFAULT NOW(),
    
    -- リスク評価
    overall_safety VARCHAR(20) NOT NULL, -- 'safe', 'low_risk', 'moderate_risk', 'high_risk'
    risk_score INTEGER,
    
    -- 警告詳細
    warning_type VARCHAR(50) NOT NULL,
    warning_level VARCHAR(20) NOT NULL, -- 'critical', 'danger', 'warning', 'caution'
    message TEXT NOT NULL,
    details JSONB,
    health_risks TEXT[],
    
    -- 推奨事項
    recommendations JSONB,
    immediate_action_required BOOLEAN DEFAULT FALSE,
    
    -- ユーザー対応
    user_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    user_response TEXT,
    
    -- フォローアップ
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_safety_logs_user_date ON safety_logs(user_id, check_date DESC);
CREATE INDEX idx_safety_logs_level ON safety_logs(warning_level);
CREATE INDEX idx_safety_logs_unacknowledged ON safety_logs(user_id, user_acknowledged) WHERE user_acknowledged = FALSE;

-- 進捗追跡テーブル（v3拡張）
CREATE TABLE IF NOT EXISTS progress_tracking_v3 (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    measurement_date DATE NOT NULL,
    
    -- 身体測定
    weight_kg DECIMAL(5,2),
    body_fat_percentage DECIMAL(4,2),
    lean_body_mass_kg DECIMAL(5,2),
    
    -- 詳細測定
    measurements JSONB, -- {waist, chest, arms, thighs, etc.}
    
    -- パフォーマンス指標
    performance_metrics JSONB, -- {squat_1rm, bench_1rm, deadlift_1rm, etc.}
    
    -- 主観的指標（1-10スケール）
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 10),
    mood INTEGER CHECK (mood BETWEEN 1 AND 10),
    soreness_level INTEGER CHECK (soreness_level BETWEEN 1 AND 10),
    hunger_level INTEGER CHECK (hunger_level BETWEEN 1 AND 10),
    
    -- 栄養遵守
    nutrition_adherence INTEGER CHECK (nutrition_adherence BETWEEN 0 AND 100),
    actual_calories INTEGER,
    actual_protein_g INTEGER,
    
    -- トレーニング遵守
    training_adherence INTEGER CHECK (training_adherence BETWEEN 0 AND 100),
    workouts_completed INTEGER,
    workouts_planned INTEGER,
    
    -- 写真
    progress_photos JSONB, -- {front_url, side_url, back_url}
    
    -- ノート
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- インデックス
CREATE UNIQUE INDEX idx_progress_tracking_v3_user_date ON progress_tracking_v3(user_id, measurement_date);
CREATE INDEX idx_progress_tracking_v3_date ON progress_tracking_v3(measurement_date DESC);

-- 分析履歴テーブル
CREATE TABLE IF NOT EXISTS analysis_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    analysis_id VARCHAR(50) UNIQUE NOT NULL,
    analysis_type VARCHAR(50) NOT NULL, -- 'comprehensive', 'body_comp', 'nutrition', etc.
    
    -- 入力データ
    input_profile JSONB NOT NULL,
    
    -- 分析結果
    results JSONB NOT NULL,
    
    -- AI統合
    ai_integrations JSONB, -- {pose_analysis, meal_analysis, phase_detection}
    
    -- メタデータ
    processing_time_ms INTEGER,
    api_version VARCHAR(10) DEFAULT 'v3',
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_analysis_history_user ON analysis_history(user_id, created_at DESC);
CREATE INDEX idx_analysis_history_type ON analysis_history(analysis_type);

-- ビュー：最新の分析サマリー
CREATE OR REPLACE VIEW user_latest_analysis AS
SELECT 
    u.id as user_id,
    u.email,
    u.display_name,
    sc.bmi,
    sc.estimated_body_fat,
    sc.lean_body_mass,
    sc.tdee,
    np.target_calories,
    np.protein_g,
    tp.program_name,
    tp.frequency_days,
    sl.overall_safety as latest_safety_status,
    sl.risk_score as latest_risk_score
FROM users u
LEFT JOIN LATERAL (
    SELECT * FROM scientific_calculations 
    WHERE user_id = u.id 
    ORDER BY calculation_date DESC 
    LIMIT 1
) sc ON true
LEFT JOIN LATERAL (
    SELECT * FROM nutrition_plans 
    WHERE user_id = u.id AND is_active = true 
    ORDER BY created_at DESC 
    LIMIT 1
) np ON true
LEFT JOIN LATERAL (
    SELECT * FROM training_programs 
    WHERE user_id = u.id AND is_active = true 
    ORDER BY created_at DESC 
    LIMIT 1
) tp ON true
LEFT JOIN LATERAL (
    SELECT * FROM safety_logs 
    WHERE user_id = u.id 
    ORDER BY check_date DESC 
    LIMIT 1
) sl ON true;

-- 関数：ユーザーの包括的統計を取得
CREATE OR REPLACE FUNCTION get_user_comprehensive_stats(p_user_id INTEGER)
RETURNS TABLE (
    total_analyses INTEGER,
    average_bmi DECIMAL,
    average_body_fat DECIMAL,
    weight_change_30d DECIMAL,
    body_fat_change_30d DECIMAL,
    training_adherence_30d DECIMAL,
    nutrition_adherence_30d DECIMAL,
    current_risk_level VARCHAR,
    unacknowledged_warnings INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT ah.id)::INTEGER as total_analyses,
        AVG(sc.bmi)::DECIMAL as average_bmi,
        AVG(sc.estimated_body_fat)::DECIMAL as average_body_fat,
        (
            SELECT p2.weight_kg - p1.weight_kg
            FROM progress_tracking_v3 p1, progress_tracking_v3 p2
            WHERE p1.user_id = p_user_id 
            AND p2.user_id = p_user_id
            AND p1.measurement_date = (
                SELECT MIN(measurement_date) 
                FROM progress_tracking_v3 
                WHERE user_id = p_user_id 
                AND measurement_date >= CURRENT_DATE - INTERVAL '30 days'
            )
            AND p2.measurement_date = (
                SELECT MAX(measurement_date) 
                FROM progress_tracking_v3 
                WHERE user_id = p_user_id
            )
        ) as weight_change_30d,
        (
            SELECT p2.body_fat_percentage - p1.body_fat_percentage
            FROM progress_tracking_v3 p1, progress_tracking_v3 p2
            WHERE p1.user_id = p_user_id 
            AND p2.user_id = p_user_id
            AND p1.measurement_date = (
                SELECT MIN(measurement_date) 
                FROM progress_tracking_v3 
                WHERE user_id = p_user_id 
                AND measurement_date >= CURRENT_DATE - INTERVAL '30 days'
            )
            AND p2.measurement_date = (
                SELECT MAX(measurement_date) 
                FROM progress_tracking_v3 
                WHERE user_id = p_user_id
            )
        ) as body_fat_change_30d,
        (
            SELECT AVG(training_adherence)::DECIMAL
            FROM progress_tracking_v3
            WHERE user_id = p_user_id
            AND measurement_date >= CURRENT_DATE - INTERVAL '30 days'
        ) as training_adherence_30d,
        (
            SELECT AVG(nutrition_adherence)::DECIMAL
            FROM progress_tracking_v3
            WHERE user_id = p_user_id
            AND measurement_date >= CURRENT_DATE - INTERVAL '30 days'
        ) as nutrition_adherence_30d,
        (
            SELECT overall_safety
            FROM safety_logs
            WHERE user_id = p_user_id
            ORDER BY check_date DESC
            LIMIT 1
        ) as current_risk_level,
        (
            SELECT COUNT(*)::INTEGER
            FROM safety_logs
            WHERE user_id = p_user_id
            AND user_acknowledged = FALSE
            AND warning_level IN ('critical', 'danger')
        ) as unacknowledged_warnings
    FROM analysis_history ah
    LEFT JOIN scientific_calculations sc ON sc.user_id = ah.user_id
    WHERE ah.user_id = p_user_id
    GROUP BY ah.user_id;
END;
$$ LANGUAGE plpgsql;

-- トリガー：更新日時の自動更新
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_scientific_calculations_updated_at BEFORE UPDATE ON scientific_calculations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nutrition_plans_updated_at BEFORE UPDATE ON nutrition_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_training_programs_updated_at BEFORE UPDATE ON training_programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_progress_tracking_v3_updated_at BEFORE UPDATE ON progress_tracking_v3
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();