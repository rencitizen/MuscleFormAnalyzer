import { 
  collection, 
  doc, 
  addDoc, 
  updateDoc, 
  deleteDoc, 
  getDocs, 
  getDoc,
  query, 
  where, 
  orderBy, 
  serverTimestamp,
  Timestamp,
  onSnapshot,
  DocumentData,
  QuerySnapshot,
  writeBatch
} from 'firebase/firestore';
import { db } from '../firebase';
import { AuthService } from './authService';

export interface ProgressData {
  id?: string;
  userId: string;
  userEmail?: string;
  exercise: string;
  score: number;
  weight?: number;
  reps?: number;
  sets?: number;
  volume?: number;
  date: Date | Timestamp;
  notes?: string;
  createdAt?: Timestamp;
  updatedAt?: Timestamp;
  isOwner?: boolean;
}

export interface ProgressSummary {
  totalSessions: number;
  averageScore: number;
  totalVolume: number;
  currentStreak: number;
  lastSessionDate?: Date;
}

/**
 * 進捗データ管理サービス
 * ユーザー固有のデータのみを扱う
 */
export class ProgressService {
  private static readonly COLLECTION_NAME = 'progress';

  /**
   * ユーザーの進捗データを取得
   */
  static async getUserProgress(
    exerciseFilter?: string,
    dateFrom?: Date,
    dateTo?: Date
  ): Promise<ProgressData[]> {
    try {
      const currentUser = await AuthService.requireAuth();
      
      // 基本クエリ（ユーザーIDでフィルタリング）
      let q = query(
        collection(db, this.COLLECTION_NAME),
        where('userId', '==', currentUser.uid)
      );

      // エクササイズフィルター
      if (exerciseFilter && exerciseFilter !== 'all') {
        q = query(q, where('exercise', '==', exerciseFilter));
      }

      // 日付でソート
      q = query(q, orderBy('date', 'desc'));
      
      const snapshot = await getDocs(q);
      
      const progressData = snapshot.docs.map(doc => {
        const data = doc.data();
        return {
          id: doc.id,
          ...data,
          date: data.date?.toDate ? data.date.toDate() : new Date(data.date),
          createdAt: data.createdAt?.toDate ? data.createdAt.toDate() : undefined,
          updatedAt: data.updatedAt?.toDate ? data.updatedAt.toDate() : undefined,
          isOwner: data.userId === currentUser.uid
        } as ProgressData;
      });

      // クライアントサイドで日付フィルタリング（必要な場合）
      let filteredData = progressData;
      if (dateFrom) {
        filteredData = filteredData.filter(item => 
          new Date(item.date) >= dateFrom
        );
      }
      if (dateTo) {
        filteredData = filteredData.filter(item => 
          new Date(item.date) <= dateTo
        );
      }

      // 追加の安全チェック（二重確認）
      return filteredData.filter(item => item.userId === currentUser.uid && item.isOwner);
      
    } catch (error) {
      console.error('進捗データ取得エラー:', error);
      return [];
    }
  }

  /**
   * 進捗データを追加
   */
  static async addProgress(progressData: Omit<ProgressData, 'id' | 'userId' | 'createdAt' | 'updatedAt' | 'isOwner'>): Promise<string> {
    try {
      const currentUser = await AuthService.requireAuth();
      
      const docData = {
        ...progressData,
        userId: currentUser.uid,
        userEmail: currentUser.email,
        date: progressData.date instanceof Date ? Timestamp.fromDate(progressData.date) : progressData.date,
        volume: progressData.weight && progressData.reps && progressData.sets 
          ? progressData.weight * progressData.reps * progressData.sets 
          : 0,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      };
      
      const docRef = await addDoc(collection(db, this.COLLECTION_NAME), docData);
      
      return docRef.id;
      
    } catch (error) {
      console.error('進捗データ追加エラー:', error);
      throw error;
    }
  }

  /**
   * 進捗データを更新
   */
  static async updateProgress(
    progressId: string, 
    updateData: Partial<Omit<ProgressData, 'id' | 'userId' | 'createdAt' | 'isOwner'>>
  ): Promise<void> {
    try {
      const currentUser = await AuthService.requireAuth();
      
      // 所有権確認
      const docRef = doc(db, this.COLLECTION_NAME, progressId);
      const docSnap = await getDoc(docRef);
      
      if (!docSnap.exists()) {
        throw new Error('記録が見つかりません');
      }
      
      if (docSnap.data().userId !== currentUser.uid) {
        throw new Error('この記録を編集する権限がありません');
      }
      
      // ボリューム再計算
      const currentData = docSnap.data();
      const weight = updateData.weight ?? currentData.weight;
      const reps = updateData.reps ?? currentData.reps;
      const sets = updateData.sets ?? currentData.sets;
      
      const updatePayload = {
        ...updateData,
        volume: weight && reps && sets ? weight * reps * sets : 0,
        updatedAt: serverTimestamp()
      };

      if (updateData.date instanceof Date) {
        updatePayload.date = Timestamp.fromDate(updateData.date);
      }
      
      await updateDoc(docRef, updatePayload);
      
    } catch (error) {
      console.error('進捗データ更新エラー:', error);
      throw error;
    }
  }

