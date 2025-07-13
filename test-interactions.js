const puppeteer = require('puppeteer');

async function testInteractions() {
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
      console.log(`[CONSOLE ${type.toUpperCase()}]: ${text}`);
    });
    
    // Navigate to the local server
    const url = 'http://localhost:8080';
    console.log(`Loading: ${url}`);
    
    await page.goto(url, { waitUntil: 'networkidle0' });
    
    // Wait for page to fully load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    console.log('\n=== Testing Search Filter ===');
    // Test search functionality
    await page.type('#quickFilter', 'restaurant');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Take screenshot after search
    await page.screenshot({ 
      path: 'tmp/test-search-filter.png', 
      fullPage: true 
    });
    console.log('Screenshot saved after search filter');
    
    // Clear search
    await page.evaluate(() => {
      document.getElementById('quickFilter').value = '';
      document.getElementById('quickFilter').dispatchEvent(new Event('input'));
    });
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('\n=== Testing Pagination ===');
    // Test pagination - click next page
    await page.click('.ag-paging-button[aria-label="Next Page"]');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Take screenshot after pagination
    await page.screenshot({ 
      path: 'tmp/test-pagination.png', 
      fullPage: true 
    });
    console.log('Screenshot saved after pagination');
    
    console.log('\nInteraction testing complete');
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
}

testInteractions();