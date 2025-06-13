import { v4 as uuidv4 } from 'uuid'

export interface FoodItem {
  name: string
  quantity: string
  calories: number
  protein?: number
  carbs?: number
  fat?: number
  fiber?: number
  confidence?: number
}

export interface MealRecord {
  id: string
  date: string
  mealType: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  foods: FoodItem[]
  totalCalories: number
  totalNutrition?: {
    protein: number
    carbs: number
    fat: number
    fiber?: number
  }
  pfcBalance?: {
    protein_ratio: number
    carbs_ratio: number
    fat_ratio: number
  }
  imageUrl?: string
  notes?: string
  createdAt: string
  updatedAt: string
}

export interface DailyStats {
  date: string
  totalCalories: number
  mealCount: number
  nutrition: {
    protein: number
    carbs: number
    fat: number
  }
}

const STORAGE_KEY = 'tenaxfit_meals'
const FAVORITES_KEY = 'tenaxfit_favorite_foods'
const CUSTOM_FOODS_KEY = 'tenaxfit_custom_foods'

export class MealStorage {
  // Create a new meal record
  static createMeal(
    mealType: MealRecord['mealType'],
    foods: FoodItem[],
    imageUrl?: string,
    notes?: string
  ): MealRecord {
    const now = new Date().toISOString()
    const totalCalories = foods.reduce((sum, food) => sum + (food.calories || 0), 0)
    const totalNutrition = this.calculateTotalNutrition(foods)
    
    return {
      id: uuidv4(),
      date: now,
      mealType,
      foods,
      totalCalories,
      totalNutrition,
      imageUrl,
      notes,
      createdAt: now,
      updatedAt: now
    }
  }

  // Calculate total nutrition from foods
  static calculateTotalNutrition(foods: FoodItem[]) {
    return foods.reduce(
      (total, food) => ({
        protein: total.protein + (food.protein || 0),
        carbs: total.carbs + (food.carbs || 0),
        fat: total.fat + (food.fat || 0),
        fiber: total.fiber + (food.fiber || 0)
      }),
      { protein: 0, carbs: 0, fat: 0, fiber: 0 }
    )
  }

