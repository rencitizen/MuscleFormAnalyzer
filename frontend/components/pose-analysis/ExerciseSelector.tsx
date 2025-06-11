'use client'

import { Card } from '../ui/card'
import { cn } from '@/lib/utils'

interface Exercise {
  id: 'squat' | 'deadlift' | 'bench_press'
  name: string
  description: string
  icon: string
}

const exercises: Exercise[] = [
  {
    id: 'squat',
    name: 'スクワット',
    description: '下半身の王道種目',
    icon: '🏋️',
  },
  {
    id: 'deadlift',
    name: 'デッドリフト',
    description: '全身を鍛える種目',
    icon: '💪',
  },
  {
    id: 'bench_press',
    name: 'ベンチプレス',
    description: '上半身の基本種目',
    icon: '🏋️‍♂️',
  },
]

interface ExerciseSelectorProps {
  selectedExercise: Exercise['id']
  onSelectExercise: (exercise: Exercise['id']) => void
}

export function ExerciseSelector({
  selectedExercise,
  onSelectExercise,
}: ExerciseSelectorProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold">種目を選択</h3>
      <div className="grid gap-4 md:grid-cols-3">
        {exercises.map((exercise) => (
          <Card
            key={exercise.id}
            className={cn(
              'cursor-pointer transition-all hover:shadow-md',
              selectedExercise === exercise.id && 'ring-2 ring-primary'
            )}
            onClick={() => onSelectExercise(exercise.id)}
          >
            <div className="p-4 text-center">
              <div className="text-3xl mb-2">{exercise.icon}</div>
              <h4 className="font-semibold">{exercise.name}</h4>
              <p className="text-sm text-muted-foreground">
                {exercise.description}
              </p>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}