const puppeteer = require('puppeteer');
const path = require('path');

async function takeScreenshot() {
  const browser = await puppeteer.launch({
    headless: false, // Set to true for headless mode
    defaultViewport: { width: 1400, height: 1000 }
  });

  try {
    const page = await browser.newPage();
    
    // Set up console logging BEFORE navigating
    page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();
      console.log(`[CONSOLE ${type.toUpperCase()}]: ${text}`);
    });
    
    page.on('pageerror', err => {
      console.log(`[PAGE ERROR]: ${err.message}`);
    });
    
    page.on('requestfailed', request => {
      console.log(`[REQUEST FAILED]: ${request.url()} - ${request.failure().errorText}`);
    });
    
    // Navigate to the local server
    const url = 'http://localhost:8080';
    console.log(`Loading: ${url}`);
    
    await page.goto(url, { waitUntil: 'networkidle0' });
    
    // Wait a bit more for any dynamic content
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Take screenshot
    await page.screenshot({ 
      path: 'tmp/frontend-screenshot.png', 
      fullPage: true 
    });
    
    console.log('Screenshot saved as tmp/frontend-screenshot.png');
    
  } catch (error) {
    console.error('Error taking screenshot:', error);
  } finally {
    await browser.close();
  }
}

takeScreenshot();