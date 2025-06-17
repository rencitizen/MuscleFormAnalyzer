'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { 
  Users,
  Activity,
  Server,
  AlertTriangle,
  TrendingUp,
  Database,
  Shield,
  Search,
  Download,
  RefreshCw,
  Ban,
  CheckCircle
} from 'lucide-react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

interface SystemStats {
  totalUsers: number
  activeUsers: number
  totalAnalyses: number
  storageUsed: number
  apiCalls: number
  errorRate: number
}

interface User {
  id: string
  name: string
  email: string
  status: 'active' | 'inactive' | 'banned'
  joinDate: string
  lastActive: string
  analysisCount: number
}

export default function AdminPage() {
  const { data: session } = useSession()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedPeriod, setSelectedPeriod] = useState('7days')

  // 管理者権限チェック
  useEffect(() => {
    if (session && session.user?.email !== 'admin@tenaxfit.com') {
      router.push('/dashboard')
    } else {
      setIsLoading(false)
    }
  }, [session, router])

  // サンプルデータ
  const systemStats: SystemStats = {
    totalUsers: 1234,
    activeUsers: 892,
    totalAnalyses: 15678,
    storageUsed: 85.4,
    apiCalls: 234567,
    errorRate: 0.12
  }

  const users: User[] = [
    {
      id: '1',
      name: '山田太郎',
      email: 'yamada@example.com',
      status: 'active',
      joinDate: '2024-01-15',
      lastActive: '2024-03-15',
      analysisCount: 45
    },
    {
      id: '2',
      name: '佐藤花子',
      email: 'sato@example.com',
      status: 'active',
      joinDate: '2024-02-01',
      lastActive: '2024-03-14',
      analysisCount: 32
    },
    {
      id: '3',
      name: '鈴木一郎',
      email: 'suzuki@example.com',
      status: 'inactive',
      joinDate: '2023-12-20',
      lastActive: '2024-02-28',
      analysisCount: 12
    }
  ]

  const activityData = [
    { date: '3/9', users: 820, analyses: 1450 },
    { date: '3/10', users: 850, analyses: 1520 },
    { date: '3/11', users: 880, analyses: 1600 },
    { date: '3/12', users: 910, analyses: 1680 },
    { date: '3/13', users: 890, analyses: 1650 },
    { date: '3/14', users: 920, analyses: 1720 },
    { date: '3/15', users: 892, analyses: 1690 }
  ]

  const apiUsageData = [
    { endpoint: '姿勢分析', calls: 45000 },
    { endpoint: '食事分析', calls: 38000 },
    { endpoint: '栄養計算', calls: 32000 },
    { endpoint: 'トレーニング生成', calls: 28000 },
    { endpoint: 'その他', calls: 12000 }
  ]

  const handleUserAction = (userId: string, action: 'ban' | 'activate') => {
    console.log(`${action} user ${userId}`)
    // API呼び出し実装予定
  }

  const exportData = () => {
    console.log('Exporting data...')
    // データエクスポート実装予定
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-[60vh]">
          <div className="text-center">
            <Shield className="w-12 h-12 mx-auto mb-4 text-muted-foreground animate-pulse" />
            <p className="text-muted-foreground">権限を確認しています...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">管理者ダッシュボード</h1>
        <p className="text-muted-foreground">システムの監視と管理</p>
      </div>

      {/* システム統計 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">総ユーザー数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{systemStats.totalUsers.toLocaleString()}</p>
            <p className="text-xs text-muted-foreground">+12% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">アクティブユーザー</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{systemStats.activeUsers.toLocaleString()}</p>
            <p className="text-xs text-muted-foreground">過去7日間</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">総分析数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{systemStats.totalAnalyses.toLocaleString()}</p>
            <p className="text-xs text-muted-foreground">累計</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">ストレージ使用率</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{systemStats.storageUsed}%</p>
            <p className="text-xs text-muted-foreground">500GB中</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">API呼び出し</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{(systemStats.apiCalls / 1000).toFixed(1)}k</p>
            <p className="text-xs text-muted-foreground">今月</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">エラー率</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{systemStats.errorRate}%</p>
            <Badge variant={systemStats.errorRate < 1 ? "default" : "destructive"}>
              {systemStats.errorRate < 1 ? "正常" : "要確認"}
            </Badge>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">
            <Activity className="w-4 h-4 mr-2" />
            概要
          </TabsTrigger>
          <TabsTrigger value="users">
            <Users className="w-4 h-4 mr-2" />
            ユーザー管理
          </TabsTrigger>
          <TabsTrigger value="system">
            <Server className="w-4 h-4 mr-2" />
            システム
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="w-4 h-4 mr-2" />
            セキュリティ
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>アクティビティ推移</CardTitle>
                <CardDescription>ユーザー数と分析数の推移</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={activityData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="users" stroke="#3b82f6" name="ユーザー" />
                      <Line type="monotone" dataKey="analyses" stroke="#10b981" name="分析数" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>API使用状況</CardTitle>
                <CardDescription>エンドポイント別の呼び出し数</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={apiUsageData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="endpoint" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="calls" fill="#8b5cf6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>最近のアラート</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>ストレージ容量警告</AlertTitle>
                  <AlertDescription>
                    ストレージ使用率が85%を超えました。容量の追加を検討してください。
                  </AlertDescription>
                </Alert>
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertTitle>システムアップデート完了</AlertTitle>
                  <AlertDescription>
                    v2.1.0へのアップデートが正常に完了しました。
                  </AlertDescription>
                </Alert>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>ユーザー一覧</CardTitle>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      type="text"
                      placeholder="ユーザーを検索"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 w-64"
                    />
                  </div>
                  <Button variant="outline" onClick={exportData}>
                    <Download className="w-4 h-4 mr-2" />
                    エクスポート
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="p-4 text-left">ユーザー</th>
                      <th className="p-4 text-left">ステータス</th>
                      <th className="p-4 text-left">登録日</th>
                      <th className="p-4 text-left">最終アクセス</th>
                      <th className="p-4 text-left">分析回数</th>
                      <th className="p-4 text-left">アクション</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id} className="border-b">
                        <td className="p-4">
                          <div>
                            <p className="font-medium">{user.name}</p>
                            <p className="text-sm text-muted-foreground">{user.email}</p>
                          </div>
                        </td>
                        <td className="p-4">
                          <Badge variant={
                            user.status === 'active' ? 'default' :
                            user.status === 'inactive' ? 'secondary' : 'destructive'
                          }>
                            {user.status === 'active' ? 'アクティブ' :
                             user.status === 'inactive' ? '非アクティブ' : '停止中'}
                          </Badge>
                        </td>
                        <td className="p-4 text-sm">
                          {new Date(user.joinDate).toLocaleDateString('ja-JP')}
                        </td>
                        <td className="p-4 text-sm">
                          {new Date(user.lastActive).toLocaleDateString('ja-JP')}
                        </td>
                        <td className="p-4 text-sm">{user.analysisCount}</td>
                        <td className="p-4">
                          <div className="flex gap-2">
                            {user.status !== 'banned' ? (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleUserAction(user.id, 'ban')}
                              >
                                <Ban className="w-4 h-4" />
                              </Button>
                            ) : (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleUserAction(user.id, 'activate')}
                              >
                                <CheckCircle className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>システム状態</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label>APIサーバー</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="default">稼働中</Badge>
                      <span className="text-sm text-muted-foreground">
                        レスポンスタイム: 124ms
                      </span>
                    </div>
                  </div>
                  <div>
                    <Label>データベース</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="default">正常</Badge>
                      <span className="text-sm text-muted-foreground">
                        接続数: 45/100
                      </span>
                    </div>
                  </div>
                  <div>
                    <Label>MediaPipeサービス</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="default">稼働中</Badge>
                      <span className="text-sm text-muted-foreground">
                        処理キュー: 3
                      </span>
                    </div>
                  </div>
                  <div>
                    <Label>ストレージ</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="secondary">警告</Badge>
                      <span className="text-sm text-muted-foreground">
                        427GB / 500GB使用中
                      </span>
                    </div>
                  </div>
                </div>

                <div className="pt-4">
                  <Button variant="outline" className="w-full">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    システム診断を実行
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>バックアップ設定</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>自動バックアップ</Label>
                  <Select defaultValue="daily">
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hourly">毎時</SelectItem>
                      <SelectItem value="daily">毎日</SelectItem>
                      <SelectItem value="weekly">毎週</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>最終バックアップ</Label>
                  <p className="text-sm text-muted-foreground mt-1">
                    2024年3月15日 03:00 - 成功
                  </p>
                </div>
                <Button className="w-full">
                  今すぐバックアップ
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="security">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>セキュリティログ</CardTitle>
                <CardDescription>最近のセキュリティイベント</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center py-2 border-b">
                    <div>
                      <p className="font-medium">管理者ログイン</p>
                      <p className="text-sm text-muted-foreground">
                        admin@tenaxfit.com - 成功
                      </p>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      5分前
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b">
                    <div>
                      <p className="font-medium">不正ログイン試行</p>
                      <p className="text-sm text-muted-foreground">
                        unknown@example.com - ブロック済み
                      </p>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      2時間前
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <div>
                      <p className="font-medium">API キー再生成</p>
                      <p className="text-sm text-muted-foreground">
                        システム管理者により実行
                      </p>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      昨日
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>セキュリティ設定</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>二要素認証</Label>
                  <p className="text-sm text-muted-foreground mt-1 mb-2">
                    管理者アカウントの二要素認証を有効化
                  </p>
                  <Button variant="outline">設定する</Button>
                </div>
                <div>
                  <Label>IPホワイトリスト</Label>
                  <p className="text-sm text-muted-foreground mt-1 mb-2">
                    管理画面へのアクセスを特定のIPアドレスに制限
                  </p>
                  <Button variant="outline">設定する</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}