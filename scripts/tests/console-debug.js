const puppeteer = require('puppeteer');

async function debugConsole() {
  const browser = await puppeteer.launch({
    headless: true,
    defaultViewport: { width: 1400, height: 1000 }
  });

  try {
    const page = await browser.newPage();
    
    // Set up comprehensive logging
    page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();
      const location = msg.location();
      console.log(`[CONSOLE ${type.toUpperCase()}]: ${text} (${location.url}:${location.lineNumber})`);
    });
    
    page.on('pageerror', err => {
      console.log(`[PAGE ERROR]: ${err.message}`);
      console.log(`Stack: ${err.stack}`);
    });
    
    page.on('requestfailed', request => {
      console.log(`[REQUEST FAILED]: ${request.url()} - ${request.failure().errorText}`);
    });
    
    page.on('response', response => {
      if (!response.ok()) {
        console.log(`[HTTP ERROR]: ${response.status()} ${response.statusText()} - ${response.url()}`);
      }
    });
    
    // Navigate to the local server
    const url = 'http://localhost:8080';
    console.log(`Loading: ${url}`);
    
    await page.goto(url, { waitUntil: 'networkidle0' });
    
    // Wait for page to fully load
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    console.log('Page loaded, console monitoring complete');
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
}

debugConsole();