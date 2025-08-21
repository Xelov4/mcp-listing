const https = require('https');
const fs = require('fs');

// Alternative solution using a headless browser service
// This would typically use a service like browserless.io, but let's try a different approach

async function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
    req.end();
  });
}

async function scrapeCursorDirectoryAlternative() {
  console.log('Attempting alternative scraping approach...');
  
  try {
    // First, let's try to get the page with different user agents and headers
    const userAgents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ];
    
    for (const userAgent of userAgents) {
      console.log(`Trying with User-Agent: ${userAgent.substring(0, 50)}...`);
      
      const options = {
        method: 'GET',
        headers: {
          'User-Agent': userAgent,
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'identity', // Disable compression for simplicity
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
        }
      };
      
      try {
        const html = await makeRequest('https://www.cursor.directory/mcp', options);
        console.log(`Response length: ${html.length}`);
        
        // More aggressive pattern matching
        const patterns = [
          // Look for Next.js data
          /"props":\s*({.*?"pageProps".*?})/s,
          /"pageProps":\s*({.*?})/s,
          // Look for any large JSON arrays
          /\[{.*?"id".*?}.*?\]/gs,
          // Look for href patterns
          /href="\/mcp\/[^"]+"/g,
          // Look for server data
          /"servers":\s*(\[.*?\])/s,
          /"data":\s*(\[.*?\])/s
        ];
        
        let foundData = [];
        let foundLinks = new Set();
        
        for (const pattern of patterns) {
          const matches = html.match(pattern);
          if (matches) {
            console.log(`Found ${matches.length} matches with pattern`);
            matches.forEach((match, i) => {
              if (match.includes('/mcp/')) {
                const hrefMatch = match.match(/href="([^"]+)"/);
                if (hrefMatch) {
                  foundLinks.add('https://www.cursor.directory' + hrefMatch[1]);
                }
              }
              
              // Try to parse as JSON
              if (match.startsWith('{') || match.startsWith('[')) {
                try {
                  const parsed = JSON.parse(match);
                  if (Array.isArray(parsed) && parsed.length > 0) {
                    foundData.push(...parsed);
                  } else if (typeof parsed === 'object') {
                    foundData.push(parsed);
                  }
                } catch (e) {
                  // Not valid JSON, skip
                }
              }
            });
          }
        }
        
        // Look for script tags with JSON data
        const scriptMatches = html.match(/<script[^>]*>([^<]*)</g);
        if (scriptMatches) {
          console.log(`Found ${scriptMatches.length} script tags`);
          scriptMatches.forEach(script => {
            if (script.includes('mcp') || script.includes('server')) {
              console.log(`Analyzing script of length ${script.length}`);
              
              // Look for JSON-like structures
              const jsonMatches = script.match(/\{[^{}]*"[^"]*"[^{}]*\}/g);
              if (jsonMatches) {
                jsonMatches.forEach(jsonStr => {
                  try {
                    const parsed = JSON.parse(jsonStr);
                    if (parsed.id || parsed.name || parsed.link) {
                      foundData.push(parsed);
                    }
                  } catch (e) {
                    // Not valid JSON
                  }
                });
              }
            }
          });
        }
        
        console.log(`Found ${foundLinks.size} unique links and ${foundData.length} data objects`);
        
        if (foundLinks.size > 11 || foundData.length > 0) {
          // We found more data than the static scraper
          break;
        }
      } catch (err) {
        console.log(`Failed with this user agent: ${err.message}`);
        continue;
      }
    }
    
    console.log('Alternative scraping complete');
    
  } catch (error) {
    console.error('Error in alternative scraping:', error);
  }
}

// Let's also try to use Node.js to emulate some JavaScript execution
async function simulateJavaScriptExecution() {
  console.log('Attempting to simulate JavaScript execution...');
  
  // This is a very basic approach - in a real scenario, we'd need a proper JS engine
  try {
    const { VM } = require('vm2');
    console.log('VM2 available - we could execute some JavaScript safely');
  } catch (e) {
    console.log('VM2 not available, cannot safely execute JavaScript');
  }
}

async function main() {
  await scrapeCursorDirectoryAlternative();
  await simulateJavaScriptExecution();
}

main().catch(console.error);