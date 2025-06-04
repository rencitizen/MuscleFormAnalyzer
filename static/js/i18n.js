/**
 * Tenax Fit 多言語対応システム
 * 日本語・英語の2言語サポート
 */

class I18nManager {
    constructor() {
        this.currentLanguage = this.detectLanguage();
        this.translations = {};
        this.loadTranslations();
    }

    // ブラウザ言語自動検出
    detectLanguage() {
        const saved = localStorage.getItem('bodyscale_language');
        if (saved) return saved;
        
        const browserLang = navigator.language.split('-')[0];
        return ['ja', 'en'].includes(browserLang) ? browserLang : 'ja';
    }

    // 翻訳データ読み込み
    loadTranslations() {
        this.translations = {
            ja: {
                // ナビゲーション
                home: 'ホーム',
                dashboard: 'ダッシュボード',
                training_analysis: 'フォーム分析',
                body_measurement: '身体測定',
                training_records: 'トレーニング記録',
                settings: '設定',

                // ボタン
                save: '保存',
                cancel: 'キャンセル',
                delete: '削除',
                export: 'エクスポート',
                upload: 'アップロード',
                add_record: '記録を追加',
                analyze: '分析開始',
                
                // フォーム
                height: '身長',
                weight: '体重',
                age: '年齢',
                exercise: '種目',
                weight_kg: '重量(kg)',
                reps: '回数',
                sets: 'セット数',
                date: '日付',
                notes: 'メモ',
                
                // 分析
                form_analysis: 'フォーム分析',
                ideal_form: '理想フォーム',
                current_form: '現在のフォーム',
                improvement_points: '改善点',
                good_points: '良い点',
                recommendations: '推奨事項',
                
                // ダッシュボード
                training_days: 'トレーニング日数',
                total_volume: '総ボリューム',
                recorded_exercises: '記録した種目数',
                top_exercise: '最頻種目',
                progress_chart: '進捗グラフ',
                training_calendar: 'トレーニングカレンダー',
                popular_exercises: '人気種目',
                
                // 設定
                language_settings: '言語設定',
                personal_info: '個人情報',
                account_settings: 'アカウント設定',
                app_settings: 'アプリ設定',
                data_management: 'データ管理',
                auto_detect: '自動検出',
                change_password: 'パスワード変更',
                export_data: 'データエクスポート',
                delete_account: 'アカウント削除',
                
                // メッセージ
                success_save: '保存が完了しました',
                error_occurred: 'エラーが発生しました',
                confirm_delete: '本当に削除しますか？',
                data_exported: 'データをエクスポートしました',
                language_changed: '言語が変更されました'
            },
            
            en: {
                // Navigation
                home: 'Home',
                dashboard: 'Dashboard',
                training_analysis: 'Form Analysis',
                body_measurement: 'Body Measurement',
                training_records: 'Training Records',
                settings: 'Settings',

                // Buttons
                save: 'Save',
                cancel: 'Cancel',
                delete: 'Delete',
                export: 'Export',
                upload: 'Upload',
                add_record: 'Add Record',
                analyze: 'Start Analysis',
                
                // Forms
                height: 'Height',
                weight: 'Weight',
                age: 'Age',
                exercise: 'Exercise',
                weight_kg: 'Weight(kg)',
                reps: 'Reps',
                sets: 'Sets',
                date: 'Date',
                notes: 'Notes',
                
                // Analysis
                form_analysis: 'Form Analysis',
                ideal_form: 'Ideal Form',
                current_form: 'Current Form',
                improvement_points: 'Improvement Points',
                good_points: 'Good Points',
                recommendations: 'Recommendations',
                
                // Dashboard
                training_days: 'Training Days',
                total_volume: 'Total Volume',
                recorded_exercises: 'Recorded Exercises',
                top_exercise: 'Top Exercise',
                progress_chart: 'Progress Chart',
                training_calendar: 'Training Calendar',
                popular_exercises: 'Popular Exercises',
                
                // Settings
                language_settings: 'Language Settings',
                personal_info: 'Personal Information',
                account_settings: 'Account Settings',
                app_settings: 'App Settings',
                data_management: 'Data Management',
                auto_detect: 'Auto Detect',
                change_password: 'Change Password',
                export_data: 'Export Data',
                delete_account: 'Delete Account',
                
                // Messages
                success_save: 'Successfully saved',
                error_occurred: 'An error occurred',
                confirm_delete: 'Are you sure you want to delete?',
                data_exported: 'Data has been exported',
                language_changed: 'Language has been changed'
            }
        };
    }

    // 翻訳取得
    t(key) {
        const keys = key.split('.');
        let value = this.translations[this.currentLanguage];
        
        for (const k of keys) {
            value = value?.[k];
        }
        
        return value || key;
    }

    // 言語変更
    setLanguage(lang) {
        if (!['ja', 'en'].includes(lang)) return;
        
        this.currentLanguage = lang;
        localStorage.setItem('bodyscale_language', lang);
        this.updatePageContent();
        
        // サーバーに言語設定を送信
        fetch('/api/language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language: lang })
        });
    }

    // ページコンテンツ更新
    updatePageContent() {
        // data-i18n属性を持つ要素を更新
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.textContent = this.t(key);
        });

        // プレースホルダーの更新
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = this.t(key);
        });

        // タイトルの更新
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });
    }

    // 現在の言語取得
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    // 言語切り替えUI作成
    createLanguageSelector() {
        const container = document.createElement('div');
        container.className = 'language-selector dropdown';
        
        container.innerHTML = `
            <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                🌐 ${this.currentLanguage.toUpperCase()}
            </button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#" data-lang="ja">🇯🇵 日本語</a></li>
                <li><a class="dropdown-item" href="#" data-lang="en">🇺🇸 English</a></li>
            </ul>
        `;

        // イベントリスナー追加
        container.querySelectorAll('[data-lang]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const lang = e.target.getAttribute('data-lang');
                this.setLanguage(lang);
                
                // ボタンテキスト更新
                const button = container.querySelector('.dropdown-toggle');
                button.innerHTML = `🌐 ${lang.toUpperCase()}`;
            });
        });

        return container;
    }
}

// グローバルインスタンス
window.i18n = new I18nManager();

// DOM読み込み完了後に初期化
document.addEventListener('DOMContentLoaded', function() {
    window.i18n.updatePageContent();
});