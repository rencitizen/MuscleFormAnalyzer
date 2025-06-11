'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Calendar, List, TrendingUp, Edit2, Trash2, Coffee, Sun, Moon, Cookie } from 'lucide-react'
import { MealStorage, type MealRecord, type DailyStats } from '../../lib/storage/mealStorage'
import { format, startOfWeek, addDays, isSameDay } from 'date-fns'
import { ja } from 'date-fns/locale'

interface MealHistoryProps {
  onEditMeal?: (meal: MealRecord) => void
}

export function MealHistory({ onEditMeal }: MealHistoryProps) {
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar')
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [meals, setMeals] = useState<MealRecord[]>([])
  const [weeklyStats, setWeeklyStats] = useState<DailyStats[]>([])
  const [dailyCalorieGoal] = useState(2000) // TODO: Make this configurable

  useEffect(() => {
    loadMeals()
    loadWeeklyStats()
  }, [selectedDate])

  const loadMeals = () => {
    if (viewMode === 'calendar') {
      const startDate = startOfWeek(selectedDate, { locale: ja })
      const endDate = addDays(startDate, 6)
      setMeals(MealStorage.getMealsByDateRange(startDate, endDate))
    } else {
      // Load last 30 days for list view
      const endDate = new Date()
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - 30)
      setMeals(MealStorage.getMealsByDateRange(startDate, endDate))
    }
  }

  const loadWeeklyStats = () => {
    setWeeklyStats(MealStorage.getWeeklyStats(selectedDate))
  }

  const handleDeleteMeal = (mealId: string) => {
    if (confirm('この食事記録を削除しますか？')) {
      MealStorage.deleteMeal(mealId)
      loadMeals()
      loadWeeklyStats()
    }
  }

  const getMealIcon = (mealType: MealRecord['mealType']) => {
    switch (mealType) {
      case 'breakfast':
        return <Coffee className="w-4 h-4" />
      case 'lunch':
        return <Sun className="w-4 h-4" />
      case 'dinner':
        return <Moon className="w-4 h-4" />
      case 'snack':
        return <Cookie className="w-4 h-4" />
    }
  }

  const getMealTypeName = (mealType: MealRecord['mealType']) => {
    switch (mealType) {
      case 'breakfast':
        return '朝食'
      case 'lunch':
        return '昼食'
      case 'dinner':
        return '夕食'
      case 'snack':
        return '間食'
    }
  }

  const renderCalendarView = () => {
    const startDate = startOfWeek(selectedDate, { locale: ja })
    const days = Array.from({ length: 7 }, (_, i) => addDays(startDate, i))

    return (
      <div className="space-y-4">
        {/* Week Navigation */}
        <div className="flex justify-between items-center">
          <Button
            variant="outline"
            onClick={() => setSelectedDate(addDays(selectedDate, -7))}
          >
            前週
          </Button>
          <h3 className="text-lg font-semibold">
            {format(startDate, 'yyyy年MM月dd日', { locale: ja })} - {format(days[6], 'MM月dd日', { locale: ja })}
          </h3>
          <Button
            variant="outline"
            onClick={() => setSelectedDate(addDays(selectedDate, 7))}
          >
            翌週
          </Button>
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-2">
          {days.map((day, index) => {
            const dayMeals = meals.filter(meal => 
              isSameDay(new Date(meal.date), day)
            )
            const dayStats = weeklyStats[index]
            const isToday = isSameDay(day, new Date())

            return (
              <Card
                key={day.toISOString()}
                className={`${isToday ? 'ring-2 ring-primary' : ''}`}
              >
                <CardHeader className="p-3">
                  <div className="text-center">
                    <div className="text-sm text-gray-500">
                      {format(day, 'E', { locale: ja })}
                    </div>
                    <div className="text-lg font-semibold">
                      {format(day, 'd')}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-3 space-y-2">
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {dayStats?.totalCalories || 0}
                    </div>
                    <div className="text-xs text-gray-500">kcal</div>
                    
                    {/* Progress bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div
                        className="bg-primary h-2 rounded-full"
                        style={{
                          width: `${Math.min(
                            ((dayStats?.totalCalories || 0) / dailyCalorieGoal) * 100,
                            100
                          )}%`
                        }}
                      />
                    </div>
                  </div>

                  {/* Meal indicators */}
                  <div className="space-y-1">
                    {dayMeals.map(meal => (
                      <div
                        key={meal.id}
                        className="flex items-center justify-between text-xs p-1 bg-gray-50 rounded cursor-pointer hover:bg-gray-100"
                        onClick={() => onEditMeal?.(meal)}
                      >
                        <div className="flex items-center gap-1">
                          {getMealIcon(meal.mealType)}
                          <span>{meal.totalCalories}kcal</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Weekly Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">週間サマリー</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-500">総カロリー</div>
                <div className="text-xl font-semibold">
                  {weeklyStats.reduce((sum, day) => sum + day.totalCalories, 0)}kcal
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-500">平均カロリー</div>
                <div className="text-xl font-semibold">
                  {Math.round(
                    weeklyStats.reduce((sum, day) => sum + day.totalCalories, 0) / 7
                  )}kcal
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-500">総タンパク質</div>
                <div className="text-xl font-semibold">
                  {weeklyStats.reduce((sum, day) => sum + day.nutrition.protein, 0).toFixed(1)}g
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-500">食事回数</div>
                <div className="text-xl font-semibold">
                  {weeklyStats.reduce((sum, day) => sum + day.mealCount, 0)}回
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const renderListView = () => {
    const mealsByDate = meals.reduce((acc, meal) => {
      const dateKey = format(new Date(meal.date), 'yyyy-MM-dd')
      if (!acc[dateKey]) {
        acc[dateKey] = []
      }
      acc[dateKey].push(meal)
      return acc
    }, {} as Record<string, MealRecord[]>)

    const sortedDates = Object.keys(mealsByDate).sort((a, b) => b.localeCompare(a))

    return (
      <div className="space-y-4">
        {sortedDates.map(dateKey => {
          const dayMeals = mealsByDate[dateKey]
          const date = new Date(dateKey)
          const dayTotal = dayMeals.reduce((sum, meal) => sum + meal.totalCalories, 0)

          return (
            <Card key={dateKey}>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle className="text-base">
                    {format(date, 'yyyy年MM月dd日 (E)', { locale: ja })}
                  </CardTitle>
                  <div className="text-lg font-semibold">{dayTotal}kcal</div>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                {dayMeals.map(meal => (
                  <div
                    key={meal.id}
                    className="p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          {getMealIcon(meal.mealType)}
                          <span className="font-medium">
                            {getMealTypeName(meal.mealType)}
                          </span>
                          <span className="text-sm text-gray-500">
                            {format(new Date(meal.date), 'HH:mm')}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600">
                          {meal.foods.map(food => food.name).join(', ')}
                        </div>
                        <div className="flex gap-4 mt-2 text-sm">
                          <span>{meal.totalCalories}kcal</span>
                          {meal.totalNutrition && (
                            <>
                              <span>P: {meal.totalNutrition.protein.toFixed(1)}g</span>
                              <span>C: {meal.totalNutrition.carbs.toFixed(1)}g</span>
                              <span>F: {meal.totalNutrition.fat.toFixed(1)}g</span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {onEditMeal && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => onEditMeal(meal)}
                          >
                            <Edit2 className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDeleteMeal(meal.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )
        })}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* View Mode Toggle */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">食事履歴</h2>
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'calendar' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('calendar')}
          >
            <Calendar className="w-4 h-4 mr-2" />
            カレンダー
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('list')}
          >
            <List className="w-4 h-4 mr-2" />
            リスト
          </Button>
        </div>
      </div>

      {/* Content */}
      {viewMode === 'calendar' ? renderCalendarView() : renderListView()}
    </div>
  )
}