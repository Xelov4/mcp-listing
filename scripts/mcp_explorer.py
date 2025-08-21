#!/usr/bin/env python3
"""
MCP Explorer - Extract detailed information about MCP servers
Creates individual MD files for each MCP with comprehensive information
"""

import os
import re
import json
import time
import requests
from urllib.parse import urlparse, urljoin
import hashlib
from datetime import datetime
from pathlib import Path

class MCPExplorer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.processed_urls = set()
        self.github_repos = {}  # For deduplication
        self.mcp_data = []
        self.output_dir = Path('/home/xelova/mcp-listing/mcp_final_list')
        self.output_dir.mkdir(exist_ok=True)
        
    def load_all_urls(self):
        """Load URLs from all source files"""
        all_urls = set()
        
        # 1. Cursor Directory URLs
        try:
            with open('/home/xelova/mcp-listing/all_mcp_urls.txt', 'r') as f:
                cursor_urls = [line.strip() for line in f if line.strip()]
            all_urls.update(cursor_urls)
            print(f"Loaded {len(cursor_urls)} URLs from Cursor Directory")
        except FileNotFoundError:
            print("Cursor Directory URLs file not found")
            
        # 2. PulseMCP URLs  
        try:
            with open('/home/xelova/mcp-listing/pulsemcp_server_urls.txt', 'r') as f:
                pulse_urls = [line.strip() for line in f if line.strip()]
            all_urls.update(pulse_urls)
            print(f"Loaded {len(pulse_urls)} URLs from PulseMCP")
        except FileNotFoundError:
            print("PulseMCP URLs file not found")
            
        # 3. GitHub URLs from Aixploria
        try:
            with open('/home/xelova/mcp-listing/aixploria-github-links.txt', 'r') as f:
                github_urls = [line.strip() for line in f if line.strip()]
            all_urls.update(github_urls)
            print(f"Loaded {len(github_urls)} GitHub URLs from Aixploria")
        except FileNotFoundError:
            print("Aixploria GitHub URLs file not found")
            
        # 4. Additional sources if available
        try:
            with open('/home/xelova/mcp-listing/FINAL_CLEAN_URLS_SORTED.txt', 'r') as f:
                final_urls = [line.strip() for line in f if line.strip()]
            all_urls.update(final_urls)
            print(f"Loaded {len(final_urls)} additional URLs")
        except FileNotFoundError:
            print("Final clean URLs file not found")
        
        print(f"Total unique URLs to process: {len(all_urls)}")
        return sorted(all_urls)
    
    def extract_github_info(self, github_url):
        """Extract information from GitHub repository"""
        try:
            # Parse GitHub URL to get owner/repo
            path = urlparse(github_url).path.strip('/')
            if '/' not in path:
                return None
                
            owner, repo = path.split('/')[:2]
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            
            response = self.session.get(api_url)
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data.get('name', repo),
                    'description': data.get('description', ''),
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'language': data.get('language', 'Unknown'),
                    'updated_at': data.get('updated_at', ''),
                    'topics': data.get('topics', []),
                    'homepage': data.get('homepage', ''),
                    'license': data.get('license', {}).get('name', '') if data.get('license') else '',
                    'clone_url': data.get('clone_url', ''),
                    'owner': data.get('owner', {}).get('login', owner)
                }
            else:
                print(f"GitHub API error for {github_url}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error extracting GitHub info for {github_url}: {e}")
            return None
    
    def extract_cursor_directory_info(self, url):
        """Extract information from Cursor Directory page"""
        try:
            response = self.session.get(url)
            if response.status_code != 200:
                return None
                
            content = response.text
            
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ''
            
            # Extract description from meta tags
            desc_patterns = [
                r'<meta name="description" content="(.*?)"',
                r'<meta property="og:description" content="(.*?)"',
                r'<meta name="twitter:description" content="(.*?)"'
            ]
            description = ''
            for pattern in desc_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    description = match.group(1).strip()
                    break
            
            # Look for GitHub links
            github_links = re.findall(r'https://github\.com/[^\s"\'<>]+', content)
            github_url = github_links[0] if github_links else ''
            
            # Extract category if available
            category_match = re.search(r'category["\']?\s*:\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            category = category_match.group(1) if category_match else ''
            
            # Extract tags if available
            tags = re.findall(r'tag["\']?\s*:\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            
            return {
                'title': title,
                'description': description,
                'github_url': github_url,
                'category': category,
                'tags': tags,
                'source_url': url
            }
            
        except Exception as e:
            print(f"Error extracting Cursor Directory info for {url}: {e}")
            return None
    
    def extract_pulsemcp_info(self, url):
        """Extract information from PulseMCP page"""
        try:
            response = self.session.get(url)
            if response.status_code != 200:
                return None
                
            content = response.text
            
            # Extract title
            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
            if not title_match:
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ''
            
            # Extract description
            desc_patterns = [
                r'<div[^>]*class[^>]*description[^>]*>(.*?)</div>',
                r'<p[^>]*class[^>]*description[^>]*>(.*?)</p>',
                r'<meta name="description" content="(.*?)"'
            ]
            description = ''
            for pattern in desc_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    description = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                    break
            
            # Look for GitHub links
            github_links = re.findall(r'https://github\.com/[^\s"\'<>]+', content)
            github_url = github_links[0] if github_links else ''
            
            # Extract version or install instructions
            install_match = re.search(r'(npm install|pip install|cargo install|git clone)([^\n<]+)', content, re.IGNORECASE)
            install_cmd = install_match.group(0).strip() if install_match else ''
            
            return {
                'title': title,
                'description': description,
                'github_url': github_url,
                'category': 'PulseMCP',
                'install_command': install_cmd,
                'source_url': url
            }
            
        except Exception as e:
            print(f"Error extracting PulseMCP info for {url}: {e}")
            return None
    
    def process_url(self, url):
        """Process a single URL and extract MCP information"""
        if url in self.processed_urls:
            return None
            
        self.processed_urls.add(url)
        
        # Determine source type and extract accordingly
        if 'cursor.directory' in url:
            info = self.extract_cursor_directory_info(url)
        elif 'pulsemcp.com' in url:
            info = self.extract_pulsemcp_info(url)
        elif 'github.com' in url:
            github_info = self.extract_github_info(url)
            if github_info:
                info = {
                    'title': github_info['name'],
                    'description': github_info['description'],
                    'github_url': url,
                    'category': 'GitHub Repository',
                    'source_url': url,
                    'github_data': github_info
                }
            else:
                info = None
        else:
            # Generic web scraping
            info = self.extract_generic_info(url)
        
        if info and info.get('github_url'):
            # Get GitHub details if available
            github_info = self.extract_github_info(info['github_url'])
            if github_info:
                info['github_data'] = github_info
                
            # Check for duplicates based on GitHub URL
            github_key = info['github_url'].lower().strip('/')
            if github_key in self.github_repos:
                print(f"Duplicate GitHub repo found: {github_key}")
                return None
            self.github_repos[github_key] = True
        
        return info
    
    def extract_generic_info(self, url):
        """Generic web scraping for other URLs"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
                
            content = response.text
            
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ''
            
            # Extract description
            desc_match = re.search(r'<meta name="description" content="(.*?)"', content, re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else ''
            
            # Look for GitHub links
            github_links = re.findall(r'https://github\.com/[^\s"\'<>]+', content)
            github_url = github_links[0] if github_links else ''
            
            return {
                'title': title,
                'description': description,
                'github_url': github_url,
                'category': 'Unknown',
                'source_url': url
            }
            
        except Exception as e:
            print(f"Error extracting generic info for {url}: {e}")
            return None
    
    def create_mcp_file(self, mcp_info):
        """Create individual MD file for MCP server"""
        if not mcp_info or not mcp_info.get('title'):
            return
            
        # Create safe filename
        safe_name = re.sub(r'[^\w\-_]', '_', mcp_info['title'].lower())
        safe_name = re.sub(r'_+', '_', safe_name).strip('_')
        filename = f"{safe_name}.md"
        
        filepath = self.output_dir / filename
        
        # Prepare content
        content = f"""# {mcp_info['title']}

## Basic Information
- **Name**: {mcp_info.get('title', 'N/A')}
- **Category**: {mcp_info.get('category', 'Unknown')}
- **Source URL**: {mcp_info.get('source_url', 'N/A')}

## Description
{mcp_info.get('description', 'No description available')}

## Links
"""
        
        if mcp_info.get('github_url'):
            content += f"- **GitHub**: {mcp_info['github_url']}\n"
            
        if mcp_info.get('github_data', {}).get('homepage'):
            content += f"- **Homepage**: {mcp_info['github_data']['homepage']}\n"
        
        # GitHub Details if available
        if 'github_data' in mcp_info:
            gh = mcp_info['github_data']
            content += f"""
## GitHub Repository Details
- **Owner**: {gh.get('owner', 'N/A')}
- **Language**: {gh.get('language', 'N/A')}
- **Stars**: {gh.get('stars', 0)}
- **Forks**: {gh.get('forks', 0)}
- **Last Updated**: {gh.get('updated_at', 'N/A')}
- **License**: {gh.get('license', 'N/A')}

## Topics/Tags
{', '.join(gh.get('topics', [])) if gh.get('topics') else 'None'}

"""
        
        # Installation if available
        if mcp_info.get('install_command'):
            content += f"""## Installation
```bash
{mcp_info['install_command']}
```

"""
        
        # Additional metadata
        content += f"""## Metadata
- **Extracted on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Source**: {urlparse(mcp_info.get('source_url', '')).netloc or 'Unknown'}

---
*This information was automatically extracted and may not be complete or up-to-date.*
"""
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created: {filename}")
        return filepath
    
    def create_summary_index(self):
        """Create summary index of all MCP servers"""
        index_content = f"""# MCP Servers Index

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
Total MCP Servers: {len(self.mcp_data)}

## Statistics
- **GitHub Repositories**: {len([m for m in self.mcp_data if m.get('github_url')])}
- **Categories**: {len(set(m.get('category', 'Unknown') for m in self.mcp_data))}

## Categories Breakdown
"""
        
        # Count by category
        categories = {}
        for mcp in self.mcp_data:
            cat = mcp.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            index_content += f"- **{cat}**: {count} servers\n"
        
        index_content += "\n## All MCP Servers\n\n"
        
        # List all MCPs
        for mcp in sorted(self.mcp_data, key=lambda x: x.get('title', '').lower()):
            safe_name = re.sub(r'[^\w\-_]', '_', mcp['title'].lower())
            safe_name = re.sub(r'_+', '_', safe_name).strip('_')
            filename = f"{safe_name}.md"
            
            github_badge = " 🐙" if mcp.get('github_url') else ""
            stars = ""
            if mcp.get('github_data', {}).get('stars', 0) > 0:
                stars = f" ⭐{mcp['github_data']['stars']}"
                
            index_content += f"- [{mcp['title']}]({filename}){github_badge}{stars} - {mcp.get('category', 'Unknown')}\n"
        
        # Write index file
        index_path = self.output_dir / "INDEX.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"Created index: {index_path}")
    
    def run(self):
        """Main execution function"""
        print("Starting MCP Explorer...")
        
        # Load all URLs
        urls = self.load_all_urls()
        
        # Process each URL with rate limiting
        failed_urls = []
        for i, url in enumerate(urls):
            print(f"Processing {i+1}/{len(urls)}: {url}")
            
            try:
                mcp_info = self.process_url(url)
                if mcp_info:
                    self.mcp_data.append(mcp_info)
                    self.create_mcp_file(mcp_info)
                else:
                    failed_urls.append(url)
                    
                # Rate limiting
                if i % 10 == 0:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error processing {url}: {e}")
                failed_urls.append(url)
                continue
        
        # Create summary index
        self.create_summary_index()
        
        # Save failed URLs for retry
        if failed_urls:
            failed_path = self.output_dir / "failed_urls.txt"
            with open(failed_path, 'w') as f:
                for url in failed_urls:
                    f.write(f"{url}\n")
            print(f"Saved {len(failed_urls)} failed URLs to {failed_path}")
        
        print(f"Completed! Processed {len(self.mcp_data)} MCP servers")
        print(f"Files created in: {self.output_dir}")

if __name__ == "__main__":
    explorer = MCPExplorer()
    explorer.run()