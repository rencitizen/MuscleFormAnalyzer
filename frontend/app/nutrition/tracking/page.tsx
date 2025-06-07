'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { MealHistory } from '@/components/nutrition/MealHistory'
import { NutritionDashboard } from '@/components/nutrition/NutritionDashboard'
import { Button } from '@/components/ui/button'
import { Plus, BarChart3, Calendar } from 'lucide-react'
import Link from 'next/link'

export default function NutritionTrackingPage() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="container mx-auto p-4 max-w-7xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">栄養管理ダッシュボード</h1>
        <Link href="/nutrition">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            食事を記録
          </Button>
        </Link>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-2 max-w-md">
          <TabsTrigger value="dashboard" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            ダッシュボード
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            履歴
          </TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-4">
          <NutritionDashboard />
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <MealHistory />
        </TabsContent>
      </Tabs>
    </div>
  )
}