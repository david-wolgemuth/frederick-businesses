const puppeteer = require('puppeteer');

const breakpoints = {
  mobile: { width: 375, height: 667, name: 'mobile' },
  tablet: { width: 768, height: 1024, name: 'tablet' },
  desktop: { width: 1200, height: 800, name: 'desktop' },
  large: { width: 1400, height: 1000, name: 'large' }
};

async function testResponsive() {
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: { width: 1400, height: 1000 }
  });

  try {
    const page = await browser.newPage();
    
    // Set up console logging
    page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();
      if (type === 'error') {
        console.log(`[CONSOLE ${type.toUpperCase()}]: ${text}`);
      }
    });
    
    const url = 'http://localhost:8080';
    console.log(`Loading: ${url}`);
    
    await page.goto(url, { waitUntil: 'networkidle0' });
    
    // Wait for page to fully load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Test each breakpoint
    for (const [key, viewport] of Object.entries(breakpoints)) {
      console.log(`\n=== Testing ${viewport.name} (${viewport.width}x${viewport.height}) ===`);
      
      // Set viewport size
      await page.setViewport({
        width: viewport.width,
        height: viewport.height
      });
      
      // Wait for layout to adjust
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Force map resize
      await page.evaluate(() => {
        if (window.map) {
          setTimeout(() => window.map.invalidateSize(), 100);
        }
      });
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Take screenshot
      await page.screenshot({ 
        path: `tmp/responsive-${viewport.name}-${viewport.width}x${viewport.height}.png`, 
        fullPage: true 
      });
      
      console.log(`✓ Screenshot saved: responsive-${viewport.name}-${viewport.width}x${viewport.height}.png`);
      
      // Test search functionality at this breakpoint
      if (key === 'tablet') {
        console.log('  Testing search at tablet size...');
        await page.type('#quickFilter', 'restaurant');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        await page.screenshot({ 
          path: `tmp/responsive-${viewport.name}-search.png`, 
          fullPage: true 
        });
        console.log('  ✓ Search test screenshot saved');
        
        // Clear search
        await page.evaluate(() => {
          document.getElementById('quickFilter').value = '';
          document.getElementById('quickFilter').dispatchEvent(new Event('input'));
        });
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
    
    console.log('\n=== Responsive testing complete ===');
    console.log('Screenshots saved in tmp/ directory');
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
}

testResponsive();