  // Save meal to localStorage
  static saveMeal(meal: MealRecord): boolean {
    try {
      const meals = this.getAllMeals()
      meals.push(meal)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(meals))
      return true
    } catch (error) {
      console.error('Failed to save meal:', error)
      return false
    }
  }

  // Get all meals
  static getAllMeals(): MealRecord[] {
    try {
      const data = localStorage.getItem(STORAGE_KEY)
      return data ? JSON.parse(data) : []
    } catch (error) {
      console.error('Failed to load meals:', error)
      return []
    }
  }

  // Get meals by date
  static getMealsByDate(date: Date): MealRecord[] {
    const targetDate = date.toDateString()
    return this.getAllMeals().filter(
      meal => new Date(meal.date).toDateString() === targetDate
    )
  }

  // Get meals by date range
  static getMealsByDateRange(startDate: Date, endDate: Date): MealRecord[] {
    const start = startDate.getTime()
    const end = endDate.getTime()
    
    return this.getAllMeals().filter(meal => {
      const mealTime = new Date(meal.date).getTime()
      return mealTime >= start && mealTime <= end
    })
  }

  // Update meal
  static updateMeal(id: string, updates: Partial<MealRecord>): boolean {
    try {
      const meals = this.getAllMeals()
      const index = meals.findIndex(meal => meal.id === id)
      
      if (index === -1) return false
      
      meals[index] = {
        ...meals[index],
        ...updates,
        updatedAt: new Date().toISOString()
      }
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(meals))
      return true
    } catch (error) {
      console.error('Failed to update meal:', error)
      return false
    }
  }

  // Delete meal
  static deleteMeal(id: string): boolean {
    try {
      const meals = this.getAllMeals()
      const filtered = meals.filter(meal => meal.id !== id)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
      return true
    } catch (error) {
      console.error('Failed to delete meal:', error)
      return false
    }
  }

  // Get daily stats
  static getDailyStats(date: Date): DailyStats {
    const meals = this.getMealsByDate(date)
    
    const stats = meals.reduce(
      (acc, meal) => ({
        totalCalories: acc.totalCalories + meal.totalCalories,
        mealCount: acc.mealCount + 1,
        nutrition: {
          protein: acc.nutrition.protein + (meal.totalNutrition?.protein || 0),
          carbs: acc.nutrition.carbs + (meal.totalNutrition?.carbs || 0),
          fat: acc.nutrition.fat + (meal.totalNutrition?.fat || 0)
        }
      }),
      {
        totalCalories: 0,
        mealCount: 0,
        nutrition: { protein: 0, carbs: 0, fat: 0 }
      }
    )
    
    return {
      date: date.toISOString(),
      ...stats
    }
  }

  // Get weekly stats
  static getWeeklyStats(date: Date): DailyStats[] {
    const stats: DailyStats[] = []
    const startOfWeek = new Date(date)
    startOfWeek.setDate(date.getDate() - date.getDay())
    
    for (let i = 0; i < 7; i++) {
      const currentDate = new Date(startOfWeek)
      currentDate.setDate(startOfWeek.getDate() + i)
      stats.push(this.getDailyStats(currentDate))
    }
    
    return stats
  }

  // Favorite foods management
  static getFavoriteFoods(): FoodItem[] {
    try {
      const data = localStorage.getItem(FAVORITES_KEY)
      return data ? JSON.parse(data) : []
    } catch (error) {
      console.error('Failed to load favorite foods:', error)
      return []
    }
  }

  static addFavoriteFood(food: FoodItem): boolean {
    try {
      const favorites = this.getFavoriteFoods()
      if (!favorites.find(f => f.name === food.name)) {
        favorites.push(food)
        localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites))
      }
      return true
    } catch (error) {
      console.error('Failed to add favorite food:', error)
      return false
    }
  }

  static removeFavoriteFood(foodName: string): boolean {
    try {
      const favorites = this.getFavoriteFoods()
      const filtered = favorites.filter(f => f.name !== foodName)
      localStorage.setItem(FAVORITES_KEY, JSON.stringify(filtered))
      return true
    } catch (error) {
      console.error('Failed to remove favorite food:', error)
      return false
    }
  }

  // Custom foods management
  static getCustomFoods(): FoodItem[] {
    try {
      const data = localStorage.getItem(CUSTOM_FOODS_KEY)
      return data ? JSON.parse(data) : []
    } catch (error) {
      console.error('Failed to load custom foods:', error)
      return []
    }
  }

  static addCustomFood(food: FoodItem): boolean {
    try {
      const customFoods = this.getCustomFoods()
      customFoods.push(food)
      localStorage.setItem(CUSTOM_FOODS_KEY, JSON.stringify(customFoods))
      return true
    } catch (error) {
      console.error('Failed to add custom food:', error)
      return false
    }
  }

  static deleteCustomFood(foodName: string): boolean {
    try {
      const customFoods = this.getCustomFoods()
      const filtered = customFoods.filter(f => f.name !== foodName)
      localStorage.setItem(CUSTOM_FOODS_KEY, JSON.stringify(filtered))
      return true
    } catch (error) {
      console.error('Failed to delete custom food:', error)
      return false
    }
  }

  // Export data for backup or Supabase sync
  static exportData() {
    return {
      meals: this.getAllMeals(),
      favorites: this.getFavoriteFoods(),
      customFoods: this.getCustomFoods(),
      exportDate: new Date().toISOString()
    }
  }

  // Import data
  static importData(data: ReturnType<typeof MealStorage.exportData>): boolean {
    try {
      if (data.meals) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data.meals))
      }
      if (data.favorites) {
        localStorage.setItem(FAVORITES_KEY, JSON.stringify(data.favorites))
      }
      if (data.customFoods) {
        localStorage.setItem(CUSTOM_FOODS_KEY, JSON.stringify(data.customFoods))
      }
      return true
    } catch (error) {
      console.error('Failed to import data:', error)
      return false
    }
  }

  // Clear all data
  static clearAllData(): boolean {
    try {
      localStorage.removeItem(STORAGE_KEY)
      localStorage.removeItem(FAVORITES_KEY)
      localStorage.removeItem(CUSTOM_FOODS_KEY)
      return true
    } catch (error) {
      console.error('Failed to clear data:', error)
      return false
    }
  }
}