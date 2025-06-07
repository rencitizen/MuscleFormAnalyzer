'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Calendar, Trash2 } from 'lucide-react'
import Link from 'next/link'

interface MealRecord {
  foods: Array<{
    name: string
    quantity: string
    calories: number
  }>
  total_calories: number
  date: string
  image?: string
}

export default function MealHistoryPage() {
  const [meals, setMeals] = useState<MealRecord[]>([])

  useEffect(() => {
    // Load meals from localStorage
    const storedMeals = JSON.parse(localStorage.getItem('meals') || '[]')
    setMeals(storedMeals.sort((a: MealRecord, b: MealRecord) => 
      new Date(b.date).getTime() - new Date(a.date).getTime()
    ))
  }, [])

  const handleDeleteMeal = (index: number) => {
    const updatedMeals = meals.filter((_, i) => i !== index)
    setMeals(updatedMeals)
    localStorage.setItem('meals', JSON.stringify(updatedMeals))
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getDailyTotal = (date: string) => {
    const targetDate = new Date(date).toDateString()
    return meals
      .filter(meal => new Date(meal.date).toDateString() === targetDate)
      .reduce((total, meal) => total + meal.total_calories, 0)
  }

  const getUniqueDates = () => {
    const dates = new Set(meals.map(meal => new Date(meal.date).toDateString()))
    return Array.from(dates)
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">食事履歴 / Meal History</h1>
        <Link href="/nutrition">
          <Button>新しい食事を記録 / Record New Meal</Button>
        </Link>
      </div>

      {meals.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-gray-500">まだ食事記録がありません</p>
            <p className="text-gray-500">No meal records yet</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {getUniqueDates().map(dateString => (
            <div key={dateString} className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  {new Date(dateString).toLocaleDateString('ja-JP', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </h2>
                <span className="text-lg font-bold">
                  合計: {getDailyTotal(dateString)} kcal
                </span>
              </div>

              {meals
                .filter(meal => new Date(meal.date).toDateString() === dateString)
                .map((meal, index) => {
                  const originalIndex = meals.indexOf(meal)
                  return (
                    <Card key={originalIndex}>
                      <CardHeader>
                        <div className="flex justify-between items-start">
                          <div>
                            <CardTitle className="text-base">
                              {new Date(meal.date).toLocaleTimeString('ja-JP', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </CardTitle>
                            <CardDescription>
                              {meal.total_calories} kcal
                            </CardDescription>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteMeal(originalIndex)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {meal.foods.map((food, foodIndex) => (
                            <div
                              key={foodIndex}
                              className="flex justify-between items-center text-sm"
                            >
                              <span>{food.name}</span>
                              <span className="text-gray-500">
                                {food.quantity} - {food.calories} kcal
                              </span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}