'use client';

import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import RealtimeCameraAnalysis from '@/components/camera/RealtimeCameraAnalysis';
import { ArrowLeft } from 'lucide-react';

const exercises = [
  { id: 'squat', name: 'スクワット' },
  { id: 'bench_press', name: 'ベンチプレス' },
  { id: 'deadlift', name: 'デッドリフト' },
  { id: 'pushup', name: 'プッシュアップ' },
  { id: 'plank', name: 'プランク' },
];

export default function RealtimeWorkoutPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const [selectedExercise, setSelectedExercise] = useState('squat');
  const [analysisResults, setAnalysisResults] = useState<any[]>([]);

  const handleAnalysisResult = (result: any) => {
    setAnalysisResults(prev => [...prev.slice(-9), result]);
  };

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>ログインが必要です</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          戻る
        </button>
      </div>

      <h1 className="text-3xl font-bold mb-8">リアルタイムフォーム分析</h1>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          エクササイズを選択
        </label>
        <select
          value={selectedExercise}
          onChange={(e) => setSelectedExercise(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {exercises.map((exercise) => (
            <option key={exercise.id} value={exercise.id}>
              {exercise.name}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-6">
        <RealtimeCameraAnalysis
          exerciseType={selectedExercise}
          userId={session.user?.id || 'anonymous'}
          onAnalysisResult={handleAnalysisResult}
        />

        {/* Recent analysis history */}
        {analysisResults.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="font-semibold mb-3">分析履歴</h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {analysisResults.map((result, index) => (
                <div
                  key={index}
                  className="text-sm p-2 bg-gray-50 rounded flex justify-between items-center"
                >
                  <span className={result.pose_detected ? 'text-green-600' : 'text-gray-500'}>
                    {result.pose_detected ? 'ポーズ検出' : 'ポーズ未検出'}
                  </span>
                  {result.analysis?.score && (
                    <span className="font-medium">{result.analysis.score}%</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="font-semibold mb-2">使い方</h3>
        <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
          <li>エクササイズを選択してください</li>
          <li>カメラの使用を許可してください</li>
          <li>全身が映るようにカメラを設置してください</li>
          <li>「リアルタイム分析を開始」をクリックして分析を開始します</li>
          <li>エクササイズを実行すると、リアルタイムでフォームが分析されます</li>
        </ol>
      </div>
    </div>
  );
}