  /**
   * 進捗データを削除
   */
  static async deleteProgress(progressId: string): Promise<void> {
    try {
      const currentUser = await AuthService.requireAuth();
      
      // 所有権確認
      const docRef = doc(db, this.COLLECTION_NAME, progressId);
      const docSnap = await getDoc(docRef);
      
      if (!docSnap.exists()) {
        throw new Error('記録が見つかりません');
      }
      
      if (docSnap.data().userId !== currentUser.uid) {
        throw new Error('この記録を削除する権限がありません');
      }
      
      await deleteDoc(docRef);
      
    } catch (error) {
      console.error('進捗データ削除エラー:', error);
      throw error;
    }
  }

  /**
   * リアルタイム進捗データ監視
   */
  static subscribeToUserProgress(
    callback: (data: ProgressData[]) => void,
    exerciseFilter?: string
  ): () => void {
    let unsubscribe = () => {};

    AuthService.getCurrentUser().then(user => {
      if (!user) {
        callback([]);
        return;
      }

      let q = query(
        collection(db, this.COLLECTION_NAME),
        where('userId', '==', user.uid),
        orderBy('date', 'desc')
      );

      if (exerciseFilter && exerciseFilter !== 'all') {
        q = query(q, where('exercise', '==', exerciseFilter));
      }

      unsubscribe = onSnapshot(q, 
        (snapshot) => {
          const data = snapshot.docs.map(doc => {
            const docData = doc.data();
            return {
              id: doc.id,
              ...docData,
              date: docData.date?.toDate ? docData.date.toDate() : new Date(docData.date),
              createdAt: docData.createdAt?.toDate ? docData.createdAt.toDate() : undefined,
              updatedAt: docData.updatedAt?.toDate ? docData.updatedAt.toDate() : undefined,
              isOwner: true
            } as ProgressData;
          });
          
          // 追加のセキュリティチェック
          const secureData = data.filter(item => item.userId === user.uid);
          callback(secureData);
        },
        (error) => {
          console.error('リアルタイムデータエラー:', error);
          callback([]);
        }
      );
    });

    return unsubscribe;
  }

  /**
   * 進捗サマリーを計算
   */
  static async getProgressSummary(dateFrom?: Date): Promise<ProgressSummary> {
    try {
      const progressData = await this.getUserProgress(undefined, dateFrom);
      
      if (progressData.length === 0) {
        return {
          totalSessions: 0,
          averageScore: 0,
          totalVolume: 0,
          currentStreak: 0
        };
      }

      // 集計計算
      const totalSessions = progressData.length;
      const totalScore = progressData.reduce((sum, item) => sum + (item.score || 0), 0);
      const totalVolume = progressData.reduce((sum, item) => sum + (item.volume || 0), 0);
      
      // 連続記録計算
      const sortedData = [...progressData].sort((a, b) => 
        new Date(b.date).getTime() - new Date(a.date).getTime()
      );
      
      let currentStreak = 0;
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      for (let i = 0; i < sortedData.length; i++) {
        const sessionDate = new Date(sortedData[i].date);
        sessionDate.setHours(0, 0, 0, 0);
        
        const daysDiff = Math.floor((today.getTime() - sessionDate.getTime()) / (1000 * 60 * 60 * 24));
        
        if (daysDiff === i) {
          currentStreak++;
        } else {
          break;
        }
      }

      return {
        totalSessions,
        averageScore: totalSessions > 0 ? totalScore / totalSessions : 0,
        totalVolume,
        currentStreak,
        lastSessionDate: sortedData[0]?.date
      };
      
    } catch (error) {
      console.error('サマリー計算エラー:', error);
      return {
        totalSessions: 0,
        averageScore: 0,
        totalVolume: 0,
        currentStreak: 0
      };
    }
  }

  /**
   * データ移行ヘルパー（既存データにuserIdがない場合）
   */
  static async migrateExistingData(): Promise<void> {
    try {
      const currentUser = await AuthService.requireAuth();
      
      const progressRef = collection(db, this.COLLECTION_NAME);
      const q = query(progressRef, where('userId', '==', null));
      const snapshot = await getDocs(q);
      
      if (snapshot.empty) {
        console.log('移行が必要なデータはありません');
        return;
      }
      
      const batch = writeBatch(db);
      
      snapshot.docs.forEach(doc => {
        // 現在のユーザーのメールアドレスと一致する場合のみ移行
        const data = doc.data();
        if (data.userEmail === currentUser.email) {
          batch.update(doc.ref, { 
            userId: currentUser.uid,
            updatedAt: serverTimestamp()
          });
        }
      });
      
      await batch.commit();
      console.log('データ移行完了');
      
    } catch (error) {
      console.error('データ移行エラー:', error);
    }
  }
}