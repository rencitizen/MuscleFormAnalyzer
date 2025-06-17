'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  TrendingUp,
  Weight,
  Ruler,
  Activity,
  Calendar,
  Plus,
  Target,
  Award,
  LineChart,
  Camera
} from 'lucide-react'
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts'

interface Measurement {
  date: string
  weight?: number
  bodyFat?: number
  muscleMass?: number
  chest?: number
  waist?: number
  hips?: number
  biceps?: number
  thighs?: number
  calves?: number
}

interface TrainingRecord {
  date: string
  exercise: string
  weight: number
  reps: number
  sets: number
}

interface Achievement {
  id: string
  title: string
  description: string
  achieved: boolean
  date?: string
  icon: string
}

export default function ProgressTrackingPage() {
  const [newMeasurement, setNewMeasurement] = useState<Partial<Measurement>>({
    date: new Date().toISOString().split('T')[0]
  })
  const [selectedPeriod, setSelectedPeriod] = useState('3months')
  const [selectedMetric, setSelectedMetric] = useState('weight')

  // サンプルデータ（実際はAPIから取得）
  const measurements: Measurement[] = [
    { date: '2024-01-01', weight: 75, bodyFat: 20, muscleMass: 60 },
    { date: '2024-01-15', weight: 74.5, bodyFat: 19.5, muscleMass: 60.2 },
    { date: '2024-02-01', weight: 74, bodyFat: 19, muscleMass: 60.5 },
    { date: '2024-02-15', weight: 73.8, bodyFat: 18.5, muscleMass: 60.8 },
    { date: '2024-03-01', weight: 73.5, bodyFat: 18, muscleMass: 61 },
    { date: '2024-03-15', weight: 73.2, bodyFat: 17.5, muscleMass: 61.3 }
  ]

  const trainingRecords: TrainingRecord[] = [
    { date: '2024-03-10', exercise: 'ベンチプレス', weight: 80, reps: 10, sets: 3 },
    { date: '2024-03-12', exercise: 'スクワット', weight: 100, reps: 8, sets: 4 },
    { date: '2024-03-14', exercise: 'デッドリフト', weight: 120, reps: 5, sets: 5 }
  ]

  const achievements: Achievement[] = [
    {
      id: '1',
      title: '初めての測定',
      description: '最初の身体測定を記録',
      achieved: true,
      date: '2024-01-01',
      icon: 'star'
    },
    {
      id: '2',
      title: '10kg減量達成',
      description: '目標体重に到達',
      achieved: true,
      date: '2024-03-01',
      icon: 'trophy'
    },
    {
      id: '3',
      title: '体脂肪率15%以下',
      description: '理想的な体脂肪率を達成',
      achieved: false,
      icon: 'target'
    },
    {
      id: '4',
      title: '100日連続記録',
      description: '100日間毎日記録を継続',
      achieved: false,
      icon: 'calendar'
    }
  ]

  const currentStats = {
    weight: 73.2,
    weightChange: -1.8,
    bodyFat: 17.5,
    bodyFatChange: -2.5,
    muscleMass: 61.3,
    muscleMassChange: +1.3
  }

  const goals = {
    targetWeight: 70,
    targetBodyFat: 15,
    targetDate: '2024-06-01'
  }

  const chartData = measurements.map(m => ({
    date: new Date(m.date).toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' }),
    体重: m.weight,
    体脂肪率: m.bodyFat,
    筋肉量: m.muscleMass
  }))

  const saveMeasurement = () => {
    console.log('Saving measurement:', newMeasurement)
    // API呼び出し実装予定
  }

  const metrics = [
    { value: 'weight', label: '体重' },
    { value: 'bodyFat', label: '体脂肪率' },
    { value: 'muscleMass', label: '筋肉量' }
  ]

  const periods = [
    { value: '1month', label: '1ヶ月' },
    { value: '3months', label: '3ヶ月' },
    { value: '6months', label: '6ヶ月' },
    { value: '1year', label: '1年' }
  ]

  return (
    <div className="container mx-auto px-4 py-8 pb-24 md:pb-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">プログレス追跡</h1>
        <p className="text-muted-foreground">あなたの成長を可視化し、目標達成をサポート</p>
      </div>

      {/* 現在の統計 */}
      <div className="grid gap-4 md:grid-cols-3 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Weight className="w-4 h-4" />
              現在の体重
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold">{currentStats.weight} kg</p>
              <Badge variant={currentStats.weightChange < 0 ? "default" : "secondary"}>
                {currentStats.weightChange > 0 ? '+' : ''}{currentStats.weightChange} kg
              </Badge>
            </div>
            <Progress 
              value={(goals.targetWeight - currentStats.weight) / (goals.targetWeight - 75) * 100} 
              className="mt-2"
            />
            <p className="text-xs text-muted-foreground mt-1">
              目標: {goals.targetWeight} kg
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="w-4 h-4" />
              体脂肪率
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold">{currentStats.bodyFat} %</p>
              <Badge variant="default">
                {currentStats.bodyFatChange} %
              </Badge>
            </div>
            <Progress 
              value={(20 - currentStats.bodyFat) / (20 - goals.targetBodyFat) * 100} 
              className="mt-2"
            />
            <p className="text-xs text-muted-foreground mt-1">
              目標: {goals.targetBodyFat} %
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              筋肉量
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold">{currentStats.muscleMass} kg</p>
              <Badge variant="default">
                +{currentStats.muscleMassChange} kg
              </Badge>
            </div>
            <Progress value={75} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-1">
              順調に増加中
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="chart" className="space-y-4">
        <TabsList>
          <TabsTrigger value="chart">
            <LineChart className="w-4 h-4 mr-2" />
            グラフ
          </TabsTrigger>
          <TabsTrigger value="input">
            <Plus className="w-4 h-4 mr-2" />
            記録入力
          </TabsTrigger>
          <TabsTrigger value="photos">
            <Camera className="w-4 h-4 mr-2" />
            写真比較
          </TabsTrigger>
          <TabsTrigger value="achievements">
            <Award className="w-4 h-4 mr-2" />
            実績
          </TabsTrigger>
        </TabsList>

        <TabsContent value="chart">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>進捗グラフ</CardTitle>
                <div className="flex gap-2">
                  <Select value={selectedMetric} onValueChange={setSelectedMetric}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {metrics.map(metric => (
                        <SelectItem key={metric.value} value={metric.value}>
                          {metric.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {periods.map(period => (
                        <SelectItem key={period.value} value={period.value}>
                          {period.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsLineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    {selectedMetric === 'weight' && (
                      <Line type="monotone" dataKey="体重" stroke="#3b82f6" strokeWidth={2} />
                    )}
                    {selectedMetric === 'bodyFat' && (
                      <Line type="monotone" dataKey="体脂肪率" stroke="#ef4444" strokeWidth={2} />
                    )}
                    {selectedMetric === 'muscleMass' && (
                      <Line type="monotone" dataKey="筋肉量" stroke="#10b981" strokeWidth={2} />
                    )}
                  </RechartsLineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="input">
          <Card>
            <CardHeader>
              <CardTitle>測定値を記録</CardTitle>
              <CardDescription>
                定期的に記録することで、正確な進捗を把握できます
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="md:col-span-3">
                  <Label htmlFor="date">日付</Label>
                  <Input
                    id="date"
                    type="date"
                    value={newMeasurement.date}
                    onChange={(e) => setNewMeasurement({...newMeasurement, date: e.target.value})}
                  />
                </div>

                <div>
                  <Label htmlFor="weight">体重 (kg)</Label>
                  <Input
                    id="weight"
                    type="number"
                    step="0.1"
                    value={newMeasurement.weight || ''}
                    onChange={(e) => setNewMeasurement({...newMeasurement, weight: parseFloat(e.target.value)})}
                  />
                </div>

                <div>
                  <Label htmlFor="bodyFat">体脂肪率 (%)</Label>
                  <Input
                    id="bodyFat"
                    type="number"
                    step="0.1"
                    value={newMeasurement.bodyFat || ''}
                    onChange={(e) => setNewMeasurement({...newMeasurement, bodyFat: parseFloat(e.target.value)})}
                  />
                </div>

                <div>
                  <Label htmlFor="muscleMass">筋肉量 (kg)</Label>
                  <Input
                    id="muscleMass"
                    type="number"
                    step="0.1"
                    value={newMeasurement.muscleMass || ''}
                    onChange={(e) => setNewMeasurement({...newMeasurement, muscleMass: parseFloat(e.target.value)})}
                  />
                </div>

                <div className="md:col-span-3">
                  <h4 className="font-semibold mb-3">体の各部位のサイズ (cm)</h4>
                </div>

                <div>
                  <Label htmlFor="chest">胸囲</Label>
                  <Input
                    id="chest"
                    type="number"
                    step="0.1"
                    value={newMeasurement.chest || ''}
                    onChange={(e) => setNewMeasurement({...newMeasurement, chest: parseFloat(e.target.value)})}
                  />
                </div>

                <div>
                  <Label htmlFor="waist">ウエスト</Label>
                  <Input
                    id="waist"
                    type="number"
                    step="0.1"
                    value={newMeasurement.waist || ''}
                    onChange={(e) => setNewMeasurement({...newMeasurement, waist: parseFloat(e.target.value)})}
                  />
                </div>

                <div>
                  <Label htmlFor="hips">ヒップ</Label>
                  <Input
                    id="hips"
                    type="number"
                    step="0.1"
                    value={newMeasurement.hips || ''}
                    onChange={(e) => setNewMeasurement({...newMeasurement, hips: parseFloat(e.target.value)})}
                  />
                </div>

                <div>
                  <Label htmlFor="biceps">上腕</Label>
                  <Input
                    id="biceps"
                    type="number"
                    step="0.1"
                    value={newMeasurement.biceps || ''}
                    onChange={(e) => setNewMeasurement({...newMeasurement, biceps: parseFloat(e.target.value)})}
                  />
                </div>

                <div>
                  <Label htmlFor="thighs">太もも</Label>
                  <Input
                    id="thighs"
                    type="number"
                    step="0.1"
                    value={newMeasurement.thighs || ''}
                    onChange={(e) => setNewMeasurement({...newMeasurement, thighs: parseFloat(e.target.value)})}
                  />
                </div>

                <div>
                  <Label htmlFor="calves">ふくらはぎ</Label>
                  <Input
                    id="calves"
                    type="number"
                    step="0.1"
                    value={newMeasurement.calves || ''}
                    onChange={(e) => setNewMeasurement({...newMeasurement, calves: parseFloat(e.target.value)})}
                  />
                </div>
              </div>

              <Button className="w-full mt-6" onClick={saveMeasurement}>
                <Plus className="w-4 h-4 mr-2" />
                記録を保存
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="photos">
          <Card>
            <CardHeader>
              <CardTitle>写真比較</CardTitle>
              <CardDescription>
                視覚的な変化を確認しましょう
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <h4 className="font-semibold mb-2">開始時（2024年1月1日）</h4>
                  <div className="aspect-[3/4] bg-gray-100 rounded-lg flex items-center justify-center">
                    <Camera className="w-12 h-12 text-gray-400" />
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">現在（2024年3月15日）</h4>
                  <div className="aspect-[3/4] bg-gray-100 rounded-lg flex items-center justify-center">
                    <Camera className="w-12 h-12 text-gray-400" />
                  </div>
                </div>
              </div>
              <Button className="w-full mt-4" variant="outline">
                <Camera className="w-4 h-4 mr-2" />
                写真をアップロード
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="achievements">
          <Card>
            <CardHeader>
              <CardTitle>実績とマイルストーン</CardTitle>
              <CardDescription>
                あなたの努力の成果です
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {achievements.map((achievement) => (
                  <div
                    key={achievement.id}
                    className={`flex items-start gap-4 p-4 rounded-lg border ${
                      achievement.achieved ? 'bg-primary/5 border-primary/20' : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      achievement.achieved ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'
                    }`}>
                      {achievement.icon === 'star' && <Award className="w-6 h-6" />}
                      {achievement.icon === 'trophy' && <Award className="w-6 h-6" />}
                      {achievement.icon === 'target' && <Target className="w-6 h-6" />}
                      {achievement.icon === 'calendar' && <Calendar className="w-6 h-6" />}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold">{achievement.title}</h4>
                      <p className="text-sm text-muted-foreground">{achievement.description}</p>
                      {achievement.achieved && achievement.date && (
                        <p className="text-xs text-muted-foreground mt-1">
                          達成日: {new Date(achievement.date).toLocaleDateString('ja-JP')}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 最近のトレーニング記録 */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>最近のトレーニング記録</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {trainingRecords.map((record, index) => (
              <div key={index} className="flex justify-between items-center py-2 border-b last:border-0">
                <div>
                  <p className="font-medium">{record.exercise}</p>
                  <p className="text-sm text-muted-foreground">
                    {new Date(record.date).toLocaleDateString('ja-JP')}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium">{record.weight} kg</p>
                  <p className="text-sm text-muted-foreground">
                    {record.sets} × {record.reps}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}