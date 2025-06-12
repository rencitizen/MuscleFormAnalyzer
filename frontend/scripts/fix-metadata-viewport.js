#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🔍 Fixing metadata viewport exports...\n');

// Find all page.tsx files
const pageFiles = glob.sync('app/**/page.tsx', { 
  cwd: path.join(__dirname, '..'),
  absolute: true 
});

let fixedCount = 0;
let errorCount = 0;

pageFiles.forEach(file => {
  try {
    let content = fs.readFileSync(file, 'utf8');
    let modified = false;

    // Check if file has metadata with viewport or themeColor
    if (content.includes('metadata') && (content.includes('viewport:') || content.includes('themeColor:'))) {
      // Pattern 1: metadata object with viewport
      content = content.replace(
        /export const metadata[^{]*{([^}]*)viewport:\s*['"`]([^'"`]*)['"`]([^}]*)}/gs,
        (match, before, viewportValue, after) => {
          modified = true;
          return `export const metadata = {${before}${after}}\n\nexport const viewport = {\n  width: 'device-width',\n  initialScale: 1,\n}`;
        }
      );

      // Pattern 2: metadata object with themeColor
      content = content.replace(
        /export const metadata[^{]*{([^}]*)themeColor:\s*['"`]([^'"`]*)['"`]([^}]*)}/gs,
        (match, before, themeColorValue, after) => {
          modified = true;
          return `export const metadata = {${before}${after}}\n\nexport const viewport = {\n  width: 'device-width',\n  initialScale: 1,\n  themeColor: '${themeColorValue}',\n}`;
        }
      );

      // Pattern 3: Metadata type with viewport/themeColor
      if (content.includes(': Metadata =') && (content.includes('viewport:') || content.includes('themeColor:'))) {
        // Extract viewport and themeColor values
        const viewportMatch = content.match(/viewport:\s*['"`]([^'"`]*)['"`]/);
        const themeColorMatch = content.match(/themeColor:\s*['"`]([^'"`]*)['"`]/);
        
        if (viewportMatch || themeColorMatch) {
          // Remove viewport and themeColor from metadata
          content = content.replace(/viewport:\s*['"`][^'"`]*['"`],?\s*/g, '');
          content = content.replace(/themeColor:\s*['"`][^'"`]*['"`],?\s*/g, '');
          
          // Add viewport export if not already present
          if (!content.includes('export const viewport')) {
            let viewportExport = '\n\nexport const viewport = {\n  width: \'device-width\',\n  initialScale: 1,\n';
            
            if (themeColorMatch) {
              viewportExport += `  themeColor: '${themeColorMatch[1]}',\n`;
            }
            
            viewportExport += '}';
            
            // Insert viewport export after metadata
            const metadataEndIndex = content.search(/export const metadata[^}]*}/);
            if (metadataEndIndex !== -1) {
              const insertPoint = content.indexOf('}', metadataEndIndex) + 1;
              content = content.slice(0, insertPoint) + viewportExport + content.slice(insertPoint);
              modified = true;
            }
          }
        }
      }
    }

    if (modified) {
      fs.writeFileSync(file, content);
      console.log(`✅ Fixed: ${path.relative(path.join(__dirname, '..'), file)}`);
      fixedCount++;
    }
  } catch (error) {
    console.error(`❌ Error processing ${file}:`, error.message);
    errorCount++;
  }
});

console.log(`\n📊 Summary:`);
console.log(`   Fixed: ${fixedCount} files`);
console.log(`   Errors: ${errorCount} files`);
console.log(`   Total: ${pageFiles.length} files checked\n`);

if (errorCount > 0) {
  process.exit(1);
}