'use client';

import React from 'react';
import { ExerciseBrowser } from '@/components/training/ExerciseBrowser';
import Link from 'next/link';
import { ChevronLeft } from 'lucide-react';

export default function ExerciseBrowserPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link 
            href="/training"
            className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-4"
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            トレーニングに戻る
          </Link>
        </div>

        {/* Exercise Browser */}
        <ExerciseBrowser />
      </div>
    </div>
  );
}