#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 Validating UI components...\n');

// List of required UI components
const requiredComponents = [
  'button',
  'card',
  'dialog',
  'input',
  'label',
  'select',
  'textarea',
  'toast',
  'progress',
  'badge',
  'alert',
  'switch',
  'slider',
  'tabs',
];

// Check components directory
const componentsDir = path.join(__dirname, '../components/ui');
const libDir = path.join(__dirname, '../lib');

// Validate UI components
const missingComponents = [];
const existingComponents = [];

requiredComponents.forEach(component => {
  const componentPath = path.join(componentsDir, `${component}.tsx`);
  if (fs.existsSync(componentPath)) {
    existingComponents.push(component);
  } else {
    missingComponents.push(component);
  }
});

// Check lib/utils.ts
const utilsPath = path.join(libDir, 'utils.ts');
const hasUtils = fs.existsSync(utilsPath);

// Report results
console.log(`✅ Found ${existingComponents.length} components:`);
existingComponents.forEach(comp => console.log(`   - ${comp}.tsx`));

if (missingComponents.length > 0) {
  console.log(`\n⚠️  Missing ${missingComponents.length} components:`);
  missingComponents.forEach(comp => console.log(`   - ${comp}.tsx`));
  console.log('\nTo add missing components, run:');
  missingComponents.forEach(comp => {
    console.log(`   npx shadcn-ui@latest add ${comp}`);
  });
}

console.log(`\n📁 lib/utils.ts: ${hasUtils ? '✅ Present' : '❌ Missing'}`);

// Check for import errors in training components
console.log('\n🔍 Checking component imports...\n');

const trainingComponents = [
  'components/training/TrainingRecord.tsx',
  'components/training/RoutineManager.tsx',
  'components/training/TrainingHistory.tsx',
];

let importErrors = 0;

trainingComponents.forEach(file => {
  const filePath = path.join(__dirname, '..', file);
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    const importRegex = /import.*from\s+['"]\.\.\/ui\/([\w-]+)['"]/g;
    let match;
    
    while ((match = importRegex.exec(content)) !== null) {
      const componentName = match[1];
      const componentPath = path.join(componentsDir, `${componentName}.tsx`);
      
      if (!fs.existsSync(componentPath)) {
        console.log(`❌ ${file}: imports missing component 'ui/${componentName}'`);
        importErrors++;
      }
    }
  }
});

if (importErrors === 0) {
  console.log('✅ All component imports are valid\n');
} else {
  console.log(`\n❌ Found ${importErrors} import errors\n`);
}

// Exit with error if issues found
if (missingComponents.length > 0 || !hasUtils || importErrors > 0) {
  console.log('❌ Validation failed! Please fix the issues above.\n');
  process.exit(1);
} else {
  console.log('✅ All validations passed!\n');
  process.exit(0);
}