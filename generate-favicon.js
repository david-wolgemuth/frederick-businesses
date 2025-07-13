const sharp = require('sharp');
const fs = require('fs');

async function generateFavicons() {
  try {
    // Read the SVG file
    const svgBuffer = fs.readFileSync('favicon.svg');
    
    // Generate different sizes
    const sizes = [16, 32, 48, 180, 192, 512];
    
    console.log('Generating favicon files...');
    
    // Generate PNG files for different sizes
    for (const size of sizes) {
      await sharp(svgBuffer)
        .resize(size, size)
        .png()
        .toFile(`favicon-${size}x${size}.png`);
      console.log(`✓ Generated favicon-${size}x${size}.png`);
    }
    
    // Generate the main favicon.ico (16x16)
    await sharp(svgBuffer)
      .resize(16, 16)
      .png()
      .toFile('favicon.ico');
    console.log('✓ Generated favicon.ico');
    
    // Generate apple-touch-icon
    await sharp(svgBuffer)
      .resize(180, 180)
      .png()
      .toFile('apple-touch-icon.png');
    console.log('✓ Generated apple-touch-icon.png');
    
    console.log('\nFavicon generation complete!');
    console.log('Files generated:');
    console.log('- favicon.ico (16x16)');
    console.log('- apple-touch-icon.png (180x180)');
    sizes.forEach(size => {
      console.log(`- favicon-${size}x${size}.png`);
    });
    
  } catch (error) {
    console.error('Error generating favicons:', error);
  }
}

generateFavicons();