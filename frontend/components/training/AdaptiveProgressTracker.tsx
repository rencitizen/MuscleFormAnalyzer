'use client';

import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Award, BarChart3, Activity } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

interface AdaptiveProgressTrackerProps {
  userProgress?: any;
  adaptedProgram?: any;
  onRequestAdaptation?: () => void;
}

const AdaptiveProgressTracker: React.FC<AdaptiveProgressTrackerProps> = ({
  userProgress,
  adaptedProgram,
  onRequestAdaptation
}) => {
  const [selectedMetric, setSelectedMetric] = useState('strength');

  if (!userProgress) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">進捗データがありません</p>
          <p className="text-sm text-gray-500 mt-2">トレーニングを開始すると進捗が表示されます</p>
        </CardContent>
      </Card>
    );
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'declining': return <TrendingDown className="w-4 h-4 text-red-500" />;
      default: return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  const getProgressColor = (value: number) => {
    if (value >= 0.8) return 'text-green-600';
    if (value >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* 進捗サマリーカード */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>進捗サマリー</span>
            <Button
              onClick={onRequestAdaptation}
              variant="outline"
              size="sm"
            >
              プログラムを最適化
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard
              title="筋力向上"
              value={userProgress.strengthProgress * 100}
              unit="%"
              trend={userProgress.strengthTrend}
              icon={<Activity className="w-4 h-4" />}
            />
            <MetricCard
              title="ボリューム耐性"
              value={userProgress.volumeTolerance * 100}
              unit="%"
              trend={userProgress.volumeTrend}
              icon={<BarChart3 className="w-4 h-4" />}
            />
            <MetricCard
              title="回復品質"
              value={userProgress.recoveryQuality * 100}
              unit="%"
              trend={userProgress.recoveryTrend}
              icon={<Activity className="w-4 h-4" />}
            />
            <MetricCard
              title="遵守率"
              value={userProgress.adherence * 100}
              unit="%"
              trend={userProgress.adherenceTrend}
              icon={<Award className="w-4 h-4" />}
            />
          </div>
        </CardContent>
      </Card>

      {/* 適応的調整 */}
      {adaptedProgram && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center text-orange-800">
              <AlertTriangle className="w-5 h-5 mr-2" />
              プログラム調整の推奨
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {adaptedProgram.reasoning.map((reason: string, index: number) => (
                <Alert key={index} className="bg-white">
                  <AlertDescription>{reason}</AlertDescription>
                </Alert>
              ))}
            </div>
            
            <div className="mt-4 p-4 bg-white rounded-lg">
              <h4 className="font-medium mb-2">次週のフォーカス</h4>
              <p className="text-sm text-gray-700">{adaptedProgram.nextWeekFocus}</p>
            </div>

            {adaptedProgram.warnings && adaptedProgram.warnings.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium mb-2 text-red-700">警告</h4>
                {adaptedProgram.warnings.map((warning: string, index: number) => (
                  <Alert key={index} variant="destructive" className="mb-2">
                    <AlertDescription>{warning}</AlertDescription>
                  </Alert>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* 詳細メトリクス */}
      <Tabs value={selectedMetric} onValueChange={setSelectedMetric}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="strength">筋力</TabsTrigger>
          <TabsTrigger value="volume">ボリューム</TabsTrigger>
          <TabsTrigger value="recovery">回復</TabsTrigger>
          <TabsTrigger value="body">身体組成</TabsTrigger>
        </TabsList>

        <TabsContent value="strength">
          <StrengthProgressView strengthData={userProgress.strengthProgress} />
        </TabsContent>

        <TabsContent value="volume">
          <VolumeAnalysisView volumeData={userProgress.workoutHistory} />
        </TabsContent>

        <TabsContent value="recovery">
          <RecoveryAnalysisView recoveryData={userProgress.subjectiveFeedback} />
        </TabsContent>

        <TabsContent value="body">
          <BodyCompositionView bodyData={userProgress.bodyMetricsHistory} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

// メトリックカードコンポーネント
const MetricCard: React.FC<{
  title: string;
  value: number;
  unit: string;
  trend: string;
  icon: React.ReactNode;
}> = ({ title, value, unit, trend, icon }) => {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">{title}</span>
          {icon}
        </div>
        <div className="flex items-baseline justify-between">
          <span className="text-2xl font-bold">
            {Math.round(value)}{unit}
          </span>
          {getTrendIcon(trend)}
        </div>
        <Progress value={value} className="mt-2 h-2" />
      </CardContent>
    </Card>
  );
};

// 筋力進捗ビュー
const StrengthProgressView: React.FC<{ strengthData: any }> = ({ strengthData }) => {
  // サンプルデータ（実際にはstrengthDataから生成）
  const data = [
    { week: '第1週', squat: 100, bench: 80, deadlift: 120 },
    { week: '第2週', squat: 105, bench: 82, deadlift: 125 },
    { week: '第3週', squat: 107, bench: 85, deadlift: 130 },
    { week: '第4週', squat: 110, bench: 87, deadlift: 135 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>主要エクササイズの進捗</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="squat" stroke="#3B82F6" name="スクワット" strokeWidth={2} />
              <Line type="monotone" dataKey="bench" stroke="#10B981" name="ベンチプレス" strokeWidth={2} />
              <Line type="monotone" dataKey="deadlift" stroke="#F59E0B" name="デッドリフト" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="text-center">
            <Badge className="bg-blue-100 text-blue-700">スクワット</Badge>
            <p className="text-sm mt-1">+10% 向上</p>
          </div>
          <div className="text-center">
            <Badge className="bg-green-100 text-green-700">ベンチプレス</Badge>
            <p className="text-sm mt-1">+8.75% 向上</p>
          </div>
          <div className="text-center">
            <Badge className="bg-yellow-100 text-yellow-700">デッドリフト</Badge>
            <p className="text-sm mt-1">+12.5% 向上</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ボリューム分析ビュー
const VolumeAnalysisView: React.FC<{ volumeData: any }> = ({ volumeData }) => {
  const data = [
    { day: '月', sets: 16, rpe: 7 },
    { day: '火', sets: 0, rpe: 0 },
    { day: '水', sets: 18, rpe: 8 },
    { day: '木', sets: 0, rpe: 0 },
    { day: '金', sets: 15, rpe: 7.5 },
    { day: '土', sets: 10, rpe: 6 },
    { day: '日', sets: 0, rpe: 0 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>週間トレーニングボリューム</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Bar yAxisId="left" dataKey="sets" fill="#3B82F6" name="セット数" />
              <Line yAxisId="right" type="monotone" dataKey="rpe" stroke="#F59E0B" name="平均RPE" strokeWidth={2} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">週間総セット数</p>
              <p className="text-xl font-bold">59セット</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">平均RPE</p>
              <p className="text-xl font-bold">7.1</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// 回復分析ビュー
const RecoveryAnalysisView: React.FC<{ recoveryData: any }> = ({ recoveryData }) => {
  const data = [
    { metric: '睡眠', value: 75 },
    { metric: 'エネルギー', value: 65 },
    { metric: 'モチベーション', value: 80 },
    { metric: '筋肉疲労', value: 40 },
    { metric: 'ストレス', value: 30 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>回復状態の総合評価</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={data}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar name="現在の状態" dataKey="value" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-4 space-y-2">
          {data.map((item, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-sm">{item.metric}</span>
              <div className="flex items-center space-x-2">
                <Progress value={item.value} className="w-24 h-2" />
                <span className="text-sm font-medium w-12 text-right">{item.value}%</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// 身体組成ビュー
const BodyCompositionView: React.FC<{ bodyData: any }> = ({ bodyData }) => {
  const data = [
    { week: '開始時', weight: 70, bodyFat: 20, muscleMass: 56 },
    { week: '第2週', weight: 69.5, bodyFat: 19.5, muscleMass: 56.2 },
    { week: '第4週', weight: 69, bodyFat: 18.8, muscleMass: 56.5 },
    { week: '第6週', weight: 68.5, bodyFat: 18, muscleMass: 56.8 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>身体組成の変化</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="weight" stackId="1" stroke="#3B82F6" fill="#3B82F6" name="体重(kg)" />
              <Area type="monotone" dataKey="bodyFat" stackId="2" stroke="#F59E0B" fill="#F59E0B" name="体脂肪率(%)" />
              <Area type="monotone" dataKey="muscleMass" stackId="3" stroke="#10B981" fill="#10B981" name="筋肉量(kg)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-600">体重変化</p>
            <p className="text-xl font-bold text-blue-700">-1.5kg</p>
          </div>
          <div className="text-center p-3 bg-yellow-50 rounded-lg">
            <p className="text-sm text-yellow-600">体脂肪率変化</p>
            <p className="text-xl font-bold text-yellow-700">-2.0%</p>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <p className="text-sm text-green-600">筋肉量変化</p>
            <p className="text-xl font-bold text-green-700">+0.8kg</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ヘルパー関数
const getTrendIcon = (trend: string) => {
  switch (trend) {
    case 'improving': return <TrendingUp className="w-4 h-4 text-green-500" />;
    case 'declining': return <TrendingDown className="w-4 h-4 text-red-500" />;
    default: return <Minus className="w-4 h-4 text-gray-500" />;
  }
};

export default AdaptiveProgressTracker;