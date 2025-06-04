"""
Firebase認証システム統合モジュール
既存のauth_models.pyと連携してFirebase認証を提供
"""
import os
import json
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
from typing import Optional, Dict, Any
from auth_models import AuthManager

class FirebaseAuthManager:
    def __init__(self):
        self.auth_manager = AuthManager()  # 既存の認証システム
        self.firebase_app = None
        self.pyrebase_auth = None
        self.init_firebase()
    
    def init_firebase(self):
        """Firebase初期化"""
        try:
            # Firebase Admin SDK初期化
            if not firebase_admin._apps:
                service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH', 'service-account-key.json')
                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    self.firebase_app = firebase_admin.initialize_app(cred)
                    print("Firebase Admin SDK初期化完了")
            
            # Pyrebase初期化（クライアント側認証用）
            firebase_config = {
                "apiKey": os.environ.get('FIREBASE_API_KEY'),
                "authDomain": os.environ.get('FIREBASE_AUTH_DOMAIN'),
                "projectId": os.environ.get('FIREBASE_PROJECT_ID'),
                "storageBucket": os.environ.get('FIREBASE_STORAGE_BUCKET'),
                "messagingSenderId": os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
                "appId": os.environ.get('FIREBASE_APP_ID'),
                "databaseURL": ""  # Realtime Database不使用
            }
            
            # 環境変数が設定されている場合のみPyrebase初期化
            if firebase_config.get('apiKey'):
                firebase = pyrebase.initialize_app(firebase_config)
                self.pyrebase_auth = firebase.auth()
                print("Pyrebase初期化完了")
            
        except Exception as e:
            print(f"Firebase初期化エラー: {e}")
    
    def create_user_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Firebaseでユーザー作成"""
        try:
            if self.pyrebase_auth:
                # Pyrebaseでユーザー作成
                user = self.pyrebase_auth.create_user_with_email_and_password(email, password)
                
                # メール認証送信
                self.pyrebase_auth.send_email_verification(user['idToken'])
                
                # 既存のPostgreSQLにもユーザー情報を保存
                self.auth_manager.create_user(email, password)
                
                return {
                    'success': True,
                    'user_id': user['localId'],
                    'email': email,
                    'message': 'アカウントを作成しました。確認メールを送信しました。'
                }
            else:
                # Firebaseが利用できない場合は既存システムを使用
                return self.auth_manager.create_user(email, password)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def sign_in_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Firebaseでサインイン"""
        try:
            if self.pyrebase_auth:
                # Pyrebaseでサインイン
                user = self.pyrebase_auth.sign_in_with_email_and_password(email, password)
                
                # Firebase IDトークンを検証
                decoded_token = auth.verify_id_token(user['idToken'])
                
                return {
                    'success': True,
                    'user_id': decoded_token['uid'],
                    'email': decoded_token['email'],
                    'email_verified': decoded_token.get('email_verified', False),
                    'id_token': user['idToken'],
                    'refresh_token': user['refreshToken']
                }
            else:
                # Firebaseが利用できない場合は既存システムを使用
                return self.auth_manager.authenticate_user_simple(email, password)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Firebase IDトークンを検証"""
        try:
            if self.firebase_app:
                decoded_token = auth.verify_id_token(id_token)
                return decoded_token
            return None
        except Exception as e:
            print(f"IDトークン検証エラー: {e}")
            return None
    
    def send_password_reset_email(self, email: str) -> Dict[str, Any]:
        """パスワードリセットメール送信"""
        try:
            if self.pyrebase_auth:
                self.pyrebase_auth.send_password_reset_email(email)
                return {
                    'success': True,
                    'message': 'パスワードリセットメールを送信しました。'
                }
            else:
                return {
                    'success': False,
                    'error': 'Firebase認証が利用できません'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """リフレッシュトークンでアクセストークンを更新"""
        try:
            if self.pyrebase_auth:
                user = self.pyrebase_auth.refresh(refresh_token)
                return {
                    'success': True,
                    'id_token': user['idToken'],
                    'refresh_token': user['refreshToken']
                }
            else:
                return {
                    'success': False,
                    'error': 'Firebase認証が利用できません'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_info(self, id_token: str) -> Optional[Dict[str, Any]]:
        """IDトークンからユーザー情報を取得"""
        decoded_token = self.verify_id_token(id_token)
        if decoded_token:
            return {
                'user_id': decoded_token['uid'],
                'email': decoded_token['email'],
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture')
            }
        return None