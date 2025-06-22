'use client'

import React, { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Activity, 
  Brain, 
  Zap, 
  Target,
  TrendingUp,
  AlertCircle,
  CheckCircle2
} from 'lucide-react'

interface UnifiedScores {
  physics_efficiency: number
  biological_optimality: number
  system_stability: number
  mathematical_optimization: number
  overall: number
}

interface FeedbackItem {
  type: string
  priority: string
  message: string
  metric: string
  current_value: number
  target_value: number
}

interface UnifiedTheoryDashboardProps {
  scores: UnifiedScores
  feedback: FeedbackItem[]
  physics: any
  biomechanics: any
  optimization: any
  isLoading?: boolean
}

export default function UnifiedTheoryDashboard({
  scores,
  feedback,
  physics,
  biomechanics,
  optimization,
  isLoading = false
}: UnifiedTheoryDashboardProps) {
  const [selectedTab, setSelectedTab] = useState('overview')

  const scoreCategories = [
    {
      name: 'Physics Efficiency',
      score: scores.physics_efficiency,
      icon: Zap,
      color: 'text-blue-500',
      description: 'Energy optimization and biomechanical efficiency'
    },
    {
      name: 'Biological Optimality',
      score: scores.biological_optimality,
      icon: Brain,
      color: 'text-green-500',
      description: 'Neuromuscular coordination and movement quality'
    },
    {
      name: 'System Stability',
      score: scores.system_stability,
      icon: Activity,
      color: 'text-purple-500',
      description: 'Movement stability and adaptability'
    },
    {
      name: 'Mathematical Optimization',
      score: scores.mathematical_optimization,
      icon: Target,
      color: 'text-orange-500',
      description: 'Personal form optimization based on constraints'
    }
  ]

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500'
      case 'medium': return 'bg-yellow-500'
      case 'low': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-6">
      {/* Overall Score Card */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">Unified Theory Analysis</h2>
          <div className="text-right">
            <div className="text-3xl font-bold">
              <span className={getScoreColor(scores.overall)}>
                {(scores.overall * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-sm text-gray-600">Overall Score</p>
          </div>
        </div>
        
        <Progress 
          value={scores.overall * 100} 
          className="h-3 mb-6"
        />

        {/* Score Categories Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {scoreCategories.map((category) => (
            <div key={category.name} className="space-y-2">
              <div className="flex items-center gap-2">
                <category.icon className={`w-5 h-5 ${category.color}`} />
                <span className="font-medium text-sm">{category.name}</span>
              </div>
              <Progress 
                value={category.score * 100} 
                className="h-2"
              />
              <p className="text-xs text-gray-600">{category.description}</p>
              <p className={`text-lg font-semibold ${getScoreColor(category.score)}`}>
                {(category.score * 100).toFixed(0)}%
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Feedback and Details Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="physics">Physics</TabsTrigger>
          <TabsTrigger value="biomechanics">Biomechanics</TabsTrigger>
          <TabsTrigger value="optimization">Optimization</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* Priority Feedback */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Priority Feedback</h3>
            {feedback.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle2 className="w-12 h-12 mx-auto mb-2 text-green-500" />
                <p>Excellent form! No critical issues detected.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {feedback.map((item, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={getPriorityColor(item.priority)}>
                            {item.priority}
                          </Badge>
                          <span className="text-sm text-gray-600">{item.type}</span>
                        </div>
                        <p className="font-medium">{item.message}</p>
                        <div className="flex items-center gap-4 mt-2 text-sm">
                          <span className="text-gray-600">
                            Current: <span className="font-semibold">{item.current_value.toFixed(1)}</span>
                          </span>
                          <span className="text-gray-600">
                            Target: <span className="font-semibold text-green-600">{item.target_value.toFixed(1)}</span>
                          </span>
                        </div>
                      </div>
                      <AlertCircle className="w-5 h-5 text-yellow-500 ml-4" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="physics" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Physics Analysis</h3>
            
            {/* Joint Angles */}
            <div className="mb-6">
              <h4 className="font-medium mb-3">Joint Angles</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {physics?.joint_angles && Object.entries(physics.joint_angles).map(([joint, angle]) => (
                  <div key={joint} className="bg-gray-50 rounded p-3">
                    <p className="text-sm text-gray-600 capitalize">{joint}</p>
                    <p className="text-xl font-semibold">{(angle as number).toFixed(1)}°</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Moment Arms */}
            <div className="mb-6">
              <h4 className="font-medium mb-3">Moment Arms</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {physics?.moment_arms && Object.entries(physics.moment_arms).map(([name, value]) => (
                  <div key={name} className="bg-gray-50 rounded p-3">
                    <p className="text-sm text-gray-600">{name.replace(/_/g, ' ')}</p>
                    <p className="text-xl font-semibold">{(value as number).toFixed(2)}m</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Energy Efficiency */}
            <div className="bg-blue-50 rounded p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Energy Efficiency</p>
                  <p className="text-sm text-gray-600">Movement economy score</p>
                </div>
                <div className="text-2xl font-bold text-blue-600">
                  {((physics?.energy_efficiency || 0) * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="biomechanics" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Biomechanics Analysis</h3>

            {/* Movement Phase */}
            <div className="mb-6">
              <h4 className="font-medium mb-3">Current Phase</h4>
              <Badge className="text-lg px-4 py-2">
                {biomechanics?.current_phase || 'Unknown'}
              </Badge>
            </div>

            {/* Muscle Activation */}
            <div className="mb-6">
              <h4 className="font-medium mb-3">Muscle Activation</h4>
              <div className="space-y-2">
                {biomechanics?.muscle_activation && Object.entries(biomechanics.muscle_activation).map(([muscle, activation]) => (
                  <div key={muscle} className="flex items-center gap-2">
                    <span className="text-sm capitalize w-24">{muscle}:</span>
                    <Progress value={(activation as number) * 100} className="flex-1 h-2" />
                    <span className="text-sm font-medium w-12 text-right">
                      {((activation as number) * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Movement Quality */}
            <div>
              <h4 className="font-medium mb-3">Movement Quality</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {biomechanics?.movement_quality && Object.entries(biomechanics.movement_quality).map(([metric, value]) => (
                  <div key={metric} className="bg-gray-50 rounded p-3">
                    <p className="text-sm text-gray-600 capitalize">{metric.replace(/_/g, ' ')}</p>
                    <Progress value={(value as number) * 100} className="h-2 my-2" />
                    <p className="text-lg font-semibold">{((value as number) * 100).toFixed(0)}%</p>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="optimization" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Personal Optimization</h3>

            {/* Improvement Priorities */}
            <div className="mb-6">
              <h4 className="font-medium mb-3">Top Improvement Priorities</h4>
              {optimization?.improvement_priorities && optimization.improvement_priorities.length > 0 ? (
                <div className="space-y-3">
                  {optimization.improvement_priorities.map((priority: any, index: number) => (
                    <div key={index} className="border rounded p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium capitalize">{priority.joint} Adjustment</span>
                        <Badge variant="outline">
                          Priority {index + 1}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-gray-600">Current</p>
                          <p className="font-semibold">{priority.current.toFixed(1)}°</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Optimal</p>
                          <p className="font-semibold text-green-600">{priority.optimal.toFixed(1)}°</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Impact</p>
                          <p className="font-semibold">{(priority.impact * 100).toFixed(0)}%</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No specific improvements needed.</p>
              )}
            </div>

            {/* Optimal Form Score */}
            {optimization?.optimal_form && (
              <div className="bg-green-50 rounded p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Optimization Score</p>
                    <p className="text-sm text-gray-600">How close you are to your optimal form</p>
                  </div>
                  <div className="text-2xl font-bold text-green-600">
                    {(optimization.optimal_form.overall_score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            )}
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}