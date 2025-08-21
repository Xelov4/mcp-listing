#!/usr/bin/env python3
import requests
import re
import json
from urllib.parse import urljoin, urlparse
import time

def scrape_aixploria_page():
    """Scrape aixploria page for MCP servers and GitHub links"""
    
    url = "https://www.aixploria.com/en/list-best-mcp-servers-directory-ai/"
    
    # Get the initial page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        
        print(f"Got HTML content, length: {len(html_content)}")
        
        # Look for JavaScript files, API endpoints, or data
        js_files = re.findall(r'<script[^>]*src=["\']([^"\']+)["\'][^>]*>', html_content)
        print(f"Found {len(js_files)} JavaScript files")
        
        # Look for inline JavaScript that might contain data or API calls
        inline_js = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        print(f"Found {len(inline_js)} inline JavaScript blocks")
        
        # Extract all URLs that might be MCP servers
        all_urls = set()
        
        # Look for GitHub URLs
        github_urls = re.findall(r'https://github\.com/[^\s"\'<>]+', html_content)
        all_urls.update(github_urls)
        
        # Look for other potential MCP server URLs
        http_urls = re.findall(r'https?://[^\s"\'<>]+', html_content)
        all_urls.update(http_urls)
        
        print(f"Found {len(all_urls)} URLs in HTML content")
        
        # Try to find API endpoints or data sources
        api_patterns = [
            r'api["\']?\s*:\s*["\']([^"\']+)',
            r'endpoint["\']?\s*:\s*["\']([^"\']+)',
            r'fetch\(["\']([^"\']+)',
            r'axios\.get\(["\']([^"\']+)',
            r'\.get\(["\']([^"\']+)',
        ]
        
        api_urls = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            api_urls.update(matches)
        
        print(f"Found {len(api_urls)} potential API URLs")
        
        # Check for Next.js or React data
        nextjs_data = re.findall(r'__NEXT_DATA__["\']?\s*=\s*({.*?});', html_content, re.DOTALL)
        if nextjs_data:
            print(f"Found Next.js data: {len(nextjs_data)} blocks")
            try:
                data = json.loads(nextjs_data[0])
                print("Successfully parsed Next.js data")
                return extract_from_nextjs_data(data)
            except json.JSONDecodeError:
                print("Failed to parse Next.js data")
        
        # Look for window.__INITIAL_STATE__ or similar
        initial_state = re.findall(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html_content, re.DOTALL)
        if initial_state:
            print("Found initial state data")
            try:
                data = json.loads(initial_state[0])
                return extract_from_initial_state(data)
            except json.JSONDecodeError:
                print("Failed to parse initial state")
        
        # Try to fetch JavaScript files that might contain data
        for js_file in js_files[:5]:  # Limit to first 5 files
            if js_file.startswith('//'):
                js_url = 'https:' + js_file
            elif js_file.startswith('/'):
                js_url = 'https://www.aixploria.com' + js_file
            elif js_file.startswith('http'):
                js_url = js_file
            else:
                js_url = urljoin(url, js_file)
            
            try:
                js_response = requests.get(js_url, headers=headers)
                if js_response.status_code == 200:
                    js_content = js_response.text
                    
                    # Look for MCP server data in JS
                    mcp_matches = re.findall(r'["\']([^"\']*mcp[^"\']*)["\']', js_content, re.IGNORECASE)
                    github_matches = re.findall(r'https://github\.com/[^\s"\'<>]+', js_content)
                    
                    all_urls.update(mcp_matches)
                    all_urls.update(github_matches)
                    
                    print(f"Extracted {len(mcp_matches)} MCP references and {len(github_matches)} GitHub URLs from {js_url}")
                    
            except Exception as e:
                print(f"Failed to fetch {js_url}: {e}")
        
        return list(all_urls)
        
    except Exception as e:
        print(f"Error scraping page: {e}")
        return []

def extract_from_nextjs_data(data):
    """Extract MCP servers from Next.js data"""
    urls = set()
    
    def recursive_extract(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and ('github.com' in value or 'mcp' in value.lower()):
                    urls.add(value)
                elif isinstance(value, (dict, list)):
                    recursive_extract(value)
        elif isinstance(obj, list):
            for item in obj:
                recursive_extract(item)
    
    recursive_extract(data)
    return list(urls)

def extract_from_initial_state(data):
    """Extract MCP servers from initial state data"""
    return extract_from_nextjs_data(data)  # Same logic

def filter_mcp_urls(urls):
    """Filter URLs to find likely MCP servers"""
    mcp_urls = []
    github_urls = []
    
    for url in urls:
        if not url:
            continue
            
        url = url.strip()
        
        if 'github.com' in url:
            github_urls.append(url)
        elif any(keyword in url.lower() for keyword in ['mcp', 'model-context-protocol', 'context-protocol']):
            mcp_urls.append(url)
    
    return mcp_urls, github_urls

def main():
    print("Scraping Aixploria MCP servers...")
    
    urls = scrape_aixploria_page()
    
    if not urls:
        print("No URLs found. The page might require more advanced JavaScript handling.")
        return
    
    mcp_urls, github_urls = filter_mcp_urls(urls)
    
    print(f"\nResults:")
    print(f"Total URLs found: {len(urls)}")
    print(f"MCP-related URLs: {len(mcp_urls)}")
    print(f"GitHub URLs: {len(github_urls)}")
    
    # Save results
    with open('/home/xelova/mcp-listing/aixploria-mcp-servers.md', 'w') as f:
        f.write("# Aixploria MCP Servers\n\n")
        f.write(f"Scraped from: https://www.aixploria.com/en/list-best-mcp-servers-directory-ai/\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if mcp_urls:
            f.write("## MCP Server URLs\n\n")
            for url in sorted(set(mcp_urls)):
                f.write(f"- {url}\n")
        
        if github_urls:
            f.write("\n## GitHub URLs\n\n")
            for url in sorted(set(github_urls)):
                f.write(f"- {url}\n")
        
        if not mcp_urls and not github_urls:
            f.write("## All URLs Found\n\n")
            for url in sorted(set(urls)):
                f.write(f"- {url}\n")
    
    # Save raw URLs for processing
    with open('/home/xelova/mcp-listing/aixploria_urls.txt', 'w') as f:
        for url in sorted(set(urls)):
            f.write(f"{url}\n")
    
    print(f"\nResults saved to aixploria-mcp-servers.md and aixploria_urls.txt")

if __name__ == "__main__":
    main()