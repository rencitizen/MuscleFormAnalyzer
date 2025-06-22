'use client'

import React, { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { 
  Activity,
  BarChart3,
  BookOpen,
  Settings,
  FileText,
  Download
} from 'lucide-react'
import RealtimeUnifiedAnalysis from '@/components/unified-theory/RealtimeUnifiedAnalysis'
import UnifiedTheoryDashboard from '@/components/unified-theory/UnifiedTheoryDashboard'

// Mock user profile - in real app, this would come from user data
const mockUserProfile = {
  physicalMeasurements: {
    height: 175, // cm
    weight: 75, // kg
    limbLengths: {
      upperArm: 30,
      forearm: 25,
      thigh: 40,
      shank: 35
    }
  },
  experienceLevel: 'intermediate' as const,
  goals: ['strength', 'hypertrophy'],
  limitations: []
}

// Mock historical data for demo
const mockHistoricalAnalysis = {
  unified_scores: {
    physics_efficiency: 0.78,
    biological_optimality: 0.82,
    system_stability: 0.75,
    mathematical_optimization: 0.80,
    overall: 0.79
  },
  feedback: [
    {
      type: 'physics',
      priority: 'high',
      message: 'Reduce forward lean to minimize spinal loading',
      metric: 'spine_angle',
      current_value: 35,
      target_value: 20
    },
    {
      type: 'optimization',
      priority: 'medium',
      message: 'Adjust knee angle from 95° to 85°',
      metric: 'knee_angle',
      current_value: 95,
      target_value: 85
    }
  ],
  physics: {
    joint_angles: {
      knee: 95,
      hip: 80,
      spine: 35,
      elbow: 120
    },
    moment_arms: {
      deadlift_spine: 0.15,
      squat_knee: 0.12
    },
    energy_efficiency: 0.78
  },
  biomechanics: {
    current_phase: 'descent',
    muscle_activation: {
      quadriceps: 0.85,
      hamstrings: 0.65,
      glutes: 0.75,
      core: 0.70
    },
    movement_quality: {
      smoothness: 0.82,
      stability: 0.75,
      symmetry: 0.88,
      tempo_consistency: 0.79,
      range_of_motion: 0.85
    }
  },
  optimization: {
    improvement_priorities: [
      {
        joint: 'spine',
        current: 35,
        optimal: 20,
        difference: 15,
        impact: 0.9
      },
      {
        joint: 'knee',
        current: 95,
        optimal: 85,
        difference: 10,
        impact: 0.7
      }
    ],
    optimal_form: {
      overall_score: 0.80
    }
  }
}

export default function UnifiedTheoryPage() {
  const [activeTab, setActiveTab] = useState('realtime')
  const [latestAnalysis, setLatestAnalysis] = useState<any>(null)

  const handleAnalysisUpdate = (analysis: any) => {
    setLatestAnalysis(analysis)
  }

  const exportAnalysisReport = () => {
    if (typeof window === 'undefined' || typeof document === 'undefined') {
      return
    }
    
    const report = {
      timestamp: new Date().toISOString(),
      userProfile: mockUserProfile,
      analysis: latestAnalysis || mockHistoricalAnalysis
    }
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `unified-theory-analysis-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Unified Theory Form Analysis</h1>
        <p className="text-gray-600">
          Advanced biomechanical analysis integrating physics, biology, complex systems, and mathematical optimization
        </p>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4 mb-6">
          <TabsTrigger value="realtime" className="gap-2">
            <Activity className="w-4 h-4" />
            Real-time Analysis
          </TabsTrigger>
          <TabsTrigger value="history" className="gap-2">
            <BarChart3 className="w-4 h-4" />
            Analysis History
          </TabsTrigger>
          <TabsTrigger value="theory" className="gap-2">
            <BookOpen className="w-4 h-4" />
            Theory Guide
          </TabsTrigger>
          <TabsTrigger value="settings" className="gap-2">
            <Settings className="w-4 h-4" />
            Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="realtime">
          <RealtimeUnifiedAnalysis
            userProfile={mockUserProfile}
            onAnalysisUpdate={handleAnalysisUpdate}
          />
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold">Historical Analysis</h2>
            <Button onClick={exportAnalysisReport} variant="outline" className="gap-2">
              <Download className="w-4 h-4" />
              Export Report
            </Button>
          </div>
          
          <UnifiedTheoryDashboard
            scores={mockHistoricalAnalysis.unified_scores}
            feedback={mockHistoricalAnalysis.feedback}
            physics={mockHistoricalAnalysis.physics}
            biomechanics={mockHistoricalAnalysis.biomechanics}
            optimization={mockHistoricalAnalysis.optimization}
          />
        </TabsContent>

        <TabsContent value="theory" className="space-y-6">
          <Card className="p-6">
            <h2 className="text-2xl font-semibold mb-4">Unified Theory Framework</h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-2 text-blue-600">Physics Engine</h3>
                <p className="text-gray-700 mb-2">
                  Applies Newtonian mechanics, lever principles, and energy conservation laws to analyze movement efficiency.
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                  <li>Joint angle calculations using vector mechanics</li>
                  <li>Moment arm analysis for force efficiency</li>
                  <li>Center of mass tracking for balance</li>
                  <li>Energy expenditure optimization</li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-2 text-green-600">Biomechanics Analyzer</h3>
                <p className="text-gray-700 mb-2">
                  Evaluates neuromuscular patterns, movement phases, and biological efficiency.
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                  <li>Movement phase detection (setup, descent, bottom, ascent, top)</li>
                  <li>Muscle activation pattern estimation</li>
                  <li>Neuromuscular coordination assessment</li>
                  <li>Movement quality metrics</li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-2 text-purple-600">Complex Systems Analysis</h3>
                <p className="text-gray-700 mb-2">
                  Applies nonlinear dynamics and self-organization theory to movement patterns.
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                  <li>Movement attractor identification</li>
                  <li>Adaptive variability vs harmful instability</li>
                  <li>Self-organization pattern detection</li>
                  <li>System stability and resilience metrics</li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-2 text-orange-600">Mathematical Optimization</h3>
                <p className="text-gray-700 mb-2">
                  Finds personalized optimal form based on individual constraints and objectives.
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                  <li>Multi-objective optimization (energy, stress, force, stability)</li>
                  <li>Constraint-based form adjustment</li>
                  <li>Personalized improvement pathways</li>
                  <li>Priority-ranked recommendations</li>
                </ul>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-4">How Scores Are Calculated</h3>
            
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <h4 className="font-medium">Physics Efficiency (25% weight)</h4>
                <p className="text-sm text-gray-600">
                  Based on energy efficiency and mechanical advantage. Lower moment arms and minimal unnecessary movement increase this score.
                </p>
              </div>

              <div className="border-l-4 border-green-500 pl-4">
                <h4 className="font-medium">Biological Optimality (30% weight)</h4>
                <p className="text-sm text-gray-600">
                  Evaluates movement quality, smoothness, and neuromuscular coordination. Higher scores indicate better motor control.
                </p>
              </div>

              <div className="border-l-4 border-purple-500 pl-4">
                <h4 className="font-medium">System Stability (20% weight)</h4>
                <p className="text-sm text-gray-600">
                  Measures movement consistency and adaptability. Balances stability with healthy variability.
                </p>
              </div>

              <div className="border-l-4 border-orange-500 pl-4">
                <h4 className="font-medium">Mathematical Optimization (25% weight)</h4>
                <p className="text-sm text-gray-600">
                  Compares current form to personalized optimal form based on your physical constraints and goals.
                </p>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card className="p-6">
            <h2 className="text-2xl font-semibold mb-4">User Profile Settings</h2>
            
            <form className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Height (cm)</label>
                  <input
                    type="number"
                    defaultValue={mockUserProfile.physicalMeasurements.height}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Weight (kg)</label>
                  <input
                    type="number"
                    defaultValue={mockUserProfile.physicalMeasurements.weight}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Experience Level</label>
                <select
                  defaultValue={mockUserProfile.experienceLevel}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Training Goals</label>
                <div className="space-y-2">
                  {['strength', 'hypertrophy', 'endurance', 'power'].map(goal => (
                    <label key={goal} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        defaultChecked={mockUserProfile.goals.includes(goal)}
                        className="rounded"
                      />
                      <span className="capitalize">{goal}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Physical Limitations</label>
                <textarea
                  placeholder="List any injuries or mobility restrictions..."
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={3}
                />
              </div>

              <Button type="submit" className="w-full">
                Save Profile
              </Button>
            </form>
          </Card>

          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-4">Analysis Preferences</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Default Analysis Interval
                </label>
                <select className="w-full px-3 py-2 border rounded-lg">
                  <option value="50">50ms (High frequency)</option>
                  <option value="100">100ms (Recommended)</option>
                  <option value="200">200ms (Low frequency)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Feedback Detail Level
                </label>
                <select className="w-full px-3 py-2 border rounded-lg">
                  <option value="basic">Basic</option>
                  <option value="detailed">Detailed</option>
                  <option value="expert">Expert</option>
                </select>
              </div>

              <div>
                <label className="flex items-center gap-2">
                  <input type="checkbox" defaultChecked className="rounded" />
                  <span>Show real-time biomechanical overlays</span>
                </label>
              </div>

              <div>
                <label className="flex items-center gap-2">
                  <input type="checkbox" defaultChecked className="rounded" />
                  <span>Audio feedback for critical form issues</span>
                </label>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}