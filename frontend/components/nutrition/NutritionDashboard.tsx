'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Progress } from '../ui/progress'
import { MealStorage, type DailyStats } from '../../lib/storage/mealStorage'
import { Line, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js'
import { format, subDays } from 'date-fns'
import { ja } from 'date-fns/locale'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface NutritionDashboardProps {
  dailyCalorieGoal?: number
  dailyProteinGoal?: number
}

export function NutritionDashboard({ 
  dailyCalorieGoal = 2000,
  dailyProteinGoal = 60 
}: NutritionDashboardProps) {
  const [last7DaysStats, setLast7DaysStats] = useState<DailyStats[]>([])
  const [todayStats, setTodayStats] = useState<DailyStats | null>(null)
  const [weeklyAverage, setWeeklyAverage] = useState({
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0
  })

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = () => {
    // Load last 7 days
    const stats: DailyStats[] = []
    for (let i = 6; i >= 0; i--) {
      const date = subDays(new Date(), i)
      stats.push(MealStorage.getDailyStats(date))
    }
    setLast7DaysStats(stats)

    // Today's stats
    setTodayStats(MealStorage.getDailyStats(new Date()))

    // Calculate weekly average
    const totals = stats.reduce(
      (acc, day) => ({
        calories: acc.calories + day.totalCalories,
        protein: acc.protein + day.nutrition.protein,
        carbs: acc.carbs + day.nutrition.carbs,
        fat: acc.fat + day.nutrition.fat
      }),
      { calories: 0, protein: 0, carbs: 0, fat: 0 }
    )

    setWeeklyAverage({
      calories: Math.round(totals.calories / 7),
      protein: Math.round(totals.protein / 7),
      carbs: Math.round(totals.carbs / 7),
      fat: Math.round(totals.fat / 7)
    })
  }

  const getTrendIcon = (current: number, average: number) => {
    const diff = ((current - average) / average) * 100
    if (diff > 5) return <TrendingUp className="w-4 h-4 text-green-500" />
    if (diff < -5) return <TrendingDown className="w-4 h-4 text-red-500" />
    return <Minus className="w-4 h-4 text-gray-400" />
  }

  const calorieChartData = {
    labels: last7DaysStats.map(stat => 
      format(new Date(stat.date), 'MM/dd', { locale: ja })
    ),
    datasets: [
      {
        label: 'カロリー',
        data: last7DaysStats.map(stat => stat.totalCalories),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        tension: 0.1
      },
      {
        label: '目標',
        data: Array(7).fill(dailyCalorieGoal),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderDash: [5, 5]
      }
    ]
  }

  const macroChartData = {
    labels: last7DaysStats.map(stat => 
      format(new Date(stat.date), 'MM/dd', { locale: ja })
    ),
    datasets: [
      {
        label: 'タンパク質',
        data: last7DaysStats.map(stat => stat.nutrition.protein),
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
      },
      {
        label: '炭水化物',
        data: last7DaysStats.map(stat => stat.nutrition.carbs),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
      },
      {
        label: '脂質',
        data: last7DaysStats.map(stat => stat.nutrition.fat),
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
      }
    ]
  }

  const chartOptions: ChartOptions<'line' | 'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Today's Summary */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>今日のカロリー</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {todayStats?.totalCalories || 0} kcal
            </div>
            <Progress
              value={(todayStats?.totalCalories || 0) / dailyCalorieGoal * 100}
              className="mt-2"
            />
            <p className="text-xs text-gray-500 mt-1">
              目標: {dailyCalorieGoal} kcal
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>今日のタンパク質</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {todayStats?.nutrition.protein.toFixed(1) || 0} g
            </div>
            <Progress
              value={(todayStats?.nutrition.protein || 0) / dailyProteinGoal * 100}
              className="mt-2"
            />
            <p className="text-xs text-gray-500 mt-1">
              目標: {dailyProteinGoal} g
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>今日の食事回数</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {todayStats?.mealCount || 0} 回
            </div>
            <div className="flex items-center gap-1 mt-2">
              {getTrendIcon(todayStats?.mealCount || 0, 3)}
              <span className="text-xs text-gray-500">
                推奨: 3-4回
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>週間平均カロリー</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {weeklyAverage.calories} kcal
            </div>
            <div className="flex items-center gap-1 mt-2">
              {getTrendIcon(weeklyAverage.calories, dailyCalorieGoal)}
              <span className="text-xs text-gray-500">
                目標比: {((weeklyAverage.calories / dailyCalorieGoal) * 100).toFixed(0)}%
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>カロリー推移</CardTitle>
            <CardDescription>過去7日間のカロリー摂取量</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <Line data={calorieChartData} options={chartOptions} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>栄養素バランス</CardTitle>
            <CardDescription>過去7日間のPFCバランス</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <Bar data={macroChartData} options={chartOptions} />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Weekly Summary */}
      <Card>
        <CardHeader>
          <CardTitle>週間サマリー</CardTitle>
          <CardDescription>過去7日間の平均値</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <div className="text-sm text-gray-500">平均カロリー</div>
              <div className="text-xl font-semibold mt-1">
                {weeklyAverage.calories} kcal
              </div>
              <div className="text-xs text-gray-400 mt-1">
                合計: {weeklyAverage.calories * 7} kcal
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">平均タンパク質</div>
              <div className="text-xl font-semibold mt-1">
                {weeklyAverage.protein} g
              </div>
              <div className="text-xs text-gray-400 mt-1">
                合計: {weeklyAverage.protein * 7} g
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">平均炭水化物</div>
              <div className="text-xl font-semibold mt-1">
                {weeklyAverage.carbs} g
              </div>
              <div className="text-xs text-gray-400 mt-1">
                合計: {weeklyAverage.carbs * 7} g
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">平均脂質</div>
              <div className="text-xl font-semibold mt-1">
                {weeklyAverage.fat} g
              </div>
              <div className="text-xs text-gray-400 mt-1">
                合計: {weeklyAverage.fat * 7} g
              </div>
            </div>
          </div>

          {/* PFC Ratio */}
          <div className="mt-6">
            <div className="text-sm text-gray-500 mb-2">平均PFCバランス</div>
            <div className="flex gap-2">
              <div className="flex-1">
                <div className="text-xs text-gray-500">P</div>
                <Progress 
                  value={weeklyAverage.protein * 4 / (weeklyAverage.protein * 4 + weeklyAverage.carbs * 4 + weeklyAverage.fat * 9) * 100} 
                  className="h-2"
                />
                <div className="text-xs text-gray-500 mt-1">
                  {(weeklyAverage.protein * 4 / (weeklyAverage.protein * 4 + weeklyAverage.carbs * 4 + weeklyAverage.fat * 9) * 100).toFixed(0)}%
                </div>
              </div>
              <div className="flex-1">
                <div className="text-xs text-gray-500">C</div>
                <Progress 
                  value={weeklyAverage.carbs * 4 / (weeklyAverage.protein * 4 + weeklyAverage.carbs * 4 + weeklyAverage.fat * 9) * 100} 
                  className="h-2"
                />
                <div className="text-xs text-gray-500 mt-1">
                  {(weeklyAverage.carbs * 4 / (weeklyAverage.protein * 4 + weeklyAverage.carbs * 4 + weeklyAverage.fat * 9) * 100).toFixed(0)}%
                </div>
              </div>
              <div className="flex-1">
                <div className="text-xs text-gray-500">F</div>
                <Progress 
                  value={weeklyAverage.fat * 9 / (weeklyAverage.protein * 4 + weeklyAverage.carbs * 4 + weeklyAverage.fat * 9) * 100} 
                  className="h-2"
                />
                <div className="text-xs text-gray-500 mt-1">
                  {(weeklyAverage.fat * 9 / (weeklyAverage.protein * 4 + weeklyAverage.carbs * 4 + weeklyAverage.fat * 9) * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}