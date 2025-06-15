'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Info, AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

interface Exercise {
  id: string;
  name: string;
  nameJa: string;
  category: string;
  primaryMuscles: string[];
  secondaryMuscles: string[];
  equipment: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  movementPattern: string;
  forceType: string;
  mechanics: string;
  instructions?: string[];
  tips?: string[];
  commonMistakes?: string[];
  variations?: string[];
  benefits?: string[];
}

interface ExerciseCardProps {
  exercise: Exercise;
  parameters?: {
    sets: number;
    reps: number | string;
    rest: number;
    tempo?: string;
    intensity?: number;
  };
  type?: 'primary' | 'secondary' | 'accessory';
  onSelect?: (exercise: Exercise) => void;
}

const ExerciseCard: React.FC<ExerciseCardProps> = ({
  exercise,
  parameters,
  type = 'primary',
  onSelect
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const getBorderColor = (type: string) => {
    switch (type) {
      case 'primary': return 'border-blue-500';
      case 'secondary': return 'border-green-500';
      case 'accessory': return 'border-purple-500';
      default: return 'border-gray-300';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-700';
      case 'intermediate': return 'bg-yellow-100 text-yellow-700';
      case 'advanced': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const muscleGroups: Record<string, string> = {
    quadriceps: '大腿四頭筋',
    glutes: '臀筋',
    hamstrings: 'ハムストリングス',
    calves: 'ふくらはぎ',
    chest: '胸',
    back: '背中',
    shoulders: '肩',
    triceps: '上腕三頭筋',
    biceps: '上腕二頭筋',
    core: 'コア',
    abs: '腹筋',
    lats: '広背筋',
    traps: '僧帽筋',
    middle_back: '中背部',
    lower_back: '下背部',
    forearms: '前腕',
    hip_flexors: '腸腰筋',
    spine: '脊柱'
  };

  const equipmentNames: Record<string, string> = {
    none: '不要',
    barbell: 'バーベル',
    dumbbell: 'ダンベル',
    kettlebell: 'ケトルベル',
    pullup_bar: '懸垂バー',
    bench: 'ベンチ',
    squat_rack: 'スクワットラック',
    power_rack: 'パワーラック',
    cable_machine: 'ケーブルマシン',
    leg_press_machine: 'レッグプレスマシン',
    resistance_band: 'レジスタンスバンド',
    treadmill: 'トレッドミル',
    stationary_bike: 'エアロバイク',
    rowing_machine: 'ローイングマシン',
    pvc_pipe: 'PVCパイプ'
  };

  return (
    <Card className={`border-l-4 ${getBorderColor(type)} overflow-hidden`}>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger className="w-full">
          <div className="p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex-1 text-left">
                <h3 className="font-bold text-lg">{exercise.nameJa}</h3>
                <p className="text-sm text-gray-600">{exercise.name}</p>
                
                <div className="flex flex-wrap gap-2 mt-2">
                  <Badge className={getDifficultyColor(exercise.difficulty)}>
                    {exercise.difficulty === 'beginner' ? '初級' : 
                     exercise.difficulty === 'intermediate' ? '中級' : '上級'}
                  </Badge>
                  {exercise.primaryMuscles.slice(0, 2).map(muscle => (
                    <Badge key={muscle} variant="outline">
                      {muscleGroups[muscle] || muscle}
                    </Badge>
                  ))}
                </div>

                {parameters && (
                  <div className="mt-3 text-sm font-medium">
                    {parameters.sets}セット × {parameters.reps}回
                    {parameters.rest && ` | 休憩${parameters.rest}秒`}
                    {parameters.intensity && ` | 強度${Math.round(parameters.intensity * 100)}%`}
                  </div>
                )}
              </div>
              
              <div className="ml-4 flex items-center">
                {isOpen ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </div>
            </div>
          </div>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="px-4 pb-4 space-y-4 border-t">
            {/* 必要器具 */}
            <div className="pt-4">
              <h4 className="font-medium mb-2 flex items-center">
                <Info className="w-4 h-4 mr-2" />
                必要器具
              </h4>
              <div className="flex flex-wrap gap-2">
                {exercise.equipment.map(item => (
                  <Badge key={item} variant="secondary">
                    {equipmentNames[item] || item}
                  </Badge>
                ))}
              </div>
            </div>

            {/* 対象筋群 */}
            <div>
              <h4 className="font-medium mb-2">対象筋群</h4>
              <div className="space-y-1">
                <div className="text-sm">
                  <span className="text-gray-600">主要:</span>{' '}
                  {exercise.primaryMuscles.map(m => muscleGroups[m] || m).join(', ')}
                </div>
                {exercise.secondaryMuscles.length > 0 && (
                  <div className="text-sm">
                    <span className="text-gray-600">補助:</span>{' '}
                    {exercise.secondaryMuscles.map(m => muscleGroups[m] || m).join(', ')}
                  </div>
                )}
              </div>
            </div>

            {/* 実施方法 */}
            {exercise.instructions && (
              <div>
                <h4 className="font-medium mb-2">実施方法</h4>
                <ol className="space-y-1">
                  {exercise.instructions.map((instruction, index) => (
                    <li key={index} className="text-sm text-gray-700 flex">
                      <span className="font-medium mr-2">{index + 1}.</span>
                      <span>{instruction}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* ポイント */}
            {exercise.tips && (
              <div>
                <h4 className="font-medium mb-2">ポイント</h4>
                <ul className="space-y-1">
                  {exercise.tips.map((tip, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* よくある間違い */}
            {exercise.commonMistakes && (
              <div>
                <h4 className="font-medium mb-2 flex items-center text-orange-700">
                  <AlertCircle className="w-4 h-4 mr-2" />
                  よくある間違い
                </h4>
                <ul className="space-y-1">
                  {exercise.commonMistakes.map((mistake, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start">
                      <span className="text-orange-500 mr-2">⚠</span>
                      <span>{mistake}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 効果 */}
            {exercise.benefits && (
              <div>
                <h4 className="font-medium mb-2">効果</h4>
                <ul className="space-y-1">
                  {exercise.benefits.map((benefit, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span>{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* バリエーション */}
            {exercise.variations && exercise.variations.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">バリエーション</h4>
                <div className="flex flex-wrap gap-2">
                  {exercise.variations.map((variation, index) => (
                    <Badge key={index} variant="outline">
                      {variation}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {onSelect && (
              <Button
                onClick={() => onSelect(exercise)}
                className="w-full mt-4"
                variant="outline"
              >
                このエクササイズを選択
              </Button>
            )}
          </div>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
};

export default ExerciseCard;