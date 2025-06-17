'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { 
  Dumbbell,
  Calendar,
  Clock,
  TrendingUp,
  RefreshCw,
  Download,
  Save,
  ChevronRight
} from 'lucide-react'

interface TrainingInput {
  experience: string
  goal: string
  frequency: string
  equipment: string[]
  limitations: string
  focusAreas: string[]
}

interface Exercise {
  name: string
  sets: number
  reps: string
  rest: string
  weight: string
  alternatives: string[]
}

interface WorkoutDay {
  day: string
  name: string
  exercises: Exercise[]
  duration: string
}

interface TrainingProgram {
  weeks: number
  phase: string
  schedule: WorkoutDay[]
  progressionPlan: string[]
  notes: string[]
}

export default function TrainingGeneratorPage() {
  const [input, setInput] = useState<TrainingInput>({
    experience: 'intermediate',
    goal: 'strength',
    frequency: '4',
    equipment: ['barbell', 'dumbbell', 'pullup'],
    limitations: '',
    focusAreas: []
  })

  const [program, setProgram] = useState<TrainingProgram | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const experienceLevels = [
    { value: 'beginner', label: '初心者（1年未満）' },
    { value: 'intermediate', label: '中級者（1-3年）' },
    { value: 'advanced', label: '上級者（3年以上）' }
  ]

  const goals = [
    { value: 'strength', label: '筋力向上' },
    { value: 'hypertrophy', label: '筋肥大' },
    { value: 'endurance', label: '筋持久力' },
    { value: 'powerlifting', label: 'パワーリフティング' },
    { value: 'athletic', label: 'アスレチック' }
  ]

  const equipment = [
    { value: 'barbell', label: 'バーベル' },
    { value: 'dumbbell', label: 'ダンベル' },
    { value: 'cable', label: 'ケーブル' },
    { value: 'pullup', label: '懸垂バー' },
    { value: 'dips', label: 'ディップスバー' },
    { value: 'bands', label: 'レジスタンスバンド' },
    { value: 'bodyweight', label: '自重のみ' }
  ]

  const bodyParts = [
    { value: 'chest', label: '胸' },
    { value: 'back', label: '背中' },
    { value: 'legs', label: '脚' },
    { value: 'shoulders', label: '肩' },
    { value: 'arms', label: '腕' },
    { value: 'core', label: '体幹' }
  ]

  const generateProgram = async () => {
    setIsGenerating(true)

    // API呼び出しのシミュレーション
    setTimeout(() => {
      setProgram({
        weeks: 12,
        phase: '筋力向上期',
        schedule: [
          {
            day: '月曜日',
            name: 'プッシュデイ（胸・肩・三頭）',
            duration: '60-75分',
            exercises: [
              {
                name: 'ベンチプレス',
                sets: 5,
                reps: '5',
                rest: '3分',
                weight: '80-85% 1RM',
                alternatives: ['ダンベルプレス', 'インクラインプレス']
              },
              {
                name: 'オーバーヘッドプレス',
                sets: 4,
                reps: '6-8',
                rest: '2.5分',
                weight: '75-80% 1RM',
                alternatives: ['ダンベルショルダープレス', 'アーノルドプレス']
              },
              {
                name: 'インクラインダンベルプレス',
                sets: 3,
                reps: '8-10',
                rest: '2分',
                weight: '70-75% 1RM',
                alternatives: ['インクラインバーベルプレス', 'ケーブルフライ']
              },
              {
                name: 'サイドレイズ',
                sets: 4,
                reps: '12-15',
                rest: '1.5分',
                weight: '軽め',
                alternatives: ['ケーブルサイドレイズ', 'フロントレイズ']
              },
              {
                name: 'トライセプスエクステンション',
                sets: 3,
                reps: '10-12',
                rest: '1.5分',
                weight: '中程度',
                alternatives: ['ケーブルプッシュダウン', 'ディップス']
              }
            ]
          },
          {
            day: '火曜日',
            name: 'プルデイ（背中・二頭）',
            duration: '60-75分',
            exercises: [
              {
                name: 'デッドリフト',
                sets: 5,
                reps: '5',
                rest: '3分',
                weight: '80-85% 1RM',
                alternatives: ['ルーマニアンデッドリフト', 'ラックプル']
              },
              {
                name: '懸垂（加重）',
                sets: 4,
                reps: '6-8',
                rest: '2.5分',
                weight: '+10-20kg',
                alternatives: ['ラットプルダウン', 'アシスト懸垂']
              },
              {
                name: 'ベントオーバーロウ',
                sets: 4,
                reps: '8-10',
                rest: '2分',
                weight: '70-75% 1RM',
                alternatives: ['ダンベルロウ', 'ケーブルロウ']
              },
              {
                name: 'フェイスプル',
                sets: 3,
                reps: '15-20',
                rest: '1.5分',
                weight: '軽め',
                alternatives: ['リアデルトフライ', 'バンドプルアパート']
              },
              {
                name: 'バーベルカール',
                sets: 3,
                reps: '8-10',
                rest: '1.5分',
                weight: '中程度',
                alternatives: ['ダンベルカール', 'ハンマーカール']
              }
            ]
          },
          {
            day: '木曜日',
            name: 'レッグデイ',
            duration: '75-90分',
            exercises: [
              {
                name: 'スクワット',
                sets: 5,
                reps: '5',
                rest: '3分',
                weight: '80-85% 1RM',
                alternatives: ['フロントスクワット', 'ゴブレットスクワット']
              },
              {
                name: 'ルーマニアンデッドリフト',
                sets: 4,
                reps: '8-10',
                rest: '2.5分',
                weight: '70-75% 1RM',
                alternatives: ['スティッフレッグデッドリフト', 'グッドモーニング']
              },
              {
                name: 'レッグプレス',
                sets: 4,
                reps: '10-12',
                rest: '2分',
                weight: '中〜高重量',
                alternatives: ['ブルガリアンスプリットスクワット', 'ランジ']
              },
              {
                name: 'レッグカール',
                sets: 3,
                reps: '12-15',
                rest: '1.5分',
                weight: '中程度',
                alternatives: ['ノルディックカール', 'グルートハムレイズ']
              },
              {
                name: 'カーフレイズ',
                sets: 4,
                reps: '15-20',
                rest: '1分',
                weight: '中程度',
                alternatives: ['シーテッドカーフレイズ', 'ドンキーカーフレイズ']
              }
            ]
          },
          {
            day: '土曜日',
            name: 'アッパーボディ（筋力）',
            duration: '60-75分',
            exercises: [
              {
                name: 'インクラインベンチプレス',
                sets: 5,
                reps: '3-5',
                rest: '3分',
                weight: '85-90% 1RM',
                alternatives: ['フラットベンチプレス', 'ダンベルプレス']
              },
              {
                name: 'ペンドレイロウ',
                sets: 5,
                reps: '3-5',
                rest: '3分',
                weight: '85-90% 1RM',
                alternatives: ['ベントオーバーロウ', 'シールロウ']
              },
              {
                name: 'クローズグリップベンチプレス',
                sets: 4,
                reps: '6-8',
                rest: '2.5分',
                weight: '75-80% 1RM',
                alternatives: ['ディップス', 'JMプレス']
              },
              {
                name: 'バーベルカール',
                sets: 4,
                reps: '6-8',
                rest: '2分',
                weight: '75-80% 1RM',
                alternatives: ['プリーチャーカール', 'ケーブルカール']
              }
            ]
          }
        ],
        progressionPlan: [
          '週1-4: 基礎筋力構築期 - 重量に慣れる',
          '週5-8: 強度増加期 - 毎週2.5-5%重量増加',
          '週9-11: ピーク期 - 高強度・低ボリューム',
          '週12: ディロード - 回復とテスト'
        ],
        notes: [
          'メイン種目（ベンチ、スクワット、デッドリフト）は必ず実施',
          'ウォームアップは軽い重量から徐々に上げる',
          '睡眠を7-9時間確保する',
          'タンパク質を体重×2g摂取する',
          '疲労が蓄積したら休息日を追加'
        ]
      })
      setIsGenerating(false)
    }, 2000)
  }

  const exportProgram = () => {
    if (!program) return
    
    const dataStr = JSON.stringify(program, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `training_program_${new Date().toISOString()}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  return (
    <div className="container mx-auto px-4 py-8 pb-24 md:pb-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">トレーニングプログラム生成</h1>
        <p className="text-muted-foreground">あなたに最適なトレーニングプログラムを作成します</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* 左側：入力フォーム */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>プログラム設定</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>経験レベル</Label>
                <RadioGroup
                  value={input.experience}
                  onValueChange={(value) => setInput({...input, experience: value})}
                >
                  {experienceLevels.map((level) => (
                    <div key={level.value} className="flex items-center space-x-2">
                      <RadioGroupItem value={level.value} id={level.value} />
                      <Label htmlFor={level.value}>{level.label}</Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>

              <div>
                <Label htmlFor="goal">目標</Label>
                <Select
                  value={input.goal}
                  onValueChange={(value) => setInput({...input, goal: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {goals.map((goal) => (
                      <SelectItem key={goal.value} value={goal.value}>
                        {goal.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="frequency">週あたりのトレーニング日数</Label>
                <Select
                  value={input.frequency}
                  onValueChange={(value) => setInput({...input, frequency: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="2">2日</SelectItem>
                    <SelectItem value="3">3日</SelectItem>
                    <SelectItem value="4">4日</SelectItem>
                    <SelectItem value="5">5日</SelectItem>
                    <SelectItem value="6">6日</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>利用可能な器具</Label>
                <div className="space-y-2">
                  {equipment.map((item) => (
                    <div key={item.value} className="flex items-center space-x-2">
                      <Checkbox
                        id={item.value}
                        checked={input.equipment.includes(item.value)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setInput({...input, equipment: [...input.equipment, item.value]})
                          } else {
                            setInput({...input, equipment: input.equipment.filter(e => e !== item.value)})
                          }
                        }}
                      />
                      <Label htmlFor={item.value}>{item.label}</Label>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label>重点的に鍛えたい部位</Label>
                <div className="space-y-2">
                  {bodyParts.map((part) => (
                    <div key={part.value} className="flex items-center space-x-2">
                      <Checkbox
                        id={part.value}
                        checked={input.focusAreas.includes(part.value)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setInput({...input, focusAreas: [...input.focusAreas, part.value]})
                          } else {
                            setInput({...input, focusAreas: input.focusAreas.filter(a => a !== part.value)})
                          }
                        }}
                      />
                      <Label htmlFor={part.value}>{part.label}</Label>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label htmlFor="limitations">制限事項・怪我など</Label>
                <Textarea
                  id="limitations"
                  value={input.limitations}
                  onChange={(e) => setInput({...input, limitations: e.target.value})}
                  placeholder="例: 腰痛があるため、重いデッドリフトは避けたい"
                  rows={3}
                />
              </div>

              <Button onClick={generateProgram} className="w-full" disabled={isGenerating}>
                {isGenerating ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    生成中...
                  </>
                ) : (
                  <>
                    <Dumbbell className="w-4 h-4 mr-2" />
                    プログラム生成
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* 右側：生成されたプログラム */}
        <div className="lg:col-span-2">
          {program ? (
            <Card>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>トレーニングプログラム</CardTitle>
                    <CardDescription>
                      {program.weeks}週間 / {program.phase}
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={exportProgram}>
                      <Download className="w-4 h-4 mr-2" />
                      エクスポート
                    </Button>
                    <Button size="sm">
                      <Save className="w-4 h-4 mr-2" />
                      保存
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="schedule" className="space-y-4">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="schedule">
                      <Calendar className="w-4 h-4 mr-2" />
                      スケジュール
                    </TabsTrigger>
                    <TabsTrigger value="progression">
                      <TrendingUp className="w-4 h-4 mr-2" />
                      進行計画
                    </TabsTrigger>
                    <TabsTrigger value="notes">
                      <ChevronRight className="w-4 h-4 mr-2" />
                      注意事項
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="schedule" className="space-y-4">
                    {program.schedule.map((day, index) => (
                      <Card key={index}>
                        <CardHeader>
                          <div className="flex justify-between items-center">
                            <CardTitle className="text-lg">{day.day}: {day.name}</CardTitle>
                            <Badge variant="secondary">
                              <Clock className="w-3 h-3 mr-1" />
                              {day.duration}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-3">
                            {day.exercises.map((exercise, exIndex) => (
                              <div key={exIndex} className="border-l-2 border-primary pl-4">
                                <div className="flex justify-between items-start">
                                  <div>
                                    <h4 className="font-semibold">{exercise.name}</h4>
                                    <p className="text-sm text-muted-foreground">
                                      {exercise.sets}セット × {exercise.reps}レップ / 休憩: {exercise.rest}
                                    </p>
                                    <p className="text-sm text-muted-foreground">
                                      重量: {exercise.weight}
                                    </p>
                                  </div>
                                </div>
                                {exercise.alternatives.length > 0 && (
                                  <div className="mt-2">
                                    <p className="text-xs text-muted-foreground">代替種目:</p>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {exercise.alternatives.map((alt, altIndex) => (
                                        <Badge key={altIndex} variant="outline" className="text-xs">
                                          {alt}
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </TabsContent>

                  <TabsContent value="progression">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">漸進性過負荷計画</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {program.progressionPlan.map((phase, index) => (
                            <div key={index} className="flex items-start gap-3">
                              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                                <span className="text-sm font-semibold">{index + 1}</span>
                              </div>
                              <p className="text-sm">{phase}</p>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="notes">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">重要な注意事項</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {program.notes.map((note, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <ChevronRight className="w-4 h-4 mt-0.5 text-primary flex-shrink-0" />
                              <span className="text-sm">{note}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          ) : (
            <Card className="h-full flex items-center justify-center min-h-[600px]">
              <CardContent>
                <div className="text-center">
                  <Dumbbell className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground">
                    設定を入力してプログラムを生成してください
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}