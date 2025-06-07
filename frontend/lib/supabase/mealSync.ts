import { supabase, type DbMealRecord } from './client'
import { MealStorage, type MealRecord } from '../storage/mealStorage'

export class MealSyncService {
  private syncInProgress = false
  private lastSyncTime: Date | null = null

  /**
   * ローカルデータをSupabaseに同期
   */
  async syncToSupabase(userId: string): Promise<{ success: boolean; error?: string }> {
    if (this.syncInProgress) {
      return { success: false, error: 'Sync already in progress' }
    }

    this.syncInProgress = true

    try {
      // ローカルの全食事データを取得
      const localMeals = MealStorage.getAllMeals()
      
      // 最後の同期時刻以降のデータのみをフィルタ
      const mealsToSync = this.lastSyncTime
        ? localMeals.filter(meal => new Date(meal.updatedAt) > this.lastSyncTime!)
        : localMeals

      if (mealsToSync.length === 0) {
        return { success: true }
      }

      // バッチでアップサート
      const { error } = await supabase
        .from('meals')
        .upsert(
          mealsToSync.map(meal => this.convertToDbFormat(meal, userId)),
          { onConflict: 'id' }
        )

      if (error) {
        throw error
      }

      this.lastSyncTime = new Date()
      return { success: true }

    } catch (error) {
      console.error('Sync to Supabase failed:', error)
      return { success: false, error: String(error) }
    } finally {
      this.syncInProgress = false
    }
  }

  /**
   * Supabaseからローカルに同期
   */
  async syncFromSupabase(userId: string): Promise<{ success: boolean; error?: string }> {
    try {
      // Supabaseから食事データを取得
      const { data, error } = await supabase
        .from('meals')
        .select('*')
        .eq('user_id', userId)
        .order('date', { ascending: false })

      if (error) {
        throw error
      }

      if (!data || data.length === 0) {
        return { success: true }
      }

      // ローカルストレージの既存データ
      const localMeals = MealStorage.getAllMeals()
      const localMealIds = new Set(localMeals.map(m => m.id))

      // 新規または更新されたデータのみを処理
      const mealsToUpdate: MealRecord[] = []

      for (const dbMeal of data) {
        const localMeal = this.convertFromDbFormat(dbMeal)
        
        // ローカルに存在しないか、更新日時が新しい場合
        const existingLocal = localMeals.find(m => m.id === localMeal.id)
        if (!existingLocal || new Date(localMeal.updatedAt) > new Date(existingLocal.updatedAt)) {
          mealsToUpdate.push(localMeal)
        }
      }

      // ローカルストレージを更新
      if (mealsToUpdate.length > 0) {
        for (const meal of mealsToUpdate) {
          if (localMealIds.has(meal.id)) {
            MealStorage.updateMeal(meal.id, meal)
          } else {
            MealStorage.saveMeal(meal)
          }
        }
      }

      this.lastSyncTime = new Date()
      return { success: true }

    } catch (error) {
      console.error('Sync from Supabase failed:', error)
      return { success: false, error: String(error) }
    }
  }

  /**
   * 双方向同期
   */
  async bidirectionalSync(userId: string): Promise<{ success: boolean; error?: string }> {
    // まずSupabaseから取得
    const pullResult = await this.syncFromSupabase(userId)
    if (!pullResult.success) {
      return pullResult
    }

    // 次にローカルの変更をプッシュ
    const pushResult = await this.syncToSupabase(userId)
    return pushResult
  }

  /**
   * リアルタイム同期の開始
   */
  startRealtimeSync(userId: string, onUpdate?: () => void) {
    const channel = supabase
      .channel(`meals:${userId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'meals',
          filter: `user_id=eq.${userId}`
        },
        async (payload) => {
          console.log('Realtime update received:', payload)
          
          // 変更をローカルに反映
          if (payload.eventType === 'INSERT' || payload.eventType === 'UPDATE') {
            const meal = this.convertFromDbFormat(payload.new as DbMealRecord)
            const existingMeal = MealStorage.getAllMeals().find(m => m.id === meal.id)
            
            if (existingMeal) {
              MealStorage.updateMeal(meal.id, meal)
            } else {
              MealStorage.saveMeal(meal)
            }
          } else if (payload.eventType === 'DELETE') {
            MealStorage.deleteMeal(payload.old.id)
          }

          onUpdate?.()
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }

  /**
   * ローカル形式からDB形式への変換
   */
  private convertToDbFormat(meal: MealRecord, userId: string): DbMealRecord {
    return {
      id: meal.id,
      user_id: userId,
      date: meal.date,
      meal_type: meal.mealType,
      foods: meal.foods,
      total_calories: meal.totalCalories,
      total_nutrition: meal.totalNutrition || {},
      pfc_balance: meal.pfcBalance || {},
      image_url: meal.imageUrl,
      notes: meal.notes,
      created_at: meal.createdAt,
      updated_at: meal.updatedAt
    }
  }

  /**
   * DB形式からローカル形式への変換
   */
  private convertFromDbFormat(dbMeal: DbMealRecord): MealRecord {
    return {
      id: dbMeal.id,
      date: dbMeal.date,
      mealType: dbMeal.meal_type,
      foods: dbMeal.foods,
      totalCalories: dbMeal.total_calories,
      totalNutrition: dbMeal.total_nutrition,
      pfcBalance: dbMeal.pfc_balance,
      imageUrl: dbMeal.image_url,
      notes: dbMeal.notes,
      createdAt: dbMeal.created_at,
      updatedAt: dbMeal.updated_at
    }
  }

  /**
   * オフライン変更の追跡
   */
  trackOfflineChanges() {
    // Service Workerを使用してオフライン変更を追跡
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      navigator.serviceWorker.ready.then(registration => {
        return (registration as any).sync.register('meal-sync')
      })
    }
  }
}