import { auth } from '../firebase';
import { onAuthStateChanged, User } from 'firebase/auth';

/**
 * 認証サービス
 * ユーザー認証状態の管理と確認
 */
export class AuthService {
  /**
   * 現在のユーザーを確実に取得
   */
  static getCurrentUser(): Promise<User | null> {
    return new Promise((resolve) => {
      const unsubscribe = onAuthStateChanged(auth, (user) => {
        unsubscribe();
        resolve(user);
      });
    });
  }

  /**
   * 認証が必要な操作の前にユーザーを確認
   */
  static async requireAuth(): Promise<User> {
    const user = await this.getCurrentUser();
    if (!user) {
      throw new Error('ログインが必要です');
    }
    return user;
  }

  /**
   * ユーザーIDを取得（認証必須）
   */
  static async getUserId(): Promise<string> {
    const user = await this.requireAuth();
    return user.uid;
  }

  /**
   * ユーザー情報を取得
   */
  static async getUserInfo(): Promise<{
    uid: string;
    email: string | null;
    displayName: string | null;
  }> {
    const user = await this.requireAuth();
    return {
      uid: user.uid,
      email: user.email,
      displayName: user.displayName
    };
  }

  /**
   * ユーザーが認証されているかチェック
   */
  static async isAuthenticated(): Promise<boolean> {
    const user = await this.getCurrentUser();
    return !!user;
  }
}