const puppeteer = require('puppeteer');
const fs = require('fs');

async function scrapeCursorDirectory() {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({ 
    headless: true,
    args: [
      '--no-sandbox', 
      '--disable-setuid-sandbox', 
      '--disable-dev-shm-usage', 
      '--disable-gpu',
      '--disable-web-security',
      '--disable-features=VizDisplayCompositor',
      '--single-process',
      '--no-zygote'
    ]
  });
  
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to cursor.directory/mcp...');
    await page.goto('https://www.cursor.directory/mcp', { waitUntil: 'networkidle2' });
    
    console.log('Waiting for initial content to load...');
    await page.waitForTimeout(3000);
    
    console.log('Scrolling to load dynamic content...');
    let previousHeight = 0;
    let currentHeight = await page.evaluate(() => document.body.scrollHeight);
    let scrollAttempts = 0;
    const maxScrollAttempts = 20; // Prevent infinite loop
    
    // Keep scrolling until no more content loads
    while (currentHeight > previousHeight && scrollAttempts < maxScrollAttempts) {
      previousHeight = currentHeight;
      
      // Scroll to bottom
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      
      // Wait for content to load
      await page.waitForTimeout(3000);
      
      // Check for new height
      currentHeight = await page.evaluate(() => document.body.scrollHeight);
      scrollAttempts++;
      
      console.log(`Scroll attempt ${scrollAttempts}: Height ${currentHeight}px`);
    }
    
    console.log('Extracting all links...');
    const links = await page.evaluate(() => {
      const allLinks = Array.from(document.querySelectorAll('a[href]'));
      return allLinks.map(link => ({
        href: link.href,
        text: link.textContent.trim(),
        title: link.title || ''
      })).filter(link => link.href && link.href !== 'javascript:void(0)');
    });
    
    // Remove duplicates
    const uniqueLinks = links.reduce((acc, link) => {
      if (!acc.find(l => l.href === link.href)) {
        acc.push(link);
      }
      return acc;
    }, []);
    
    console.log(`Found ${uniqueLinks.length} unique links`);
    
    // Create markdown content
    let markdown = '# Cursor Directory MCP - All Links (Dynamic Scraping)\\n\\n';
    markdown += `Extracted from: https://www.cursor.directory/mcp\\n`;
    markdown += `Date: ${new Date().toISOString()}\\n`;
    markdown += `Total links found: ${uniqueLinks.length}\\n`;
    markdown += `Scroll attempts: ${scrollAttempts}\\n\\n`;
    
    // Categorize links
    const categories = {
      navigation: [],
      mcp_servers: [],
      external: [],
      other: []
    };
    
    uniqueLinks.forEach(link => {
      if (link.href.includes('cursor.directory')) {
        if (link.href.includes('/mcp/') && !link.href.endsWith('/mcp') && !link.href.endsWith('/mcp/new')) {
          categories.mcp_servers.push(link);
        } else {
          categories.navigation.push(link);
        }
      } else {
        categories.external.push(link);
      }
    });
    
    // Write categorized markdown
    if (categories.navigation.length > 0) {
      markdown += '## Navigation Links\\n\\n';
      categories.navigation.forEach(link => {
        markdown += `- [${link.text || 'Link'}](${link.href})\\n`;
      });
      markdown += '\\n';
    }
    
    if (categories.mcp_servers.length > 0) {
      markdown += '## MCP Server Listings\\n\\n';
      categories.mcp_servers.forEach(link => {
        markdown += `- [${link.text || 'MCP Server'}](${link.href})\\n`;
      });
      markdown += '\\n';
    }
    
    if (categories.external.length > 0) {
      markdown += '## External Links\\n\\n';
      categories.external.forEach(link => {
        markdown += `- [${link.text || 'External Link'}](${link.href})\\n`;
      });
      markdown += '\\n';
    }
    
    // Write raw list as well
    markdown += '## All Links (Raw)\\n\\n';
    uniqueLinks.forEach(link => {
      markdown += `- ${link.href}\\n`;
    });
    
    const filename = '/home/xelova/mcp-listing/cursor_directory_mcp_dynamic_scrape.md';
    fs.writeFileSync(filename, markdown);
    console.log(`Results saved to ${filename}`);
    
    return uniqueLinks;
    
  } catch (error) {
    console.error('Error during scraping:', error);
  } finally {
    await browser.close();
  }
}

scrapeCursorDirectory();