'use client';

import React, { useState, useEffect } from 'react';
import { Calculator, Target, Activity, Apple, Dumbbell, AlertTriangle, Droplets, Brain, Shield } from 'lucide-react';
import MetricCard from './MetricCard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import type { SafetyWarning } from '@/lib/engines/safety';

interface AnalysisResults {
  bodyComposition: {
    bmi: number;
    estimatedBodyFat: number;
    leanBodyMass: number;
    ffmi: number;
    category: string;
    healthRisk: string;
  };
  metabolism: {
    bmr: number;
    tdee: number;
    targetCalories: number;
    weeklyWeightChange: number;
  };
  nutrition: {
    pfcMacros: {
      protein: number;
      carbs: number;
      fats: number;
    };
    proteinPerKg: number;
  };
  safetyAnalysis: {
    overallSafety: 'safe' | 'caution' | 'unsafe';
    score: number;
    warnings: SafetyWarning[];
    recommendations: string[];
  };
}

interface ComprehensiveDashboardProps {
  analysisResults?: AnalysisResults | null;
}

export default function ComprehensiveDashboard({ analysisResults }: ComprehensiveDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview');

  if (!analysisResults) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">分析結果がありません</h2>
          <p className="text-gray-600">プロフィールフォームから分析を開始してください</p>
        </div>
      </div>
    );
  }

  const { bodyComposition, metabolism, nutrition, safetyAnalysis } = analysisResults;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">TENAX FIT v3.0</h1>
          <p className="text-gray-600">AI-Powered Comprehensive Fitness Analysis</p>
        </div>

        {/* 安全性アラート */}
        {safetyAnalysis.overallSafety !== 'safe' && (
          <Alert className={`mb-6 ${safetyAnalysis.overallSafety === 'unsafe' ? 'border-red-500' : 'border-yellow-500'}`}>
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>安全性に関する注意</AlertTitle>
            <AlertDescription>
              あなたの目標設定に健康上のリスクが含まれている可能性があります。
              詳細は安全性タブをご確認ください。
            </AlertDescription>
          </Alert>
        )}

        {/* メトリクスカード */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard 
            icon={Calculator} 
            title="基礎代謝量" 
            value={metabolism.bmr} 
            unit="kcal" 
            color="blue"
            description="安静時のカロリー消費"
          />
          <MetricCard 
            icon={Target} 
            title="目標カロリー" 
            value={metabolism.targetCalories} 
            unit="kcal" 
            color="green"
            description="1日の摂取目標"
          />
          <MetricCard 
            icon={Activity} 
            title="推定体脂肪率" 
            value={bodyComposition.estimatedBodyFat} 
            unit="%" 
            color="orange"
            description={bodyComposition.category}
          />
          <MetricCard 
            icon={Shield} 
            title="安全スコア" 
            value={safetyAnalysis.score} 
            unit="/100" 
            color={safetyAnalysis.score >= 80 ? 'green' : safetyAnalysis.score >= 50 ? 'yellow' : 'red'}
            description={safetyAnalysis.overallSafety === 'safe' ? '安全' : safetyAnalysis.overallSafety === 'caution' ? '注意' : '危険'}
          />
        </div>

        {/* タブコンテンツ */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid grid-cols-5 w-full">
            <TabsTrigger value="overview">概要</TabsTrigger>
            <TabsTrigger value="nutrition">栄養</TabsTrigger>
            <TabsTrigger value="body">身体組成</TabsTrigger>
            <TabsTrigger value="metabolism">代謝</TabsTrigger>
            <TabsTrigger value="safety">安全性</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <OverviewPanel data={analysisResults} />
          </TabsContent>

          <TabsContent value="nutrition" className="space-y-4">
            <NutritionPanel nutrition={nutrition} targetCalories={metabolism.targetCalories} />
          </TabsContent>

          <TabsContent value="body" className="space-y-4">
            <BodyCompositionPanel bodyComposition={bodyComposition} />
          </TabsContent>

          <TabsContent value="metabolism" className="space-y-4">
            <MetabolismPanel metabolism={metabolism} />
          </TabsContent>

          <TabsContent value="safety" className="space-y-4">
            <SafetyPanel safetyAnalysis={safetyAnalysis} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// 概要パネル
function OverviewPanel({ data }: { data: AnalysisResults }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">主要指標</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">BMI</span>
            <span className="font-medium">{data.bodyComposition.bmi}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">除脂肪体重</span>
            <span className="font-medium">{data.bodyComposition.leanBodyMass} kg</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">FFMI</span>
            <span className="font-medium">{data.bodyComposition.ffmi}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">週間体重変化予測</span>
            <span className="font-medium">{data.metabolism.weeklyWeightChange} kg</span>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">日次栄養目標</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">タンパク質</span>
            <span className="font-medium">{data.nutrition.pfcMacros.protein}g</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">炭水化物</span>
            <span className="font-medium">{data.nutrition.pfcMacros.carbs}g</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">脂質</span>
            <span className="font-medium">{data.nutrition.pfcMacros.fats}g</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">体重1kgあたりタンパク質</span>
            <span className="font-medium">{data.nutrition.proteinPerKg}g</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// 栄養パネル
function NutritionPanel({ nutrition, targetCalories }: { nutrition: AnalysisResults['nutrition'], targetCalories: number }) {
  const { protein, carbs, fats } = nutrition.pfcMacros;
  const proteinCalories = protein * 4;
  const carbsCalories = carbs * 4;
  const fatsCalories = fats * 9;

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">PFCバランス</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{protein}g</div>
            <div className="text-sm text-gray-600">タンパク質</div>
            <div className="text-xs text-gray-500">{proteinCalories}kcal ({Math.round((proteinCalories / targetCalories) * 100)}%)</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{carbs}g</div>
            <div className="text-sm text-gray-600">炭水化物</div>
            <div className="text-xs text-gray-500">{carbsCalories}kcal ({Math.round((carbsCalories / targetCalories) * 100)}%)</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">{fats}g</div>
            <div className="text-sm text-gray-600">脂質</div>
            <div className="text-xs text-gray-500">{fatsCalories}kcal ({Math.round((fatsCalories / targetCalories) * 100)}%)</div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">食事配分の推奨</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-700">朝食</div>
            <div className="text-xs text-gray-600 mt-1">25%</div>
            <div className="text-sm font-semibold mt-2">{Math.round(targetCalories * 0.25)}kcal</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-700">昼食</div>
            <div className="text-xs text-gray-600 mt-1">30%</div>
            <div className="text-sm font-semibold mt-2">{Math.round(targetCalories * 0.30)}kcal</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-700">夕食</div>
            <div className="text-xs text-gray-600 mt-1">25%</div>
            <div className="text-sm font-semibold mt-2">{Math.round(targetCalories * 0.25)}kcal</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-700">間食</div>
            <div className="text-xs text-gray-600 mt-1">20%</div>
            <div className="text-sm font-semibold mt-2">{Math.round(targetCalories * 0.20)}kcal</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// 身体組成パネル
function BodyCompositionPanel({ bodyComposition }: { bodyComposition: AnalysisResults['bodyComposition'] }) {
  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'none': return 'text-green-600';
      case 'low': return 'text-yellow-600';
      case 'medium': return 'text-orange-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">身体組成分析</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <div className="text-sm text-gray-600">BMI</div>
            <div className="text-2xl font-bold">{bodyComposition.bmi}</div>
            <div className="text-sm text-gray-500">{bodyComposition.category}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">推定体脂肪率</div>
            <div className="text-2xl font-bold">{bodyComposition.estimatedBodyFat}%</div>
          </div>
        </div>
        <div className="space-y-4">
          <div>
            <div className="text-sm text-gray-600">除脂肪体重（LBM）</div>
            <div className="text-2xl font-bold">{bodyComposition.leanBodyMass}kg</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">FFMI（除脂肪量指数）</div>
            <div className="text-2xl font-bold">{bodyComposition.ffmi}</div>
            <div className="text-sm text-gray-500">筋肉量の指標</div>
          </div>
        </div>
      </div>
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">健康リスク評価</span>
          <span className={`text-sm font-semibold ${getRiskColor(bodyComposition.healthRisk)}`}>
            {bodyComposition.healthRisk === 'none' ? 'リスクなし' :
             bodyComposition.healthRisk === 'low' ? '低リスク' :
             bodyComposition.healthRisk === 'medium' ? '中リスク' : '高リスク'}
          </span>
        </div>
      </div>
    </div>
  );
}

// 代謝パネル
function MetabolismPanel({ metabolism }: { metabolism: AnalysisResults['metabolism'] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">エネルギー代謝</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">基礎代謝率（BMR）</span>
              <span className="text-lg font-semibold">{metabolism.bmr} kcal</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '60%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">総消費カロリー（TDEE）</span>
              <span className="text-lg font-semibold">{metabolism.tdee} kcal</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-green-600 h-2 rounded-full" style={{ width: '80%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">目標カロリー</span>
              <span className="text-lg font-semibold">{metabolism.targetCalories} kcal</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-orange-600 h-2 rounded-full" style={{ width: `${(metabolism.targetCalories / metabolism.tdee) * 100}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">予測される変化</h3>
        <div className="text-center">
          <div className="text-4xl font-bold text-blue-600 mb-2">
            {Math.abs(metabolism.weeklyWeightChange)} kg
          </div>
          <div className="text-sm text-gray-600">週間体重変化</div>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              {metabolism.weeklyWeightChange > 0 ? '増量' : '減量'}ペース: 
              月間約{Math.abs(metabolism.weeklyWeightChange * 4).toFixed(1)}kg
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// 安全性パネル
function SafetyPanel({ safetyAnalysis }: { safetyAnalysis: AnalysisResults['safetyAnalysis'] }) {
  const getWarningColor = (level: string) => {
    switch (level) {
      case 'info': return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'critical': return 'bg-orange-50 border-orange-200 text-orange-800';
      case 'danger': return 'bg-red-50 border-red-200 text-red-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* 安全スコア */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">安全性評価</h3>
        <div className="text-center">
          <div className="text-5xl font-bold mb-2" style={{ color: safetyAnalysis.score >= 80 ? '#10b981' : safetyAnalysis.score >= 50 ? '#f59e0b' : '#ef4444' }}>
            {safetyAnalysis.score}
          </div>
          <div className="text-sm text-gray-600">安全スコア（100点満点）</div>
          <div className="mt-2 text-lg font-medium">
            {safetyAnalysis.overallSafety === 'safe' ? '安全' :
             safetyAnalysis.overallSafety === 'caution' ? '注意が必要' : '危険'}
          </div>
        </div>
      </div>

      {/* 警告 */}
      {safetyAnalysis.warnings.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">警告事項</h3>
          {safetyAnalysis.warnings.map((warning, index) => (
            <div key={index} className={`p-4 rounded-lg border ${getWarningColor(warning.level)}`}>
              <div className="font-semibold mb-2">{warning.category}</div>
              <div className="text-sm mb-3">{warning.message}</div>
              {warning.risks.length > 0 && (
                <div className="mb-3">
                  <div className="text-xs font-semibold mb-1">リスク:</div>
                  <ul className="text-xs list-disc list-inside space-y-1">
                    {warning.risks.map((risk, i) => (
                      <li key={i}>{risk}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 推奨事項 */}
      {safetyAnalysis.recommendations.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">推奨事項</h3>
          <ul className="space-y-2">
            {safetyAnalysis.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span className="text-sm text-gray-700">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}