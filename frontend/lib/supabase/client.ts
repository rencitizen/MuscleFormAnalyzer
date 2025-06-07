import { createClient } from '@supabase/supabase-js'

// Supabase設定
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// データベース型定義
export interface DbMealRecord {
  id: string
  user_id: string
  date: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  foods: any[] // JSON
  total_calories: number
  total_nutrition: any // JSON
  pfc_balance: any // JSON
  image_url?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface DbUserProfile {
  id: string
  email: string
  display_name?: string
  height_cm?: number
  weight_kg?: number
  age?: number
  gender?: 'male' | 'female' | 'other'
  activity_level?: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active'
  daily_calorie_goal?: number
  daily_protein_goal?: number
  created_at: string
  updated_at: string
}

export interface DbFavoriteFood {
  id: string
  user_id: string
  food_name: string
  food_data: any // JSON
  created_at: string
}