#!/usr/bin/env python3

import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_mcp_data():
    print("Fetching cursor.directory/mcp page...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get('https://www.cursor.directory/mcp', headers=headers)
        response.raise_for_status()
        
        print(f"Page loaded successfully. Content length: {len(response.text)}")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all links
        print("Extracting all links...")
        all_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Convert relative URLs to absolute
            if href.startswith('/'):
                href = urljoin('https://www.cursor.directory', href)
            elif not href.startswith(('http://', 'https://')):
                continue
                
            text = link.get_text(strip=True)
            title = link.get('title', '')
            
            all_links.append({
                'href': href,
                'text': text,
                'title': title
            })
        
        # Remove duplicates
        unique_links = []
        seen_hrefs = set()
        for link in all_links:
            if link['href'] not in seen_hrefs:
                unique_links.append(link)
                seen_hrefs.add(link['href'])
        
        print(f"Found {len(unique_links)} unique links")
        
        # Look for JavaScript data
        print("Looking for embedded JavaScript data...")
        scripts = soup.find_all('script')
        
        mcp_data = []
        for script in scripts:
            if script.string:
                # Look for JSON-like data structures
                text = script.string
                
                # Try to find data patterns
                if 'mcp' in text.lower() or 'server' in text.lower():
                    print(f"Found potentially relevant script (length: {len(text)})")
                    
                    # Look for JSON structures
                    json_patterns = [
                        r'"data":\s*(\[.*?\])',
                        r'"servers":\s*(\[.*?\])',
                        r'"mcps":\s*(\[.*?\])',
                        r'\[{[^}]*"id"[^}]*}[^\]]*\]'
                    ]
                    
                    for pattern in json_patterns:
                        matches = re.findall(pattern, text, re.DOTALL)
                        for match in matches:
                            try:
                                data = json.loads(match)
                                if isinstance(data, list) and len(data) > 5:  # Likely MCP data
                                    print(f"Found JSON array with {len(data)} items")
                                    mcp_data.extend(data)
                            except json.JSONDecodeError:
                                continue
        
        # Categorize links
        categories = {
            'navigation': [],
            'mcp_servers': [],
            'external': [],
            'other': []
        }
        
        for link in unique_links:
            href = link['href']
            if 'cursor.directory' in href:
                if '/mcp/' in href and not href.endswith('/mcp') and not href.endswith('/mcp/new'):
                    categories['mcp_servers'].append(link)
                else:
                    categories['navigation'].append(link)
            else:
                categories['external'].append(link)
        
        # Generate markdown
        markdown = '# Cursor Directory MCP - All Links (Static Scraping)\n\n'
        markdown += f'Extracted from: https://www.cursor.directory/mcp\n'
        markdown += f'Date: {requests.utils.default_headers()}\n'
        markdown += f'Total links found: {len(unique_links)}\n'
        markdown += f'MCP data items found: {len(mcp_data)}\n\n'
        
        if categories['navigation']:
            markdown += '## Navigation Links\n\n'
            for link in categories['navigation']:
                markdown += f'- [{link["text"] or "Link"}]({link["href"]})\n'
            markdown += '\n'
        
        if categories['mcp_servers']:
            markdown += '## MCP Server Listings\n\n'
            for link in categories['mcp_servers']:
                markdown += f'- [{link["text"] or "MCP Server"}]({link["href"]})\n'
            markdown += '\n'
        
        if categories['external']:
            markdown += '## External Links\n\n'
            for link in categories['external']:
                markdown += f'- [{link["text"] or "External Link"}]({link["href"]})\n'
            markdown += '\n'
        
        # Add extracted MCP data if found
        if mcp_data:
            markdown += '## Extracted MCP Data\n\n'
            for item in mcp_data[:50]:  # Limit to first 50 items
                if isinstance(item, dict):
                    name = item.get('name', item.get('title', 'Unknown'))
                    link = item.get('link', item.get('url', ''))
                    description = item.get('description', '')[:100]
                    markdown += f'- **{name}**: {description}{"..." if len(str(description)) >= 100 else ""}\n'
                    if link:
                        markdown += f'  - Link: {link}\n'
            markdown += '\n'
        
        # Add raw links
        markdown += '## All Links (Raw)\n\n'
        for link in unique_links:
            markdown += f'- {link["href"]}\n'
        
        # Save to file
        filename = '/home/xelova/mcp-listing/cursor_directory_mcp_static_scrape.md'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f'Results saved to {filename}')
        
        return unique_links, mcp_data
        
    except Exception as e:
        print(f'Error: {e}')
        return [], []

if __name__ == '__main__':
    extract_mcp_data()