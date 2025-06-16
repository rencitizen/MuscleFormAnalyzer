'use client';

import React, { useState } from 'react';
import ComprehensiveDashboard from '@/components/dashboard/ComprehensiveDashboard';
import ProfileForm from '@/components/forms/ProfileForm';
import AITrainingRecommendation from '@/components/training/AITrainingRecommendation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Brain, Calculator, Shield, TrendingUp, Users, ChevronRight } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

export default function TenaxFitV3Page() {
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [showForm, setShowForm] = useState(false);

  const handleAnalysisComplete = (results: any) => {
    setAnalysisResults(results);
    setShowForm(false);
  };

  if (analysisResults) {
    return (
      <div>
        <div className="flex justify-end p-4">
          <Button 
            variant="outline" 
            onClick={() => {
              setAnalysisResults(null);
              setShowForm(true);
            }}
          >
            新しい分析を開始
          </Button>
        </div>
        <ComprehensiveDashboard analysisResults={analysisResults} />
      </div>
    );
  }

  if (showForm) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <Button 
            variant="ghost" 
            onClick={() => setShowForm(false)}
            className="mb-4"
          >
            ← 戻る
          </Button>
          <ProfileForm onSubmit={handleAnalysisComplete} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">TENAX FIT v3.0</h1>
              <p className="text-gray-600 mt-1">科学的根拠に基づいた包括的フィットネス分析</p>
            </div>
            <Button 
              size="lg" 
              onClick={() => setShowForm(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              分析を開始 <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* 特徴セクション */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            TENAX FIT v3.0の新機能
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <FeatureCard
              icon={Brain}
              title="AI駆動の分析"
              description="MediaPipeとTensorFlow.jsを活用した高精度な姿勢推定と動作分析"
              color="blue"
            />
            <FeatureCard
              icon={Calculator}
              title="科学的計算エンジン"
              description="最新の研究に基づいた代謝率、体組成、栄養素配分の精密計算"
              color="green"
            />
            <FeatureCard
              icon={Shield}
              title="安全性チェック"
              description="健康リスクを事前に検出し、安全で持続可能な目標設定をサポート"
              color="orange"
            />
          </div>
        </section>

        {/* 分析内容 */}
        <section className="mb-16">
          <Card className="overflow-hidden">
            <CardHeader className="bg-gray-50">
              <CardTitle>包括的な分析内容</CardTitle>
              <CardDescription>
                あなたの健康とフィットネスを多角的に評価します
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <Tabs defaultValue="body" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="body">身体組成</TabsTrigger>
                  <TabsTrigger value="metabolism">代謝</TabsTrigger>
                  <TabsTrigger value="nutrition">栄養</TabsTrigger>
                  <TabsTrigger value="safety">安全性</TabsTrigger>
                </TabsList>
                
                <TabsContent value="body" className="p-6">
                  <h3 className="font-semibold mb-3">身体組成分析</h3>
                  <ul className="space-y-2 text-gray-600">
                    <li>• BMI（ボディマス指数）の計算と評価</li>
                    <li>• 田中式による体脂肪率の推定</li>
                    <li>• 除脂肪体重（LBM）の算出</li>
                    <li>• FFMI（除脂肪量指数）による筋肉量評価</li>
                    <li>• 健康リスクの総合評価</li>
                  </ul>
                </TabsContent>
                
                <TabsContent value="metabolism" className="p-6">
                  <h3 className="font-semibold mb-3">代謝分析</h3>
                  <ul className="space-y-2 text-gray-600">
                    <li>• Mifflin-St Jeor式による基礎代謝率（BMR）計算</li>
                    <li>• 活動レベルに応じた総消費カロリー（TDEE）算出</li>
                    <li>• 目標に最適化されたカロリー設定</li>
                    <li>• 週間・月間の体重変化予測</li>
                    <li>• 安全な減量/増量ペースの提案</li>
                  </ul>
                </TabsContent>
                
                <TabsContent value="nutrition" className="p-6">
                  <h3 className="font-semibold mb-3">栄養プラン</h3>
                  <ul className="space-y-2 text-gray-600">
                    <li>• 目標別PFCバランスの最適化</li>
                    <li>• 体重あたりのタンパク質必要量計算</li>
                    <li>• 食事タイミングと配分の提案</li>
                    <li>• 高品質な食品の推奨リスト</li>
                    <li>• 水分摂取量の個別計算</li>
                  </ul>
                </TabsContent>
                
                <TabsContent value="safety" className="p-6">
                  <h3 className="font-semibold mb-3">安全性評価</h3>
                  <ul className="space-y-2 text-gray-600">
                    <li>• カロリー摂取量の安全性チェック</li>
                    <li>• 目標体脂肪率のリスク評価</li>
                    <li>• オーバートレーニングの予防</li>
                    <li>• 個別の健康リスク警告</li>
                    <li>• エビデンスに基づいた推奨事項</li>
                  </ul>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </section>

        {/* 利用者の声 */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            プロフェッショナルからの評価
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TestimonialCard
              quote="科学的根拠に基づいた計算と、実践的なアドバイスの組み合わせが素晴らしい。クライアントの指導に活用しています。"
              author="山田太郎"
              role="パーソナルトレーナー"
            />
            <TestimonialCard
              quote="安全性チェック機能が特に優れています。無理な目標設定を防ぎ、持続可能なプランを立てられます。"
              author="佐藤花子"
              role="管理栄養士"
            />
          </div>
        </section>

        {/* CTA */}
        <section className="text-center">
          <Card className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
            <CardContent className="py-12">
              <h2 className="text-3xl font-bold mb-4">
                今すぐ始めましょう
              </h2>
              <p className="text-xl mb-8 text-blue-100">
                あなたの健康とフィットネスを次のレベルへ
              </p>
              <Button 
                size="lg" 
                variant="secondary"
                onClick={() => setShowForm(true)}
                className="bg-white text-blue-600 hover:bg-gray-100"
              >
                無料で分析を開始
              </Button>
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
}

// コンポーネント

function FeatureCard({ 
  icon: Icon, 
  title, 
  description, 
  color 
}: { 
  icon: any; 
  title: string; 
  description: string; 
  color: string;
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    orange: 'bg-orange-50 text-orange-600'
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-6">
        <div className={`inline-flex p-3 rounded-lg ${colorClasses[color as keyof typeof colorClasses]} mb-4`}>
          <Icon size={24} />
        </div>
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-gray-600 text-sm">{description}</p>
      </CardContent>
    </Card>
  );
}

function TestimonialCard({ 
  quote, 
  author, 
  role 
}: { 
  quote: string; 
  author: string; 
  role: string;
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start space-x-1 text-yellow-500 mb-4">
          {"★★★★★".split('').map((star, i) => (
            <span key={i}>{star}</span>
          ))}
        </div>
        <p className="text-gray-600 italic mb-4">"{quote}"</p>
        <div>
          <p className="font-semibold">{author}</p>
          <p className="text-sm text-gray-500">{role}</p>
        </div>
      </CardContent>
    </Card>
  );
}