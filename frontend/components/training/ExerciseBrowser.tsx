'use client';

import React, { useState, useMemo } from 'react';
import { Search, Filter, Dumbbell, Users, TrendingUp, X } from 'lucide-react';
import { COMPLETE_EXERCISE_DATABASE, getExerciseStatistics } from '@/lib/engines/training/completeExerciseDatabase';
import { PHASE2_EXERCISES } from '@/lib/engines/training/exerciseDatabasePhase2';
import { MUSCLE_GROUPS, EQUIPMENT_CATEGORIES, DIFFICULTY_LEVELS } from '@/lib/engines/training/exerciseCategories';
import { Exercise } from '@/lib/engines/training/exerciseDatabase';
import ExerciseCard from './ExerciseCard';

// Merge all exercises
const ALL_EXERCISES = {
  ...COMPLETE_EXERCISE_DATABASE,
  ...PHASE2_EXERCISES
};

// Debug logging
console.log('COMPLETE_EXERCISE_DATABASE:', Object.keys(COMPLETE_EXERCISE_DATABASE).length);
console.log('PHASE2_EXERCISES:', Object.keys(PHASE2_EXERCISES).length);
console.log('ALL_EXERCISES:', Object.keys(ALL_EXERCISES).length);

export const ExerciseBrowser: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedMuscle, setSelectedMuscle] = useState<string>('all');
  const [selectedEquipment, setSelectedEquipment] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);

  // Get statistics
  const stats = useMemo(() => {
    const exercises = Object.values(ALL_EXERCISES);
    return {
      total: exercises.length,
      byCategory: {
        compound: exercises.filter(e => e.category === 'compound').length,
        isolation: exercises.filter(e => e.category === 'isolation').length,
        cardio: exercises.filter(e => e.category === 'cardio').length,
        core: exercises.filter(e => e.category === 'core').length,
      },
      byDifficulty: {
        beginner: exercises.filter(e => e.difficulty === 'beginner').length,
        intermediate: exercises.filter(e => e.difficulty === 'intermediate').length,
        advanced: exercises.filter(e => e.difficulty === 'advanced').length,
      },
      bodyweightOnly: exercises.filter(e => e.equipment.includes('none')).length
    };
  }, []);

  // Filter exercises
  const filteredExercises = useMemo(() => {
    console.log('Filtering exercises, total:', Object.values(ALL_EXERCISES).length);
    return Object.values(ALL_EXERCISES).filter(exercise => {
      // Search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (!exercise.name.toLowerCase().includes(query) && 
            !exercise.nameJa.includes(searchQuery)) {
          return false;
        }
      }

      // Category filter
      if (selectedCategory !== 'all' && exercise.category !== selectedCategory) {
        return false;
      }

      // Muscle filter
      if (selectedMuscle !== 'all') {
        if (!exercise.primaryMuscles.includes(selectedMuscle) && 
            !exercise.secondaryMuscles.includes(selectedMuscle)) {
          return false;
        }
      }

      // Equipment filter
      if (selectedEquipment !== 'all') {
        if (!exercise.equipment.includes(selectedEquipment)) {
          return false;
        }
      }

      // Difficulty filter
      if (selectedDifficulty !== 'all' && exercise.difficulty !== selectedDifficulty) {
        return false;
      }

      return true;
    });
  }, [searchQuery, selectedCategory, selectedMuscle, selectedEquipment, selectedDifficulty]);

  // Get unique muscle groups from exercises
  const muscleGroups = useMemo(() => {
    const muscles = new Set<string>();
    Object.values(ALL_EXERCISES).forEach(exercise => {
      exercise.primaryMuscles.forEach(muscle => muscles.add(muscle));
      exercise.secondaryMuscles.forEach(muscle => muscles.add(muscle));
    });
    return Array.from(muscles).sort();
  }, []);

  // Get unique equipment from exercises
  const equipment = useMemo(() => {
    const equip = new Set<string>();
    Object.values(ALL_EXERCISES).forEach(exercise => {
      exercise.equipment.forEach(e => equip.add(e));
    });
    return Array.from(equip).sort();
  }, []);

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('all');
    setSelectedMuscle('all');
    setSelectedEquipment('all');
    setSelectedDifficulty('all');
  };

  const hasActiveFilters = selectedCategory !== 'all' || 
                          selectedMuscle !== 'all' || 
                          selectedEquipment !== 'all' || 
                          selectedDifficulty !== 'all';

  return (
    <div className="w-full">
      {/* Header with Stats */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-4">エクササイズデータベース</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">総種目数</p>
                <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
              </div>
              <Dumbbell className="w-8 h-8 text-blue-500 opacity-50" />
            </div>
          </div>
          
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">複合種目</p>
                <p className="text-2xl font-bold text-green-600">{stats.byCategory.compound}</p>
              </div>
              <Users className="w-8 h-8 text-green-500 opacity-50" />
            </div>
          </div>
          
          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">自重種目</p>
                <p className="text-2xl font-bold text-purple-600">{stats.bodyweightOnly}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-500 opacity-50" />
            </div>
          </div>
          
          <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">初心者向け</p>
                <p className="text-2xl font-bold text-orange-600">{stats.byDifficulty.beginner}</p>
              </div>
              <Filter className="w-8 h-8 text-orange-500 opacity-50" />
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="mb-6 space-y-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="エクササイズ名で検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2 rounded-lg border flex items-center gap-2 transition-colors ${
              hasActiveFilters 
                ? 'bg-blue-50 border-blue-300 text-blue-700' 
                : 'bg-white hover:bg-gray-50'
            }`}
          >
            <Filter className="w-4 h-4" />
            フィルター
            {hasActiveFilters && (
              <span className="ml-1 px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full">
                {[selectedCategory, selectedMuscle, selectedEquipment, selectedDifficulty]
                  .filter(f => f !== 'all').length}
              </span>
            )}
          </button>
        </div>

        {/* Filter Options */}
        {showFilters && (
          <div className="p-4 border rounded-lg space-y-4 bg-gray-50 dark:bg-gray-800">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-semibold">フィルター設定</h3>
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  <X className="w-3 h-3" />
                  クリア
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium mb-2">カテゴリー</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full p-2 border rounded-lg"
                >
                  <option value="all">すべて</option>
                  <option value="compound">複合種目</option>
                  <option value="isolation">単関節種目</option>
                  <option value="cardio">有酸素</option>
                  <option value="core">体幹</option>
                </select>
              </div>

              {/* Muscle Group Filter */}
              <div>
                <label className="block text-sm font-medium mb-2">筋群</label>
                <select
                  value={selectedMuscle}
                  onChange={(e) => setSelectedMuscle(e.target.value)}
                  className="w-full p-2 border rounded-lg"
                >
                  <option value="all">すべて</option>
                  {muscleGroups.map(muscle => (
                    <option key={muscle} value={muscle}>
                      {MUSCLE_GROUPS[muscle as keyof typeof MUSCLE_GROUPS]?.nameJa || muscle}
                    </option>
                  ))}
                </select>
              </div>

              {/* Equipment Filter */}
              <div>
                <label className="block text-sm font-medium mb-2">器具</label>
                <select
                  value={selectedEquipment}
                  onChange={(e) => setSelectedEquipment(e.target.value)}
                  className="w-full p-2 border rounded-lg"
                >
                  <option value="all">すべて</option>
                  {equipment.map(equip => (
                    <option key={equip} value={equip}>
                      {EQUIPMENT_CATEGORIES[equip as keyof typeof EQUIPMENT_CATEGORIES]?.nameJa || equip}
                    </option>
                  ))}
                </select>
              </div>

              {/* Difficulty Filter */}
              <div>
                <label className="block text-sm font-medium mb-2">難易度</label>
                <select
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                  className="w-full p-2 border rounded-lg"
                >
                  <option value="all">すべて</option>
                  <option value="beginner">初心者</option>
                  <option value="intermediate">中級者</option>
                  <option value="advanced">上級者</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results Count */}
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          {filteredExercises.length}件の種目が見つかりました
        </p>
      </div>

      {/* Exercise Grid */}
      {filteredExercises.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">データベースに該当する種目が見つかりません</p>
          <p className="text-gray-400 text-sm mt-2">フィルター条件を変更してみてください</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredExercises.map(exercise => (
          <div
            key={exercise.id}
            className="cursor-pointer transform transition-transform hover:scale-105"
            onClick={() => setSelectedExercise(exercise)}
          >
            <ExerciseCard exercise={exercise} />
          </div>
        ))}
      </div>
      )}

      {/* Exercise Detail Modal */}
      {selectedExercise && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedExercise(null)}
        >
          <div 
            className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-2xl font-bold">{selectedExercise.nameJa}</h3>
                  <p className="text-gray-600">{selectedExercise.name}</p>
                </div>
                <button
                  onClick={() => setSelectedExercise(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <ExerciseCard exercise={selectedExercise} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};