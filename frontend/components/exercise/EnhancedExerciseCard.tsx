import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Collapsible, 
  CollapsibleContent, 
  CollapsibleTrigger 
} from '@/components/ui/collapsible';
import { 
  ChevronDown, 
  ChevronUp, 
  Play, 
  BookOpen, 
  Star,
  Clock,
  Flame,
  Users,
  Heart,
  Share2,
  BarChart
} from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface Exercise {
  id: string;
  name: string;
  category: string;
  targetMuscles: string[];
  secondaryMuscles?: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  equipment: string[];
  description: string;
  instructions: string[];
  tips: string[];
  videoUrl?: string;
  duration?: number; // in seconds
  caloriesBurned?: number; // per set/rep
  popularity?: number; // 1-5
  isFavorite?: boolean;
}

interface ExerciseCardProps {
  exercise: Exercise;
  onSelectExercise?: (exercise: Exercise) => void;
  onToggleFavorite?: (exerciseId: string) => void;
  onShare?: (exercise: Exercise) => void;
  onViewStats?: (exerciseId: string) => void;
  isSelected?: boolean;
  showStats?: boolean;
}

const EnhancedExerciseCard: React.FC<ExerciseCardProps> = ({
  exercise,
  onSelectExercise,
  onToggleFavorite,
  onShare,
  onViewStats,
  isSelected = false,
  showStats = true
}) => {
  const [isOpen, setIsOpen] = React.useState(false);

  const getDifficultyColor = (difficulty: Exercise['difficulty']) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'advanced':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  const getDifficultyText = (difficulty: Exercise['difficulty']) => {
    switch (difficulty) {
      case 'beginner':
        return '初級';
      case 'intermediate':
        return '中級';
      case 'advanced':
        return '上級';
      default:
        return difficulty;
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return null;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}分${secs > 0 ? `${secs}秒` : ''}` : `${secs}秒`;
  };

  return (
    <Card className={`transition-all duration-200 hover:shadow-lg ${
      isSelected ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-950' : ''
    }`}>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start mb-2">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {exercise.name}
            </CardTitle>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{exercise.category}</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={getDifficultyColor(exercise.difficulty)}>
              {getDifficultyText(exercise.difficulty)}
            </Badge>
            {onToggleFavorite && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={() => onToggleFavorite(exercise.id)}
                    >
                      <Heart 
                        className={`w-4 h-4 ${
                          exercise.isFavorite 
                            ? 'fill-red-500 text-red-500' 
                            : 'text-gray-500'
                        }`} 
                      />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{exercise.isFavorite ? 'お気に入りから削除' : 'お気に入りに追加'}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </div>
        </div>

        {/* Stats Row */}
        {showStats && (
          <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
            {exercise.duration && (
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{formatDuration(exercise.duration)}</span>
              </div>
            )}
            {exercise.caloriesBurned && (
              <div className="flex items-center gap-1">
                <Flame className="w-4 h-4 text-orange-500" />
                <span>{exercise.caloriesBurned} kcal</span>
              </div>
            )}
            {exercise.popularity && (
              <div className="flex items-center gap-1">
                <Users className="w-4 h-4" />
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-3 h-3 ${
                        i < exercise.popularity 
                          ? 'fill-yellow-400 text-yellow-400' 
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Target Muscles */}
        <div className="space-y-2">
          <div className="flex flex-wrap gap-2">
            {exercise.targetMuscles.map((muscle, index) => (
              <Badge key={index} variant="default" className="text-xs">
                {muscle}
              </Badge>
            ))}
          </div>
          
          {exercise.secondaryMuscles && exercise.secondaryMuscles.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {exercise.secondaryMuscles.map((muscle, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {muscle}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Equipment */}
        {exercise.equipment.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {exercise.equipment.map((eq, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {eq}
              </Badge>
            ))}
          </div>
        )}
      </CardHeader>

      <CardContent className="pt-0">
        <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
          {exercise.description}
        </p>

        <Collapsible open={isOpen} onOpenChange={setIsOpen}>
          <div className="flex gap-2 mb-3 flex-wrap">
            {exercise.videoUrl && (
              <Button 
                variant="outline" 
                size="sm"
                className="flex items-center gap-2"
                onClick={() => window.open(exercise.videoUrl, '_blank')}
              >
                <Play className="w-4 h-4" />
                動画
              </Button>
            )}
            
            <CollapsibleTrigger asChild>
              <Button variant="outline" size="sm" className="flex items-center gap-2">
                <BookOpen className="w-4 h-4" />
                詳細
                {isOpen ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </Button>
            </CollapsibleTrigger>

            {onShare && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => onShare(exercise)}
                className="flex items-center gap-2"
              >
                <Share2 className="w-4 h-4" />
                共有
              </Button>
            )}

            {onViewStats && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => onViewStats(exercise.id)}
                className="flex items-center gap-2"
              >
                <BarChart className="w-4 h-4" />
                統計
              </Button>
            )}

            {onSelectExercise && (
              <Button 
                variant={isSelected ? "default" : "outline"}
                size="sm"
                onClick={() => onSelectExercise(exercise)}
                className="ml-auto"
              >
                {isSelected ? '選択済み' : '選択'}
              </Button>
            )}
          </div>

          <CollapsibleContent className="space-y-4 animate-in slide-in-from-top-2">
            {exercise.instructions.length > 0 && (
              <div>
                <h4 className="font-medium text-sm mb-2 text-gray-900 dark:text-gray-100">
                  実行方法:
                </h4>
                <ol className="list-decimal list-inside space-y-1">
                  {exercise.instructions.map((instruction, index) => (
                    <li key={index} className="text-sm text-gray-700 dark:text-gray-300">
                      {instruction}
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {exercise.tips.length > 0 && (
              <div>
                <h4 className="font-medium text-sm mb-2 text-gray-900 dark:text-gray-100">
                  コツ・注意点:
                </h4>
                <ul className="list-disc list-inside space-y-1">
                  {exercise.tips.map((tip, index) => (
                    <li key={index} className="text-sm text-gray-700 dark:text-gray-300">
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Additional Info Section */}
            <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    カテゴリー:
                  </span>
                  <span className="ml-2 text-gray-700 dark:text-gray-300">
                    {exercise.category}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    難易度:
                  </span>
                  <span className="ml-2 text-gray-700 dark:text-gray-300">
                    {getDifficultyText(exercise.difficulty)}
                  </span>
                </div>
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>
      </CardContent>
    </Card>
  );
};

export default EnhancedExerciseCard;