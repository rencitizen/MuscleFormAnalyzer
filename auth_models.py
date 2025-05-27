"""
ユーザー認証システム
メール認証・アカウント管理
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any

class AuthManager:
    def __init__(self):
        self.connection_params = {
            'host': os.environ.get('PGHOST'),
            'port': os.environ.get('PGPORT'),
            'database': os.environ.get('PGDATABASE'),
            'user': os.environ.get('PGUSER'),
            'password': os.environ.get('PGPASSWORD')
        }
        self.init_auth_tables()
    
    def get_connection(self):
        """データベース接続を取得"""
        return psycopg2.connect(**self.connection_params)
    
    def init_auth_tables(self):
        """認証関連テーブルを初期化"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # ユーザーアカウントテーブル
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS user_accounts (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            salt VARCHAR(255) NOT NULL,
                            is_verified BOOLEAN DEFAULT FALSE,
                            verification_token VARCHAR(255),
                            reset_token VARCHAR(255),
                            reset_token_expires TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP
                        )
                    """)
                    
                    # セッションテーブル
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS user_sessions (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES user_accounts(id) ON DELETE CASCADE,
                            session_token VARCHAR(255) UNIQUE NOT NULL,
                            expires_at TIMESTAMP NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # 既存のuser_profilesテーブルをuser_accountsと連携
                    cur.execute("""
                        ALTER TABLE user_profiles 
                        DROP CONSTRAINT IF EXISTS user_profiles_user_id_fkey
                    """)
                    
                    cur.execute("""
                        ALTER TABLE user_profiles 
                        ADD CONSTRAINT user_profiles_user_id_fkey 
                        FOREIGN KEY (user_id) REFERENCES user_accounts(email) 
                        ON DELETE CASCADE
                    """)
                    
                    # 既存のworkoutsテーブルもuser_accountsと連携
                    cur.execute("""
                        ALTER TABLE workouts 
                        DROP CONSTRAINT IF EXISTS workouts_user_id_fkey
                    """)
                    
                    cur.execute("""
                        ALTER TABLE workouts 
                        ADD CONSTRAINT workouts_user_id_fkey 
                        FOREIGN KEY (user_id) REFERENCES user_accounts(email) 
                        ON DELETE CASCADE
                    """)
                    
                    conn.commit()
                    print("認証テーブルを初期化しました")
                    
        except Exception as e:
            print(f"認証テーブル初期化エラー: {e}")
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """パスワードをハッシュ化"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        return password_hash, salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """パスワードを検証"""
        computed_hash, _ = self.hash_password(password, salt)
        return computed_hash == password_hash
    
    def create_user(self, email: str, password: str) -> Dict[str, Any]:
        """新規ユーザーを作成"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 既存ユーザーチェック
                    cur.execute("SELECT id FROM user_accounts WHERE email = %s", (email,))
                    if cur.fetchone():
                        return {'success': False, 'error': 'このメールアドレスは既に登録されています'}
                    
                    # パスワードハッシュ化
                    password_hash, salt = self.hash_password(password)
                    verification_token = secrets.token_urlsafe(32)
                    
                    # ユーザー作成
                    cur.execute("""
                        INSERT INTO user_accounts (email, password_hash, salt, verification_token)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (email, password_hash, salt, verification_token))
                    
                    user_id = cur.fetchone()['id']
                    conn.commit()
                    
                    return {
                        'success': True,
                        'user_id': user_id,
                        'verification_token': verification_token
                    }
                    
        except Exception as e:
            print(f"ユーザー作成エラー: {e}")
            return {'success': False, 'error': 'アカウント作成に失敗しました'}
    
    def verify_user(self, verification_token: str) -> bool:
        """メール認証を完了"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE user_accounts 
                        SET is_verified = TRUE, verification_token = NULL
                        WHERE verification_token = %s
                    """, (verification_token,))
                    
                    if cur.rowcount > 0:
                        conn.commit()
                        return True
                    return False
                    
        except Exception as e:
            print(f"メール認証エラー: {e}")
            return False
    
    def authenticate_user_simple(self, email: str, password: str) -> Dict[str, Any]:
        """ユーザー認証（メール認証スキップ版）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, email, password_hash, salt
                        FROM user_accounts 
                        WHERE email = %s
                    """, (email,))
                    
                    user = cur.fetchone()
                    if not user:
                        return {'success': False, 'error': 'メールアドレスまたはパスワードが間違っています'}
                    
                    if not self.verify_password(password, user['password_hash'], user['salt']):
                        return {'success': False, 'error': 'メールアドレスまたはパスワードが間違っています'}
                    
                    # ログイン時刻を更新
                    cur.execute("""
                        UPDATE user_accounts 
                        SET last_login = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    """, (user['id'],))
                    conn.commit()
                    
                    return {
                        'success': True,
                        'user': {
                            'id': user['id'],
                            'email': user['email']
                        }
                    }
                    
        except Exception as e:
            print(f"認証エラー: {e}")
            return {'success': False, 'error': 'ログインに失敗しました'}
    
    def create_session(self, user_id: int) -> str:
        """セッションを作成"""
        try:
            session_token = secrets.token_urlsafe(64)
            expires_at = datetime.now() + timedelta(days=30)
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO user_sessions (user_id, session_token, expires_at)
                        VALUES (%s, %s, %s)
                    """, (user_id, session_token, expires_at))
                    conn.commit()
                    
            return session_token
            
        except Exception as e:
            print(f"セッション作成エラー: {e}")
            return None
    
    def get_user_from_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """セッションからユーザー情報を取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT ua.id, ua.email
                        FROM user_accounts ua
                        JOIN user_sessions us ON ua.id = us.user_id
                        WHERE us.session_token = %s AND us.expires_at > CURRENT_TIMESTAMP
                    """, (session_token,))
                    
                    user = cur.fetchone()
                    return dict(user) if user else None
                    
        except Exception as e:
            print(f"セッション取得エラー: {e}")
            return None
    
    def delete_session(self, session_token: str) -> bool:
        """セッションを削除（ログアウト）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM user_sessions 
                        WHERE session_token = %s
                    """, (session_token,))
                    
                    success = cur.rowcount > 0
                    conn.commit()
                    return success
                    
        except Exception as e:
            print(f"セッション削除エラー: {e}")
            return False

# グローバルインスタンス
auth_manager = AuthManager()