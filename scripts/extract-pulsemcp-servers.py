#!/usr/bin/env python3

import requests
import re
from datetime import datetime

def extract_pulsemcp_servers():
    """Extract all server URLs from PulseMCP sitemap"""
    
    print("Fetching PulseMCP sitemap...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get('https://www.pulsemcp.com/sitemap.xml', headers=headers)
        response.raise_for_status()
        
        print(f"Sitemap loaded successfully. Content length: {len(response.text)}")
        
        # Extract all URLs containing /servers/
        print("Extracting server URLs...")
        server_urls = []
        
        # Look for URLs in XML format
        url_patterns = [
            r'<loc>(https://www\.pulsemcp\.com/servers/[^<]+)</loc>',
            r'https://www\.pulsemcp\.com/servers/[^\s<>"]+',
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, response.text)
            server_urls.extend(matches)
        
        # Remove duplicates while preserving order
        unique_urls = []
        seen = set()
        for url in server_urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
        
        print(f"Found {len(unique_urls)} unique server URLs")
        
        if unique_urls:
            # Generate markdown content
            markdown = f"""# PulseMCP Servers

## Summary
- **Total servers found**: {len(unique_urls)}
- **Source**: https://www.pulsemcp.com/sitemap.xml
- **Date extracted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## All Server URLs

"""
            
            # Add numbered list
            for i, url in enumerate(unique_urls, 1):
                # Extract server name from URL
                server_name = url.split('/servers/')[-1]
                display_name = server_name.replace('-', ' ').title()
                markdown += f"{i}. [{display_name}]({url})\n"
            
            # Add raw URLs section
            markdown += f"""

## Raw URLs List

```
"""
            for url in unique_urls:
                markdown += f"{url}\n"
            
            markdown += "```\n"
            
            # Save to file
            filename = '/home/xelova/mcp-listing/pulsemcp-servers.md'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"✅ Results saved to: {filename}")
            
            # Also save simple URL list
            url_filename = '/home/xelova/mcp-listing/pulsemcp_server_urls.txt'
            with open(url_filename, 'w') as f:
                for url in unique_urls:
                    f.write(url + '\n')
            
            print(f"✅ URL list saved to: {url_filename}")
            print(f"📊 Total servers: {len(unique_urls)}")
            
            return unique_urls
        else:
            print("❌ No server URLs found")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == '__main__':
    extract_pulsemcp_servers()