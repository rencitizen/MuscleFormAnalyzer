'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Bug, Lightbulb, MessageSquare, AlertCircle, TrendingUp, Users, BarChart3, Download } from 'lucide-react'
import toast from 'react-hot-toast'

interface FeedbackItem {
  type: 'bug' | 'feature' | 'usability' | 'other'
  severity: 'low' | 'medium' | 'high'
  description: string
  screenshot?: string
  userAgent: string
  timestamp: string
  userId?: string
  pageUrl: string
  sessionId: string
}

interface FeedbackStats {
  total: number
  byType: Record<string, number>
  bySeverity: Record<string, number>
}

const typeIcons = {
  bug: Bug,
  feature: Lightbulb,
  usability: MessageSquare,
  other: AlertCircle
}

const typeLabels = {
  bug: 'バグ報告',
  feature: '機能要望',
  usability: '使いやすさ',
  other: 'その他'
}

const severityColors = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-800'
}

export default function FeedbackDashboard() {
  const [feedback, setFeedback] = useState<FeedbackItem[]>([])
  const [stats, setStats] = useState<FeedbackStats | null>(null)
  const [filter, setFilter] = useState<string>('all')
  const [loading, setLoading] = useState(true)

  // フィードバックデータの取得
  useEffect(() => {
    fetchFeedback()
  }, [filter])

  const fetchFeedback = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filter !== 'all') {
        params.append('type', filter)
      }
      
      const response = await fetch(`/api/feedback?${params}`)
      const data = await response.json()
      
      setFeedback(data.items)
      setStats(data.stats)
    } catch (error) {
      console.error('Failed to fetch feedback:', error)
      toast.error('データの取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  // CSVエクスポート
  const exportToCSV = () => {
    const headers = ['Type', 'Severity', 'Description', 'URL', 'Timestamp']
    const rows = feedback.map(item => [
      item.type,
      item.severity,
      item.description.replace(/,/g, ';'),
      item.pageUrl,
      new Date(item.timestamp).toLocaleString()
    ])
    
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `feedback-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    
    toast.success('CSVをエクスポートしました')
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">フィードバックダッシュボード</h1>
          <p className="text-gray-600 mt-2">ユーザーからのフィードバックを管理・分析</p>
        </div>
        <Button onClick={exportToCSV} variant="outline">
          <Download className="h-4 w-4 mr-2" />
          CSVエクスポート
        </Button>
      </div>

      {/* 統計カード */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">総フィードバック数</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
              <p className="text-xs text-gray-600 mt-1">
                <TrendingUp className="h-3 w-3 inline mr-1" />
                全期間
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">バグ報告</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.byType.bug || 0}</div>
              <div className="mt-1">
                <Badge className={severityColors.high} variant="secondary">
                  高: {stats.bySeverity.high || 0}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">機能要望</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.byType.feature || 0}</div>
              <p className="text-xs text-gray-600 mt-1">
                <Lightbulb className="h-3 w-3 inline mr-1" />
                新機能リクエスト
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">UX改善</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.byType.usability || 0}</div>
              <p className="text-xs text-gray-600 mt-1">
                <Users className="h-3 w-3 inline mr-1" />
                使いやすさの提案
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* フィルターとリスト */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>フィードバック一覧</CardTitle>
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="フィルター" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">すべて</SelectItem>
                <SelectItem value="bug">バグ報告</SelectItem>
                <SelectItem value="feature">機能要望</SelectItem>
                <SelectItem value="usability">使いやすさ</SelectItem>
                <SelectItem value="other">その他</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">読み込み中...</div>
          ) : feedback.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              フィードバックがありません
            </div>
          ) : (
            <div className="space-y-4">
              {feedback.map((item, index) => {
                const Icon = typeIcons[item.type]
                return (
                  <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className="mt-1">
                          <Icon className="h-5 w-5 text-gray-600" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary">{typeLabels[item.type]}</Badge>
                            {item.type === 'bug' && (
                              <Badge className={severityColors[item.severity]} variant="secondary">
                                {item.severity}
                              </Badge>
                            )}
                            <span className="text-sm text-gray-500">
                              {new Date(item.timestamp).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-gray-800 mb-2">{item.description}</p>
                          <div className="text-xs text-gray-500">
                            <a href={item.pageUrl} className="hover:underline" target="_blank" rel="noopener noreferrer">
                              {item.pageUrl}
                            </a>
                          </div>
                        </div>
                      </div>
                      {item.screenshot && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => window.open(item.screenshot, '_blank')}
                        >
                          スクリーンショット
                        </Button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}