#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Map of files and their @/ imports to relative paths
const importMappings = {
  // components/pose-analysis/PoseAnalyzerEnhanced.tsx
  'components/pose-analysis/PoseAnalyzerEnhanced.tsx': {
    '@/components/ui/card': '../ui/card',
    '@/components/ui/button': '../ui/button',
    '@/components/ui/badge': '../ui/badge',
    '@/components/ui/progress': '../ui/progress',
    '@/components/ui/alert': '../ui/alert'
  },
  
  // components/pose-analysis/CameraGuide.tsx
  'components/pose-analysis/CameraGuide.tsx': {
    '@/components/ui/card': '../ui/card',
    '@/components/ui/alert': '../ui/alert',
    '@/components/ui/progress': '../ui/progress'
  },
  
  // components/pose-analysis/CalibrationModal.tsx
  'components/pose-analysis/CalibrationModal.tsx': {
    '@/components/ui/dialog': '../ui/dialog',
    '@/components/ui/button': '../ui/button',
    '@/components/ui/input': '../ui/input',
    '@/components/ui/label': '../ui/label',
    '@/components/ui/slider': '../ui/slider',
    '@/lib/mediapipe/types': '../../lib/mediapipe/types',
    '@/lib/calibration/personalizedAnalyzer': '../../lib/calibration/personalizedAnalyzer'
  },
  
  // components/pose-analysis/ExerciseSelector.tsx
  'components/pose-analysis/ExerciseSelector.tsx': {
    '@/components/ui/tabs': '../ui/tabs',
    '@/components/ui/card': '../ui/card'
  },
  
  // components/pose-analysis/AnalysisResults.tsx
  'components/pose-analysis/AnalysisResults.tsx': {
    '@/components/ui/button': '../ui/button',
    '@/components/ui/card': '../ui/card',
    '@/components/ui/progress': '../ui/progress',
    '@/lib/mediapipe/types': '../../lib/mediapipe/types',
    '@/lib/analysis/exerciseAnalyzer': '../../lib/analysis/exerciseAnalyzer'
  },
  
  // app/analyze/page.tsx
  'app/analyze/page.tsx': {
    '@/components/ui/button': '../../components/ui/button',
    '@/components/ui/card': '../../components/ui/card',
    '@/lib/mediapipe/usePoseDetection': '../../lib/mediapipe/usePoseDetection',
    '@/lib/mediapipe/types': '../../lib/mediapipe/types',
    '@/components/pose-analysis/ExerciseSelector': '../../components/pose-analysis/ExerciseSelector',
    '@/components/pose-analysis/CalibrationModal': '../../components/pose-analysis/CalibrationModal',
    '@/components/pose-analysis/AnalysisResults': '../../components/pose-analysis/AnalysisResults'
  },
  
  // app/layout.tsx
  'app/layout.tsx': {
    '@/components/ui/toaster': '../components/ui/toaster',
    '@/components/providers/AuthProvider': '../components/providers/AuthProvider',
    '@/components/providers/ThemeProvider': '../components/providers/ThemeProvider',
    '@/components/layout/MobileNav': '../components/layout/MobileNav'
  },
  
  // app/page.tsx
  'app/page.tsx': {
    '@/components/ui/button': '../components/ui/button',
    '@/components/ui/card': '../components/ui/card'
  },
  
  // app/exercises/page.tsx
  'app/exercises/page.tsx': {
    '@/components/ui/card': '../../components/ui/card',
    '@/components/ui/button': '../../components/ui/button',
    '@/components/ui/tabs': '../../components/ui/tabs'
  },
  
  // app/progress/page.tsx
  'app/progress/page.tsx': {
    '@/components/ui/card': '../../components/ui/card',
    '@/components/ui/button': '../../components/ui/button',
    '@/components/ui/tabs': '../../components/ui/tabs',
    '@/lib/firebase': '../../lib/firebase'
  },
  
  // app/auth/login/page.tsx
  'app/auth/login/page.tsx': {
    '@/components/ui/button': '../../../components/ui/button',
    '@/components/ui/card': '../../../components/ui/card',
    '@/components/ui/input': '../../../components/ui/input',
    '@/components/ui/label': '../../../components/ui/label',
    '@/lib/firebase': '../../../lib/firebase'
  },
  
  // app/nutrition/tracking/page.tsx
  'app/nutrition/tracking/page.tsx': {
    '@/components/nutrition/NutritionDashboard': '../../../components/nutrition/NutritionDashboard'
  },
  
  // app/nutrition/history/page.tsx
  'app/nutrition/history/page.tsx': {
    '@/components/nutrition/MealHistory': '../../../components/nutrition/MealHistory'
  },
  
  // app/nutrition/enhanced-page.tsx
  'app/nutrition/enhanced-page.tsx': {
    '@/components/ui/card': '../../components/ui/card',
    '@/components/ui/button': '../../components/ui/button',
    '@/components/ui/tabs': '../../components/ui/tabs',
    '@/components/ui/input': '../../components/ui/input',
    '@/components/ui/label': '../../components/ui/label',
    '@/components/ui/progress': '../../components/ui/progress',
    '@/lib/storage/mealStorage': '../../lib/storage/mealStorage',
    '@/lib/supabase/mealSync': '../../lib/supabase/mealSync'
  },
  
  // components/layout/MobileNav.tsx
  'components/layout/MobileNav.tsx': {
    '@/components/ui/button': '../ui/button'
  },
  
  // components/providers/AuthProvider.tsx
  'components/providers/AuthProvider.tsx': {
    '@/lib/firebase': '../../lib/firebase'
  },
  
  // components/providers/ThemeProvider.tsx
  'components/providers/ThemeProvider.tsx': {
    // No @/ imports in this file based on typical theme provider patterns
  },
  
  // components/nutrition/NutritionDashboard.tsx
  'components/nutrition/NutritionDashboard.tsx': {
    '@/components/ui/card': '../ui/card',
    '@/components/ui/button': '../ui/button',
    '@/components/ui/tabs': '../ui/tabs',
    '@/components/ui/input': '../ui/input',
    '@/components/ui/label': '../ui/label',
    '@/components/ui/progress': '../ui/progress',
    '@/lib/storage/mealStorage': '../../lib/storage/mealStorage'
  },
  
  // components/nutrition/MealHistory.tsx
  'components/nutrition/MealHistory.tsx': {
    '@/components/ui/card': '../ui/card',
    '@/components/ui/button': '../ui/button',
    '@/lib/storage/mealStorage': '../../lib/storage/mealStorage'
  },
  
  // All UI components
  'components/ui/button.tsx': {
    '@/lib/utils': '../../lib/utils'
  },
  'components/ui/card.tsx': {
    '@/lib/utils': '../../lib/utils'
  },
  'components/ui/dialog.tsx': {
    '@/lib/utils': '../../lib/utils'
  },
  'components/ui/input.tsx': {
    '@/lib/utils': '../../lib/utils'
  },
  'components/ui/label.tsx': {
    '@/lib/utils': '../../lib/utils'
  },
  'components/ui/progress.tsx': {
    '@/lib/utils': '../../lib/utils'
  },
  'components/ui/sheet.tsx': {
    '@/lib/utils': '../../lib/utils'
  },
  'components/ui/slider.tsx': {
    '@/lib/utils': '../../lib/utils'
  },
  'components/ui/tabs.tsx': {
    '@/lib/utils': '../../lib/utils'
  },
  
  // lib files
  'lib/analysis/exerciseAnalyzer.ts': {
    '@/lib/mediapipe/types': '../mediapipe/types',
    '@/lib/analysis/utils': './utils'
  },
  'lib/analysis/utils.ts': {
    '@/lib/mediapipe/types': '../mediapipe/types'
  },
  'lib/calibration/personalizedAnalyzer.ts': {
    '@/lib/mediapipe/types': '../mediapipe/types',
    '@/lib/analysis/utils': '../analysis/utils'
  },
  'lib/mediapipe/usePoseDetection.ts': {
    // No @/ imports, uses relative ./types
  },
  'lib/supabase/mealSync.ts': {
    '@/lib/supabase/client': './client',
    '@/lib/storage/mealStorage': '../storage/mealStorage'
  }
};

// Process each file
Object.entries(importMappings).forEach(([filePath, imports]) => {
  const fullPath = path.join(__dirname, filePath);
  
  if (!fs.existsSync(fullPath)) {
    console.log(`Skipping ${filePath} - file not found`);
    return;
  }
  
  let content = fs.readFileSync(fullPath, 'utf-8');
  let hasChanges = false;
  
  Object.entries(imports).forEach(([oldImport, newImport]) => {
    const regex = new RegExp(`from ['"]${oldImport.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}['"]`, 'g');
    if (content.match(regex)) {
      content = content.replace(regex, `from '${newImport}'`);
      hasChanges = true;
      console.log(`✓ ${filePath}: ${oldImport} → ${newImport}`);
    }
  });
  
  if (hasChanges) {
    fs.writeFileSync(fullPath, content);
    console.log(`Updated ${filePath}`);
  }
});

console.log('\nImport fixes complete!');