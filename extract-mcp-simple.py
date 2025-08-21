#!/usr/bin/env python3

import requests
import re
import json
from urllib.parse import urljoin

def extract_mcp_data():
    print("Fetching cursor.directory/mcp page...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get('https://www.cursor.directory/mcp', headers=headers)
        response.raise_for_status()
        
        print(f"Page loaded successfully. Content length: {len(response.text)}")
        html = response.text
        
        # Extract all href attributes
        print("Extracting all links...")
        href_pattern = r'href="([^"]*)"'
        all_hrefs = re.findall(href_pattern, html)
        
        # Convert to absolute URLs and clean up
        unique_links = set()
        for href in all_hrefs:
            if href.startswith('/'):
                href = urljoin('https://www.cursor.directory', href)
            elif not href.startswith(('http://', 'https://')):
                continue
            
            if href != 'javascript:void(0)' and href != '#':
                unique_links.add(href)
        
        unique_links = list(unique_links)
        print(f"Found {len(unique_links)} unique links")
        
        # Look for embedded data patterns in JavaScript
        print("Looking for embedded data patterns...")
        
        # Search for common data patterns
        data_patterns = [
            r'"servers"\s*:\s*(\[[^\]]+\])',
            r'"data"\s*:\s*(\[[^\]]+\])',
            r'"mcps"\s*:\s*(\[[^\]]+\])',
            r'\{"id":[^}]+\}',
        ]
        
        found_data = []
        for pattern in data_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    if match.startswith('['):
                        data = json.loads(match)
                        found_data.extend(data if isinstance(data, list) else [data])
                except:
                    # Try to extract individual objects
                    obj_pattern = r'\{[^}]*"id"[^}]*\}'
                    objs = re.findall(obj_pattern, match)
                    for obj in objs:
                        try:
                            parsed = json.loads(obj)
                            found_data.append(parsed)
                        except:
                            continue
        
        # Categorize links
        categories = {
            'navigation': [],
            'mcp_servers': [],
            'external': []
        }
        
        for href in unique_links:
            if 'cursor.directory' in href:
                if '/mcp/' in href and not href.endswith('/mcp') and not href.endswith('/mcp/new'):
                    categories['mcp_servers'].append(href)
                else:
                    categories['navigation'].append(href)
            else:
                categories['external'].append(href)
        
        # Generate markdown
        from datetime import datetime
        markdown = '# Cursor Directory MCP - All Links (Regex Scraping)\\n\\n'
        markdown += f'Extracted from: https://www.cursor.directory/mcp\\n'
        markdown += f'Date: {datetime.now().isoformat()}\\n'
        markdown += f'Total links found: {len(unique_links)}\\n'
        markdown += f'Data objects found: {len(found_data)}\\n\\n'
        
        if categories['navigation']:
            markdown += '## Navigation Links\\n\\n'
            for link in categories['navigation']:
                markdown += f'- {link}\\n'
            markdown += '\\n'
        
        if categories['mcp_servers']:
            markdown += '## MCP Server Listings\\n\\n'
            for link in categories['mcp_servers']:
                markdown += f'- {link}\\n'
            markdown += '\\n'
        
        if categories['external']:
            markdown += '## External Links\\n\\n'
            for link in categories['external']:
                markdown += f'- {link}\\n'
            markdown += '\\n'
        
        # Add found data
        if found_data:
            markdown += '## Extracted Data Objects\\n\\n'
            for i, item in enumerate(found_data[:20]):  # Limit to first 20
                markdown += f'{i+1}. {json.dumps(item, indent=2)}\\n\\n'
        
        # Add all links
        markdown += '## All Links (Raw)\\n\\n'
        for link in sorted(unique_links):
            markdown += f'- {link}\\n'
        
        # Save to file
        filename = '/home/xelova/mcp-listing/cursor_directory_mcp_regex_scrape.md'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f'Results saved to {filename}')
        print(f'Categories: Navigation={len(categories["navigation"])}, MCP Servers={len(categories["mcp_servers"])}, External={len(categories["external"])}')
        
        return unique_links, found_data
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return [], []

if __name__ == '__main__':
    extract_mcp_data()