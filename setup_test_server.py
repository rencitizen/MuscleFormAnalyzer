#!/usr/bin/env python3
"""
BodyScale Pose Analyzer - テストサーバーセットアップスクリプト
簡単にテスト環境を構築して動作確認ができます
"""

import os
import sys
import subprocess
import json
import shutil
import time
from pathlib import Path

class TestServerSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.frontend_dir = self.root_dir / 'frontend'
        self.is_windows = sys.platform.startswith('win')
        
    def check_requirements(self):
        """必要なソフトウェアがインストールされているか確認"""
        print("🔍 必要なソフトウェアを確認中...")
        
        # Python確認
        try:
            python_version = subprocess.check_output([sys.executable, '--version'], text=True)
            print(f"✅ Python: {python_version.strip()}")
        except:
            print("❌ Pythonが見つかりません")
            return False
            
        # Node.js確認
        try:
            node_version = subprocess.check_output(['node', '--version'], text=True)
            print(f"✅ Node.js: {node_version.strip()}")
        except:
            print("❌ Node.jsが見つかりません。https://nodejs.org からインストールしてください")
            return False
            
        return True
    
    def setup_backend(self):
        """バックエンドのセットアップ"""
        print("\n📦 バックエンドをセットアップ中...")
        
        # 仮想環境作成
        if not (self.root_dir / 'venv').exists():
            print("仮想環境を作成中...")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], cwd=self.root_dir)
        
        # 仮想環境のPythonパス
        if self.is_windows:
            pip_path = self.root_dir / 'venv' / 'Scripts' / 'pip'
            python_path = self.root_dir / 'venv' / 'Scripts' / 'python'
        else:
            pip_path = self.root_dir / 'venv' / 'bin' / 'pip'
            python_path = self.root_dir / 'venv' / 'bin' / 'python'
        
        # 最小限の依存関係をインストール
        print("依存関係をインストール中...")
        minimal_requirements = [
            'flask>=3.0.0',
            'flask-cors',
            'numpy',
            'opencv-python-headless',  # GUIなしバージョン
            'mediapipe',
            'python-dotenv'
        ]
        
        for req in minimal_requirements:
            subprocess.run([str(pip_path), 'install', req], capture_output=True)
            print(f"  ✅ {req}")
        
        # テスト用の環境変数ファイル作成
        env_content = """# テスト環境用設定
USE_SQLITE=true
SQLITE_DB_PATH=test_muscleform.db
SESSION_SECRET=test-secret-key-change-in-production
ENV=development
LOG_LEVEL=DEBUG
"""
        with open(self.root_dir / '.env', 'w') as f:
            f.write(env_content)
        
        # テスト用データベース初期化
        print("テストデータベースを初期化中...")
        init_db_script = """
import sqlite3
import json
from datetime import datetime, timedelta

# SQLiteデータベース作成
conn = sqlite3.connect('test_muscleform.db')
cur = conn.cursor()

# 基本テーブル作成
cur.execute('''CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT DEFAULT 'demo_user',
    date DATE NOT NULL,
    exercise TEXT NOT NULL,
    exercise_name TEXT,
    weight_kg REAL NOT NULL,
    reps INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    height_cm REAL,
    weight_kg REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

# デモユーザー作成
cur.execute("INSERT OR IGNORE INTO user_profiles (user_id, height_cm, weight_kg) VALUES (?, ?, ?)",
            ('demo_user', 170, 70))

# サンプルワークアウトデータ
sample_workouts = []
exercises = [
    ('squat', 'スクワット', [60, 65, 70, 75, 80]),
    ('bench_press', 'ベンチプレス', [40, 45, 50, 50, 55]),
    ('deadlift', 'デッドリフト', [80, 85, 90, 95, 100])
]

for i in range(30):
    date = datetime.now() - timedelta(days=29-i)
    if i % 3 != 2:  # 3日に2日トレーニング
        for exercise_id, exercise_name, weights in exercises:
            if i % 3 == 0 and exercise_id == 'squat':
                weight = weights[min(i//6, 4)]
                cur.execute('''INSERT INTO workouts 
                    (user_id, date, exercise, exercise_name, weight_kg, reps) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    ('demo_user', date.strftime('%Y-%m-%d'), exercise_id, exercise_name, weight, 8))
            elif i % 3 == 1 and exercise_id == 'bench_press':
                weight = weights[min(i//6, 4)]
                cur.execute('''INSERT INTO workouts 
                    (user_id, date, exercise, exercise_name, weight_kg, reps) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    ('demo_user', date.strftime('%Y-%m-%d'), exercise_id, exercise_name, weight, 10))

conn.commit()
conn.close()
print("✅ テストデータベース作成完了")
"""
        
        init_db_path = self.root_dir / 'init_test_db.py'
        with open(init_db_path, 'w') as f:
            f.write(init_db_script)
        
        subprocess.run([str(python_path), str(init_db_path)], cwd=self.root_dir)
        os.remove(init_db_path)
        
        return str(python_path)
    
    def setup_frontend(self):
        """フロントエンドのセットアップ"""
        print("\n🎨 フロントエンドをセットアップ中...")
        
        if not self.frontend_dir.exists():
            print("❌ frontendディレクトリが見つかりません")
            return False
        
        # package.jsonの存在確認
        if not (self.frontend_dir / 'package.json').exists():
            print("❌ package.jsonが見つかりません")
            return False
        
        # テスト用環境変数設定
        env_local = """# テスト環境用Firebase設定（ダミー）
NEXT_PUBLIC_FIREBASE_API_KEY=test-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=test-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=test-project
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=test-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abc123

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:5000

# Demo Mode
NEXT_PUBLIC_DEMO_MODE=true
"""
        with open(self.frontend_dir / '.env.local', 'w') as f:
            f.write(env_local)
        
        print("依存関係をインストール中... (初回は時間がかかります)")
        result = subprocess.run(['npm', 'install'], cwd=self.frontend_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ npm installでエラーが発生しました: {result.stderr}")
            return False
        
        print("✅ フロントエンドのセットアップ完了")
        return True
    
    def create_demo_mode(self):
        """デモモード用のコンポーネント作成"""
        print("\n🎭 デモモードを設定中...")
        
        # デモモード用のフックを作成
        demo_hook = '''export function useDemoMode() {
  const isDemoMode = process.env.NEXT_PUBLIC_DEMO_MODE === 'true'
  
  const demoVideo = '/demo/squat_demo.mp4'
  const demoMessage = 'デモモード: 実際のカメラの代わりにサンプル動画を使用しています'
  
  return { isDemoMode, demoVideo, demoMessage }
}'''
        
        with open(self.frontend_dir / 'lib' / 'hooks' / 'useDemoMode.ts', 'w') as f:
            f.write(demo_hook)
        
        print("✅ デモモード設定完了")
    
    def start_servers(self, python_path):
        """サーバーを起動"""
        print("\n🚀 サーバーを起動中...")
        
        # バックエンドサーバー起動
        print("バックエンドサーバーを起動中...")
        if self.is_windows:
            backend_cmd = f'start cmd /k "{python_path} app.py"'
            subprocess.Popen(backend_cmd, shell=True, cwd=self.root_dir)
        else:
            subprocess.Popen([python_path, 'app.py'], cwd=self.root_dir)
        
        # 少し待機
        time.sleep(3)
        
        # フロントエンドサーバー起動
        print("フロントエンドサーバーを起動中...")
        if self.is_windows:
            frontend_cmd = 'start cmd /k "npm run dev"'
            subprocess.Popen(frontend_cmd, shell=True, cwd=self.frontend_dir)
        else:
            subprocess.Popen(['npm', 'run', 'dev'], cwd=self.frontend_dir)
        
        print("\n✅ サーバーが起動しました！")
        print("\n📱 アクセスURL:")
        print("   フロントエンド: http://localhost:3000")
        print("   バックエンド: http://localhost:5000")
        print("\n🔑 デモアカウント:")
        print("   メール: demo@example.com")
        print("   パスワード: demo123")
        print("\n💡 ヒント:")
        print("   - デモモードではカメラなしで動作確認できます")
        print("   - サンプルデータが既に入っています")
        print("   - Ctrl+C で終了できます")
    
    def run(self):
        """セットアップを実行"""
        print("🏋️ BodyScale Pose Analyzer テストサーバーセットアップ")
        print("="*50)
        
        if not self.check_requirements():
            return
        
        python_path = self.setup_backend()
        
        if not self.setup_frontend():
            return
        
        # デモモード用のディレクトリ作成
        os.makedirs(self.frontend_dir / 'lib' / 'hooks', exist_ok=True)
        self.create_demo_mode()
        
        self.start_servers(python_path)
        
        # 終了待機
        try:
            print("\n終了するには Ctrl+C を押してください")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 サーバーを停止しています...")

if __name__ == '__main__':
    setup = TestServerSetup()
    setup.run()