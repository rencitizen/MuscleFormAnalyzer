'use client'

import { useState, useEffect } from 'react'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { ChevronLeft, Plus, Dumbbell, Clock, Calendar, TrendingUp } from 'lucide-react'
import Link from 'next/link'
import { TrainingRecord } from '../../components/training/TrainingRecord'
import { RoutineManager } from '../../components/training/RoutineManager'
import { TrainingHistory } from '../../components/training/TrainingHistory'

export default function TrainingPage() {
  const [activeTab, setActiveTab] = useState<'record' | 'routines' | 'history'>('record')

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon">
                <ChevronLeft className="w-5 h-5" />
              </Button>
            </Link>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Dumbbell className="w-6 h-6" />
              トレーニング記録
            </h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* タブナビゲーション */}
        <div className="flex gap-2 mb-6 border-b">
          <button
            onClick={() => setActiveTab('record')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'record'
                ? 'text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            記録
          </button>
          <button
            onClick={() => setActiveTab('routines')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'routines'
                ? 'text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            ルーティン
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'history'
                ? 'text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            履歴
          </button>
        </div>

        {/* コンテンツエリア */}
        <div className="max-w-4xl mx-auto">
          {activeTab === 'record' && <TrainingRecord />}
          {activeTab === 'routines' && <RoutineManager />}
          {activeTab === 'history' && <TrainingHistory />}
        </div>
      </main>
    </div>
  )
}