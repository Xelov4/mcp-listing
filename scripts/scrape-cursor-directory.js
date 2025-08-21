const { chromium } = require('playwright');
const fs = require('fs');

async function scrapeCursorDirectory() {
  console.log('Launching browser...');
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to cursor.directory/mcp...');
    await page.goto('https://www.cursor.directory/mcp', { waitUntil: 'networkidle' });
    
    console.log('Waiting for initial content to load...');
    await page.waitForTimeout(3000);
    
    console.log('Scrolling to load dynamic content...');
    let previousHeight = 0;
    let currentHeight = await page.evaluate(() => document.body.scrollHeight);
    
    // Keep scrolling until no more content loads
    while (currentHeight > previousHeight) {
      previousHeight = currentHeight;
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(2000); // Wait for content to load
      currentHeight = await page.evaluate(() => document.body.scrollHeight);
      console.log(`Scrolled to height: ${currentHeight}`);
    }
    
    console.log('Extracting all links...');
    const links = await page.evaluate(() => {
      const allLinks = Array.from(document.querySelectorAll('a[href]'));
      return allLinks.map(link => ({
        href: link.href,
        text: link.textContent.trim(),
        title: link.title || ''
      }));
    });
    
    // Remove duplicates and filter
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
    markdown += `Total links found: ${uniqueLinks.length}\\n\\n`;
    
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
    
    fs.writeFileSync('/home/xelova/mcp-listing/cursor_directory_mcp_dynamic_scrape.md', markdown);
    console.log('Results saved to cursor_directory_mcp_dynamic_scrape.md');
    
    return uniqueLinks;
    
  } catch (error) {
    console.error('Error during scraping:', error);
  } finally {
    await browser.close();
  }
}

scrapeCursorDirectory();