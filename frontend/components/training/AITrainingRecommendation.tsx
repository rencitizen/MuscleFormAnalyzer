'use client';

import React, { useState, useEffect } from 'react';
import { Brain, Calendar, Clock, Target, TrendingUp, AlertCircle, CheckCircle, ChevronRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface AITrainingRecommendationProps {
  comprehensiveAnalysis?: any;
  trainingRecommendation?: any;
  onAdoptProgram?: (program: any) => void;
}

const AITrainingRecommendation: React.FC<AITrainingRecommendationProps> = ({
  comprehensiveAnalysis,
  trainingRecommendation,
  onAdoptProgram
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedTab, setSelectedTab] = useState('overview');

  if (!comprehensiveAnalysis) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">包括的な分析を先に実行してください</p>
        </CardContent>
      </Card>
    );
  }

  if (!trainingRecommendation) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">AIトレーニングプログラムを生成中...</p>
        </CardContent>
      </Card>
    );
  }

  const { programOverview, weeklySchedule, exerciseSelection, loadParameters, nutritionSync, recoveryPlan } = trainingRecommendation;

  return (
    <div className="space-y-6">
      {/* プログラム概要 */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Brain className="w-6 h-6 text-blue-600" />
              <CardTitle className="text-2xl">{programOverview.title}</CardTitle>
            </div>
            <Badge variant="secondary" className="bg-blue-100 text-blue-700">
              {programOverview.duration}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 mb-4">{programOverview.objective}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <h4 className="font-semibold mb-2 text-blue-800">期待される効果</h4>
              <ul className="space-y-1">
                {programOverview.expectedOutcomes.map((outcome: string, index: number) => (
                  <li key={index} className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{outcome}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2 text-purple-800">重要な原則</h4>
              <ul className="space-y-1">
                {programOverview.keyPrinciples.map((principle: string, index: number) => (
                  <li key={index} className="flex items-start">
                    <Target className="w-4 h-4 text-purple-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{principle}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <Button 
            onClick={() => onAdoptProgram?.(trainingRecommendation)}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            このプログラムを採用する
          </Button>
        </CardContent>
      </Card>

      {/* タブ形式の詳細情報 */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">概要</TabsTrigger>
          <TabsTrigger value="schedule">スケジュール</TabsTrigger>
          <TabsTrigger value="exercises">エクササイズ</TabsTrigger>
          <TabsTrigger value="recovery">回復</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <WeeklyScheduleView schedule={weeklySchedule} />
        </TabsContent>

        <TabsContent value="schedule">
          <DetailedScheduleView schedule={weeklySchedule} />
        </TabsContent>

        <TabsContent value="exercises">
          <ExerciseSelectionView exerciseSelection={exerciseSelection} />
        </TabsContent>

        <TabsContent value="recovery">
          <RecoveryPlanView recoveryPlan={recoveryPlan} nutritionSync={nutritionSync} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

// 週間スケジュール表示コンポーネント
const WeeklyScheduleView: React.FC<{ schedule: any }> = ({ schedule }) => {
  const days = ['月', '火', '水', '木', '金', '土', '日'];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Calendar className="w-5 h-5 mr-2" />
          週間スケジュール
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-2">
          {Object.entries(schedule.schedule).map(([day, session]: [string, any], index) => (
            <div
              key={day}
              className={`p-3 rounded-lg text-center ${
                session.type === 'rest' 
                  ? 'bg-gray-100 text-gray-600' 
                  : 'bg-blue-100 text-blue-800'
              }`}
            >
              <div className="font-bold text-lg">{days[index]}</div>
              <div className="text-sm mt-1">
                {session.type === 'rest' ? '休息' : session.focus || session.type}
              </div>
              {session.duration && (
                <div className="text-xs mt-1 flex items-center justify-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {session.duration}分
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">週間トレーニング回数</span>
            <span className="font-bold">{schedule.totalSessions}回</span>
          </div>
          <div className="flex items-center justify-between mt-2">
            <span className="text-sm text-gray-600">週間総ボリューム</span>
            <span className="font-bold">{schedule.weeklyVolume}セット</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// 詳細スケジュール表示
const DetailedScheduleView: React.FC<{ schedule: any }> = ({ schedule }) => {
  const dayNames = {
    day1: '第1日',
    day2: '第2日',
    day3: '第3日',
    day4: '第4日',
    day5: '第5日',
    day6: '第6日',
    day7: '第7日'
  };

  return (
    <div className="space-y-4">
      {Object.entries(schedule.schedule).map(([day, session]: [string, any]) => (
        <Card key={day}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold">{dayNames[day as keyof typeof dayNames]}</h3>
              <Badge variant={session.type === 'rest' ? 'secondary' : 'default'}>
                {session.type === 'rest' ? '休息日' : 'トレーニング日'}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {session.type !== 'rest' ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">タイプ</span>
                  <span className="font-medium">{session.type}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">フォーカス</span>
                  <span className="font-medium">{session.focus}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">所要時間</span>
                  <span className="font-medium">{session.duration}分</span>
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-600">
                アクティビティ: {session.activity}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

// エクササイズ選択表示
const ExerciseSelectionView: React.FC<{ exerciseSelection: any }> = ({ exerciseSelection }) => {
  const exerciseCategories = [
    { key: 'primary', title: 'メイン種目', color: 'blue' },
    { key: 'secondary', title: '補助種目', color: 'green' },
    { key: 'accessories', title: 'アクセサリー種目', color: 'purple' },
    { key: 'cardio', title: '有酸素運動', color: 'orange' },
    { key: 'mobility', title: 'モビリティ', color: 'pink' }
  ];

  return (
    <div className="space-y-6">
      {exerciseCategories.map(category => {
        const exercises = exerciseSelection[category.key];
        if (!exercises || exercises.length === 0) return null;

        return (
          <Card key={category.key}>
            <CardHeader>
              <CardTitle className={`text-${category.color}-700`}>
                {category.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {exercises.map((exercise: any, index: number) => (
                  <div
                    key={index}
                    className={`p-3 border-l-4 border-${category.color}-500 bg-gray-50 rounded`}
                  >
                    <h4 className="font-medium">{exercise.exercise}</h4>
                    <p className="text-sm text-gray-600 mt-1">{exercise.reason}</p>
                    {exercise.parameters && (
                      <div className="text-xs text-gray-500 mt-2">
                        {exercise.parameters.sets && `${exercise.parameters.sets}セット × ${exercise.parameters.reps}回`}
                        {exercise.parameters.duration && `${exercise.parameters.duration}分`}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

// 回復プラン表示
const RecoveryPlanView: React.FC<{ recoveryPlan: any; nutritionSync: any }> = ({ recoveryPlan, nutritionSync }) => {
  return (
    <div className="space-y-6">
      {/* 栄養同期 */}
      <Card>
        <CardHeader>
          <CardTitle>栄養タイミング</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-yellow-50 rounded-lg">
            <h4 className="font-medium text-yellow-800 mb-2">ワークアウト前</h4>
            <p className="text-sm text-yellow-700">{nutritionSync.preWorkout}</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <h4 className="font-medium text-green-800 mb-2">ワークアウト後</h4>
            <p className="text-sm text-green-700">{nutritionSync.postWorkout}</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-800 mb-2">水分補給</h4>
            <p className="text-sm text-blue-700">{nutritionSync.hydrationPlan}</p>
          </div>
        </CardContent>
      </Card>

      {/* 睡眠最適化 */}
      <Card>
        <CardHeader>
          <CardTitle>睡眠最適化</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">推奨睡眠時間</span>
              <span className="font-bold text-lg">{recoveryPlan.sleepOptimization.targetHours}時間</span>
            </div>
            <Progress value={(recoveryPlan.sleepOptimization.targetHours / 9) * 100} className="h-2" />
          </div>
          
          <div className="space-y-3">
            <div>
              <h4 className="font-medium mb-2">就寝前ルーティン</h4>
              <ul className="space-y-1">
                {recoveryPlan.sleepOptimization.bedtimeRoutine.map((item: string, index: number) => (
                  <li key={index} className="flex items-start">
                    <ChevronRight className="w-4 h-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* アクティブリカバリー */}
      <Card>
        <CardHeader>
          <CardTitle>アクティブリカバリー</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="text-center p-3 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-700">
                {recoveryPlan.activeRecovery.frequency}
              </div>
              <div className="text-sm text-purple-600">回/週</div>
            </div>
            <div className="text-center p-3 bg-pink-50 rounded-lg">
              <div className="text-lg font-bold text-pink-700">
                {recoveryPlan.activeRecovery.duration}
              </div>
              <div className="text-sm text-pink-600">推奨時間</div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium mb-2">推奨アクティビティ</h4>
            <div className="flex flex-wrap gap-2">
              {recoveryPlan.activeRecovery.activities.map((activity: string, index: number) => (
                <Badge key={index} variant="outline">
                  {activity}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AITrainingRecommendation;