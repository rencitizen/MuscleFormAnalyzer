/**
 * Generate PWA icons from source image
 * This script creates the required icon sizes for PWA
 */

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const sourceIcon = path.join(__dirname, '../../generated-icon.png');
const publicDir = path.join(__dirname, '../public');

const sizes = [
  { size: 192, name: 'icon-192x192.png' },
  { size: 512, name: 'icon-512x512.png' },
  { size: 180, name: 'apple-touch-icon.png' },
  { size: 32, name: 'favicon-32x32.png' },
  { size: 16, name: 'favicon-16x16.png' }
];

async function generateIcons() {
  try {
    // Check if source icon exists
    if (!fs.existsSync(sourceIcon)) {
      console.error('Source icon not found:', sourceIcon);
      process.exit(1);
    }

    // Create public directory if it doesn't exist
    if (!fs.existsSync(publicDir)) {
      fs.mkdirSync(publicDir, { recursive: true });
    }

    // Generate icons
    for (const { size, name } of sizes) {
      const outputPath = path.join(publicDir, name);
      
      await sharp(sourceIcon)
        .resize(size, size, {
          fit: 'contain',
          background: { r: 255, g: 255, b: 255, alpha: 0 }
        })
        .png()
        .toFile(outputPath);
      
      console.log(`Generated ${name} (${size}x${size})`);
    }

    // Also create a favicon.ico (multi-size)
    await sharp(sourceIcon)
      .resize(32, 32)
      .png()
      .toFile(path.join(publicDir, 'favicon.ico'));
    
    console.log('All icons generated successfully!');
  } catch (error) {
    console.error('Error generating icons:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  generateIcons();
}

module.exports = generateIcons;