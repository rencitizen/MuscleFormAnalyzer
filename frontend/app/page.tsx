'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Progress } from '../components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { 
  Camera, 
  Utensils,
  TrendingUp,
  Activity,
  Target,
  Zap,
  Trophy,
  Calendar,
  BarChart3,
  Users,
  MessageSquare,
  Brain,
  Dumbbell,
  Heart,
  Flame,
  Timer,
  Award,
  AlertCircle,
  ArrowRight,
  Plus,
  Sparkles,
  Microscope,
  Clock,
  Moon,
  Sun
} from 'lucide-react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { useLanguage } from '@/contexts/LanguageContext'
import { cn } from '@/lib/utils'

interface QuickStat {
  label: string
  labelEn: string
  value: string | number
  unit?: string
  icon: React.ElementType
  trend?: number
  color: string
}

interface Feature {
  title: string
  titleEn: string
  description: string
  descriptionEn: string
  icon: React.ElementType
  href: string
  badge?: string
  isNew?: boolean
  isPro?: boolean
  color: string
  stats?: {
    label: string
    value: string | number
  }[]
}

export default function HomePage() {
  const { user, loading } = useAuth()
  const { language } = useLanguage()
  const router = useRouter()
  const [greeting, setGreeting] = useState('こんにちは')
  const [greetingEn, setGreetingEn] = useState('Hello')
  const [timeOfDay, setTimeOfDay] = useState<'morning' | 'afternoon' | 'evening' | 'night'>('morning')

  const t = (ja: string, en: string) => language === 'ja' ? ja : en

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    }
  }, [user, loading, router])

  useEffect(() => {
    const hour = new Date().getHours()
    if (hour < 6) {
      setGreeting('おはようございます')
      setGreetingEn('Good Morning')
      setTimeOfDay('night')
    } else if (hour < 12) {
      setGreeting('おはようございます')
      setGreetingEn('Good Morning')
      setTimeOfDay('morning')
    } else if (hour < 18) {
      setGreeting('こんにちは')
      setGreetingEn('Good Afternoon')
      setTimeOfDay('afternoon')
    } else {
      setGreeting('こんばんは')
      setGreetingEn('Good Evening')
      setTimeOfDay('evening')
    }
  }, [])

  const quickStats: QuickStat[] = [
    {
      label: '今日のカロリー',
      labelEn: "Today's Calories",
      value: 1850,
      unit: 'kcal',
      icon: Flame,
      trend: -5,
      color: 'text-orange-500'
    },
    {
      label: '運動時間',
      labelEn: 'Exercise Time',
      value: 45,
      unit: '分',
      icon: Timer,
      trend: 15,
      color: 'text-blue-500'
    },
    {
      label: 'フォームスコア',
      labelEn: 'Form Score',
      value: 88,
      unit: '%',
      icon: Trophy,
      trend: 3,
      color: 'text-green-500'
    },
    {
      label: '連続日数',
      labelEn: 'Streak',
      value: 12,
      unit: '日',
      icon: Zap,
      color: 'text-purple-500'
    }
  ]

  const mainFeatures: Feature[] = [
    {
      title: 'フォーム分析',
      titleEn: 'Form Analysis',
      description: 'AIがリアルタイムでフォームを解析し、改善点を提案',
      descriptionEn: 'AI analyzes your form in real-time and suggests improvements',
      icon: Camera,
      href: '/analyze',
      badge: 'AI',
      isNew: true,
      color: 'from-blue-500 to-cyan-500',
      stats: [
        { label: '精度', value: '98%' },
        { label: '検出速度', value: '30fps' }
      ]
    },
    {
      title: '栄養管理',
      titleEn: 'Nutrition',
      description: '食事記録と栄養バランスの最適化',
      descriptionEn: 'Meal tracking and nutrition optimization',
      icon: Utensils,
      href: '/nutrition',
      color: 'from-green-500 to-emerald-500',
      stats: [
        { label: '登録食品', value: '10万+' },
        { label: '栄養素', value: '15種類' }
      ]
    },
    {
      title: '進捗追跡',
      titleEn: 'Progress',
      description: '成長を可視化し、モチベーションを維持',
      descriptionEn: 'Visualize growth and maintain motivation',
      icon: TrendingUp,
      href: '/progress',
      color: 'from-purple-500 to-pink-500',
      stats: [
        { label: '指標', value: '20+' },
        { label: 'グラフ', value: '自動生成' }
      ]
    },
    {
      title: 'AIトレーナー',
      titleEn: 'AI Trainer',
      description: 'あなた専用のトレーニングプランを生成',
      descriptionEn: 'Generate personalized training plans',
      icon: Brain,
      href: '/training-generator',
      badge: 'PRO',
      isPro: true,
      color: 'from-indigo-500 to-purple-500',
      stats: [
        { label: 'プラン', value: '∞' },
        { label: '最適化', value: 'リアルタイム' }
      ]
    }
  ]

  const advancedFeatures: Feature[] = [
    {
      title: '科学的分析',
      titleEn: 'Scientific Analysis',
      description: '体組成・代謝・ホルモンバランスの詳細分析',
      descriptionEn: 'Detailed analysis of body composition, metabolism, and hormones',
      icon: Microscope,
      href: '/v3',
      badge: 'V3',
      isNew: true,
      color: 'from-red-500 to-orange-500'
    },
    {
      title: 'エクササイズDB',
      titleEn: 'Exercise DB',
      description: '1000種類以上の運動データベース',
      descriptionEn: 'Database of 1000+ exercises',
      icon: Dumbbell,
      href: '/exercises',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      title: 'トレーニング',
      titleEn: 'Training',
      description: 'ワークアウトの実行と記録',
      descriptionEn: 'Execute and record workouts',
      icon: Activity,
      href: '/training',
      color: 'from-teal-500 to-green-500'
    },
    {
      title: '科学的指標',
      titleEn: 'Scientific Metrics',
      description: '高度なフィットネス指標の分析',
      descriptionEn: 'Advanced fitness metrics analysis',
      icon: Sparkles,
      href: '/dashboard/scientific',
      color: 'from-violet-500 to-purple-500'
    }
  ]

  const todaysTasks = [
    {
      title: '胸と三頭筋のトレーニング',
      titleEn: 'Chest & Triceps Training',
      time: '18:00',
      duration: '45分',
      durationEn: '45 min',
      icon: Dumbbell,
      completed: false
    },
    {
      title: 'プロテイン摂取',
      titleEn: 'Protein Intake',
      time: '19:00',
      duration: '目標: 30g',
      durationEn: 'Target: 30g',
      icon: Utensils,
      completed: false
    },
    {
      title: '睡眠記録',
      titleEn: 'Sleep Tracking',
      time: '23:00',
      duration: '目標: 8時間',
      durationEn: 'Target: 8 hours',
      icon: Moon,
      completed: false
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-background/95">
      <main className="container mx-auto px-4 py-6 md:py-8 space-y-6 md:space-y-8">
        {/* Enhanced Welcome Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center md:text-left"
        >
          <div className="flex items-center gap-2 justify-center md:justify-start mb-2">
            {timeOfDay === 'morning' && <Sun className="h-5 w-5 text-yellow-500" />}
            {timeOfDay === 'afternoon' && <Sun className="h-5 w-5 text-orange-500" />}
            {timeOfDay === 'evening' && <Moon className="h-5 w-5 text-indigo-500" />}
            {timeOfDay === 'night' && <Moon className="h-5 w-5 text-purple-500" />}
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
              {t(greeting, greetingEn)}、{user?.displayName || t('アスリート', 'Athlete')}
            </h1>
          </div>
          <p className="text-muted-foreground">
            {t('今日も目標に向かって頑張りましょう！', "Let's work towards your goals today!")}
          </p>
        </motion.div>

        {/* Quick Stats Dashboard */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4"
        >
          {quickStats.map((stat, index) => (
            <Card key={index} className="relative overflow-hidden group hover:shadow-lg transition-all">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <stat.icon className={cn("h-5 w-5", stat.color)} />
                  {stat.trend && (
                    <Badge variant={stat.trend > 0 ? "default" : "secondary"} className="text-xs">
                      {stat.trend > 0 ? '+' : ''}{stat.trend}%
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">{t(stat.label, stat.labelEn)}</p>
                <p className="text-2xl font-bold">
                  {stat.value}
                  {stat.unit && <span className="text-sm font-normal text-muted-foreground ml-1">{stat.unit}</span>}
                </p>
              </CardContent>
              <div className={cn("absolute inset-0 bg-gradient-to-r opacity-5 group-hover:opacity-10 transition-opacity", stat.color)} />
            </Card>
          ))}
        </motion.div>

        {/* Today's Tasks */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  {t('今日のタスク', "Today's Tasks")}
                </CardTitle>
                <Link href="/training/new">
                  <Button size="sm" variant="outline" className="gap-2">
                    <Plus className="h-4 w-4" />
                    {t('追加', 'Add')}
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {todaysTasks.map((task, index) => (
                <div key={index} className="flex items-center gap-4 p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors">
                  <div className={cn(
                    "h-10 w-10 rounded-full flex items-center justify-center",
                    task.completed ? "bg-green-500/20" : "bg-primary/20"
                  )}>
                    <task.icon className={cn(
                      "h-5 w-5",
                      task.completed ? "text-green-500" : "text-primary"
                    )} />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{t(task.title, task.titleEn)}</p>
                    <p className="text-sm text-muted-foreground">
                      {task.time} • {t(task.duration, task.durationEn)}
                    </p>
                  </div>
                  <Button
                    size="sm"
                    variant={task.completed ? "secondary" : "default"}
                    className="ml-auto"
                  >
                    {task.completed ? t('完了', 'Done') : t('開始', 'Start')}
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        {/* Main Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">{t('主要機能', 'Main Features')}</h2>
            <Link href="/features">
              <Button variant="ghost" size="sm" className="gap-2">
                {t('すべて見る', 'View All')}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {mainFeatures.map((feature, index) => (
              <Link key={index} href={feature.href}>
                <Card className="group cursor-pointer hover:shadow-xl transition-all h-full relative overflow-hidden">
                  <div className={cn(
                    "absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-10 transition-opacity",
                    feature.color
                  )} />
                  <CardHeader>
                    <div className="flex items-start justify-between mb-2">
                      <div className={cn(
                        "h-12 w-12 rounded-lg bg-gradient-to-br flex items-center justify-center text-white shadow-lg",
                        feature.color
                      )}>
                        <feature.icon className="h-6 w-6" />
                      </div>
                      <div className="flex gap-1">
                        {feature.badge && (
                          <Badge variant="secondary" className="text-xs">
                            {feature.badge}
                          </Badge>
                        )}
                        {feature.isNew && (
                          <Badge variant="destructive" className="text-xs">
                            NEW
                          </Badge>
                        )}
                      </div>
                    </div>
                    <CardTitle className="text-lg">{t(feature.title, feature.titleEn)}</CardTitle>
                    <CardDescription className="text-sm">
                      {t(feature.description, feature.descriptionEn)}
                    </CardDescription>
                  </CardHeader>
                  {feature.stats && (
                    <CardContent>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        {feature.stats.map((stat, i) => (
                          <div key={i} className="text-center p-2 rounded bg-secondary/50">
                            <p className="text-xs text-muted-foreground">{stat.label}</p>
                            <p className="font-semibold">{stat.value}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  )}
                </Card>
              </Link>
            ))}
          </div>
        </motion.div>

        {/* Advanced Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2 className="text-xl font-semibold mb-4">{t('高度な機能', 'Advanced Features')}</h2>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            {advancedFeatures.map((feature, index) => (
              <Link key={index} href={feature.href}>
                <Card className="group cursor-pointer hover:shadow-lg transition-all h-full">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "h-10 w-10 rounded-lg bg-gradient-to-br flex items-center justify-center text-white",
                        feature.color
                      )}>
                        <feature.icon className="h-5 w-5" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-base">{t(feature.title, feature.titleEn)}</CardTitle>
                          {feature.badge && (
                            <Badge variant="secondary" className="text-xs">
                              {feature.badge}
                            </Badge>
                          )}
                          {feature.isNew && (
                            <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                          )}
                        </div>
                        <CardDescription className="text-xs mt-1">
                          {t(feature.description, feature.descriptionEn)}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              </Link>
            ))}
          </div>
        </motion.div>

        {/* Weekly Progress Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  {t('今週の進捗', 'Weekly Progress')}
                </CardTitle>
                <Link href="/progress">
                  <Button variant="ghost" size="sm" className="gap-2">
                    {t('詳細', 'Details')}
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">{t('トレーニング完了率', 'Training Completion')}</span>
                    <span className="text-sm text-muted-foreground">85%</span>
                  </div>
                  <Progress value={85} className="h-2" />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">{t('栄養目標達成率', 'Nutrition Goals')}</span>
                    <span className="text-sm text-muted-foreground">92%</span>
                  </div>
                  <Progress value={92} className="h-2" />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">{t('フォーム改善', 'Form Improvement')}</span>
                    <span className="text-sm text-muted-foreground">+12%</span>
                  </div>
                  <Progress value={72} className="h-2" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Community & Motivation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid gap-4 md:grid-cols-2"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                {t('コミュニティ', 'Community')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Award className="h-8 w-8 text-yellow-500" />
                  <div>
                    <p className="font-medium">{t('今週のトップアスリート', 'Top Athlete This Week')}</p>
                    <p className="text-sm text-muted-foreground">{t('あなたは全体の上位15%です！', "You're in the top 15%!")}</p>
                  </div>
                </div>
                <Link href="/community">
                  <Button variant="outline" className="w-full gap-2">
                    <MessageSquare className="h-4 w-4" />
                    {t('コミュニティに参加', 'Join Community')}
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="h-5 w-5" />
                {t('今日のモチベーション', "Today's Motivation")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <blockquote className="italic text-muted-foreground mb-2">
                "{t('成功は日々の小さな努力の積み重ねだ', 'Success is the sum of small efforts repeated day in and day out')}"
              </blockquote>
              <p className="text-sm text-right">- Robert Collier</p>
              <Button variant="outline" className="w-full mt-4 gap-2">
                <Sparkles className="h-4 w-4" />
                {t('もっと見る', 'View More')}
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </main>
    </div>
  )
}