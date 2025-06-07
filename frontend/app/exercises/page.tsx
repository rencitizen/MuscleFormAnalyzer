'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Search, Dumbbell, ChevronRight } from 'lucide-react'
import Link from 'next/link'

interface Exercise {
  id: string
  name: string
  category: string
  subcategory: string
  primary_muscles: string[]
  secondary_muscles: string[]
  description?: string
}

export default function ExercisesPage() {
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchExercises()
  }, [])

  const fetchExercises = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/exercises/all')
      if (response.ok) {
        const data = await response.json()
        setExercises(data.exercises || [])
      }
    } catch (error) {
      console.error('Failed to fetch exercises:', error)
    } finally {
      setLoading(false)
    }
  }

  const categories = [
    { id: 'all', name: '全て', icon: '💪' },
    { id: 'chest', name: '胸', icon: '🎯' },
    { id: 'back', name: '背中', icon: '🔙' },
    { id: 'legs', name: '脚', icon: '🦵' },
    { id: 'shoulders', name: '肩', icon: '🤷' },
    { id: 'arms', name: '腕', icon: '💪' },
    { id: 'core', name: '体幹', icon: '🎯' },
  ]

  const filteredExercises = exercises.filter(exercise => {
    const matchesSearch = exercise.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || exercise.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const exercisesByCategory = filteredExercises.reduce((acc, exercise) => {
    if (!acc[exercise.category]) {
      acc[exercise.category] = []
    }
    acc[exercise.category].push(exercise)
    return acc
  }, {} as Record<string, Exercise[]>)

  return (
    <div className="container mx-auto p-4 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">エクササイズデータベース</h1>
        <p className="text-muted-foreground">
          300種類以上のトレーニング種目から選択
        </p>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="種目名で検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Category Tabs */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="mb-6">
        <TabsList className="grid grid-cols-4 lg:grid-cols-7 h-auto">
          {categories.map(category => (
            <TabsTrigger 
              key={category.id} 
              value={category.id}
              className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
            >
              <span className="mr-1">{category.icon}</span>
              {category.name}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Exercise List */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(exercisesByCategory).map(([category, exercises]) => (
            <div key={category}>
              <h2 className="text-xl font-semibold mb-3 capitalize">
                {categories.find(c => c.id === category)?.name || category}
              </h2>
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                {exercises.map(exercise => (
                  <Card 
                    key={exercise.id}
                    className="cursor-pointer hover:shadow-md transition-shadow"
                  >
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base flex items-center justify-between">
                        <span>{exercise.name}</span>
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-sm text-muted-foreground space-y-1">
                        <p>主働筋: {exercise.primary_muscles.join(', ')}</p>
                        {exercise.secondary_muscles.length > 0 && (
                          <p>補助筋: {exercise.secondary_muscles.join(', ')}</p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredExercises.length === 0 && (
        <Card className="text-center py-12">
          <CardContent>
            <Dumbbell className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">
              該当する種目が見つかりません
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}