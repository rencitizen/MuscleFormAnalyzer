'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Info,
  Loader2,
  TrendingUp,
  TrendingDown,
  Zap,
  Target,
  Award,
  Flame
} from 'lucide-react'
import { Card } from './card'
import { Progress } from './progress'
import { Badge } from './badge'

interface FeedbackItem {
  id: string
  type: 'success' | 'error' | 'warning' | 'info' | 'progress'
  title: string
  message?: string
  progress?: number
  duration?: number
  icon?: React.ElementType
  action?: {
    label: string
    onClick: () => void
  }
}

interface RealtimeFeedbackProps {
  items: FeedbackItem[]
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'center'
  className?: string
}

const iconMap = {
  success: CheckCircle2,
  error: XCircle,
  warning: AlertCircle,
  info: Info,
  progress: Loader2
}

const colorMap = {
  success: 'text-green-500 bg-green-50 dark:bg-green-900/20',
  error: 'text-red-500 bg-red-50 dark:bg-red-900/20',
  warning: 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20',
  info: 'text-blue-500 bg-blue-50 dark:bg-blue-900/20',
  progress: 'text-purple-500 bg-purple-50 dark:bg-purple-900/20'
}

export function RealtimeFeedback({ 
  items, 
  position = 'top-right',
  className 
}: RealtimeFeedbackProps) {
  const [visibleItems, setVisibleItems] = useState<FeedbackItem[]>([])

  useEffect(() => {
    setVisibleItems(items)
    
    items.forEach(item => {
      if (item.duration && item.duration > 0) {
        setTimeout(() => {
          setVisibleItems(prev => prev.filter(i => i.id !== item.id))
        }, item.duration)
      }
    })
  }, [items])

  const positionClasses = {
    'top-right': 'top-20 right-4',
    'top-left': 'top-20 left-4',
    'bottom-right': 'bottom-20 right-4',
    'bottom-left': 'bottom-20 left-4',
    'center': 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'
  }

  return (
    <div className={cn(
      'fixed z-50 space-y-2 max-w-sm',
      positionClasses[position],
      className
    )}>
      <AnimatePresence>
        {visibleItems.map((item) => {
          const Icon = item.icon || iconMap[item.type]
          
          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <Card className={cn(
                'p-4 shadow-lg border-0',
                colorMap[item.type]
              )}>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0">
                    {item.type === 'progress' ? (
                      <Icon className="h-5 w-5 animate-spin" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>
                  <div className="flex-1 space-y-1">
                    <p className="font-medium text-sm">{item.title}</p>
                    {item.message && (
                      <p className="text-xs opacity-90">{item.message}</p>
                    )}
                    {item.progress !== undefined && (
                      <Progress value={item.progress} className="h-2 mt-2" />
                    )}
                    {item.action && (
                      <button
                        onClick={item.action.onClick}
                        className="text-xs font-medium underline mt-2 hover:no-underline"
                      >
                        {item.action.label}
                      </button>
                    )}
                  </div>
                </div>
              </Card>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}

interface LiveStatsProps {
  stats: {
    label: string
    value: number | string
    unit?: string
    trend?: 'up' | 'down' | 'neutral'
    icon?: React.ElementType
    color?: string
  }[]
  className?: string
}

export function LiveStats({ stats, className }: LiveStatsProps) {
  return (
    <div className={cn('grid gap-2', className)}>
      {stats.map((stat, index) => {
        const Icon = stat.icon || Zap
        const trendIcon = stat.trend === 'up' ? TrendingUp : stat.trend === 'down' ? TrendingDown : null
        
        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary/70 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className={cn(
                'h-8 w-8 rounded-full flex items-center justify-center',
                stat.color || 'bg-primary/10'
              )}>
                <Icon className="h-4 w-4" />
              </div>
              <span className="text-sm font-medium">{stat.label}</span>
            </div>
            <div className="flex items-center gap-2">
              <motion.span
                key={stat.value}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-lg font-bold"
              >
                {stat.value}
                {stat.unit && <span className="text-sm font-normal ml-1">{stat.unit}</span>}
              </motion.span>
              {trendIcon && (
                <trendIcon className={cn(
                  'h-4 w-4',
                  stat.trend === 'up' ? 'text-green-500' : 'text-red-500'
                )} />
              )}
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

interface AchievementToastProps {
  achievement: {
    title: string
    description: string
    icon?: React.ElementType
    rarity?: 'common' | 'rare' | 'epic' | 'legendary'
  }
  onClose?: () => void
}

export function AchievementToast({ achievement, onClose }: AchievementToastProps) {
  const Icon = achievement.icon || Award
  
  const rarityColors = {
    common: 'from-gray-400 to-gray-600',
    rare: 'from-blue-400 to-blue-600',
    epic: 'from-purple-400 to-purple-600',
    legendary: 'from-yellow-400 to-orange-600'
  }
  
  const rarityGlow = {
    common: '',
    rare: 'shadow-blue-500/50',
    epic: 'shadow-purple-500/50',
    legendary: 'shadow-yellow-500/50 animate-pulse'
  }

  return (
    <motion.div
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      exit={{ scale: 0, opacity: 0 }}
      transition={{ type: "spring", duration: 0.5 }}
      className="relative"
    >
      <Card className={cn(
        'p-6 text-center space-y-3 shadow-2xl border-0 bg-gradient-to-br',
        rarityColors[achievement.rarity || 'common'],
        rarityGlow[achievement.rarity || 'common']
      )}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="inline-block"
        >
          <div className="h-16 w-16 rounded-full bg-white/20 backdrop-blur flex items-center justify-center mx-auto">
            <Icon className="h-8 w-8 text-white" />
          </div>
        </motion.div>
        
        <div className="space-y-1">
          <h3 className="text-xl font-bold text-white">{achievement.title}</h3>
          <p className="text-sm text-white/90">{achievement.description}</p>
        </div>
        
        <Badge 
          variant="secondary" 
          className="bg-white/20 text-white border-white/30"
        >
          新しい実績を解除！
        </Badge>
        
        {onClose && (
          <button
            onClick={onClose}
            className="absolute top-2 right-2 text-white/70 hover:text-white"
          >
            <XCircle className="h-4 w-4" />
          </button>
        )}
      </Card>
    </motion.div>
  )
}

interface ProgressIndicatorProps {
  label: string
  value: number
  maxValue: number
  showPercentage?: boolean
  icon?: React.ElementType
  color?: string
  size?: 'sm' | 'md' | 'lg'
}

export function ProgressIndicator({
  label,
  value,
  maxValue,
  showPercentage = true,
  icon: Icon = Target,
  color = 'bg-primary',
  size = 'md'
}: ProgressIndicatorProps) {
  const percentage = Math.min((value / maxValue) * 100, 100)
  
  const sizeClasses = {
    sm: 'h-6',
    md: 'h-8',
    lg: 'h-10'
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">{label}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold">
            {value}/{maxValue}
          </span>
          {showPercentage && (
            <Badge variant="secondary" className="text-xs">
              {percentage.toFixed(0)}%
            </Badge>
          )}
        </div>
      </div>
      <div className={cn('relative rounded-full bg-secondary overflow-hidden', sizeClasses[size])}>
        <motion.div
          className={cn('absolute inset-y-0 left-0 flex items-center justify-center', color)}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        >
          {percentage >= 50 && (
            <Flame className="h-4 w-4 text-white animate-pulse ml-auto mr-2" />
          )}
        </motion.div>
      </div>
    </div>
  )
}