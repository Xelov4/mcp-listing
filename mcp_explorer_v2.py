#!/usr/bin/env python3
"""
MCP Explorer V2 - Optimized version with better rate limiting and resume functionality
Creates individual MD files for each MCP with comprehensive information
"""

import os
import re
import json
import time
import requests
from urllib.parse import urlparse, urljoin
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Set, Dict, List, Optional
import logging

class MCPExplorerV2:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Configuration
        self.processed_urls = set()
        self.github_repos = {}
        self.mcp_data = []
        self.output_dir = Path('/home/xelova/mcp-listing/mcp_final_list')
        self.output_dir.mkdir(exist_ok=True)
        
        # Rate limiting and error handling
        self.github_rate_limit_reset = None
        self.github_requests_remaining = 0
        self.failed_github_urls = []
        self.successful_extractions = 0
        
        # Progress tracking
        self.progress_file = self.output_dir / "progress.json"
        self.load_progress()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / "extraction.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_progress(self):
        """Load previous progress to resume processing"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                    self.processed_urls = set(progress.get('processed_urls', []))
                    self.github_repos = progress.get('github_repos', {})
                    self.successful_extractions = progress.get('successful_extractions', 0)
                self.logger.info(f"Resumed: {len(self.processed_urls)} URLs already processed, {self.successful_extractions} successful extractions")
            except Exception as e:
                self.logger.warning(f"Could not load progress: {e}")
    
    def save_progress(self):
        """Save current progress"""
        progress = {
            'processed_urls': list(self.processed_urls),
            'github_repos': self.github_repos,
            'successful_extractions': self.successful_extractions,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def check_github_rate_limit(self):
        """Check GitHub API rate limit status"""
        try:
            response = self.session.get("https://api.github.com/rate_limit")
            if response.status_code == 200:
                data = response.json()
                core = data.get('resources', {}).get('core', {})
                self.github_requests_remaining = core.get('remaining', 0)
                reset_timestamp = core.get('reset', 0)
                self.github_rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
                
                self.logger.info(f"GitHub API: {self.github_requests_remaining} requests remaining, resets at {self.github_rate_limit_reset}")
                return self.github_requests_remaining > 10
            return False
        except Exception as e:
            self.logger.warning(f"Could not check GitHub rate limit: {e}")
            return False
    
    def wait_for_github_reset(self):
        """Wait for GitHub rate limit to reset"""
        if self.github_rate_limit_reset:
            wait_time = (self.github_rate_limit_reset - datetime.now()).total_seconds()
            if wait_time > 0:
                self.logger.info(f"Waiting {wait_time:.0f} seconds for GitHub rate limit reset...")
                time.sleep(min(wait_time + 60, 3600))  # Wait max 1 hour
    
    def load_all_urls(self):
        """Load URLs from all source files"""
        all_urls = set()
        sources = {
            'Cursor Directory': '/home/xelova/mcp-listing/all_mcp_urls.txt',
            'PulseMCP': '/home/xelova/mcp-listing/pulsemcp_server_urls.txt', 
            'Aixploria GitHub': '/home/xelova/mcp-listing/aixploria-github-links.txt',
            'Final Clean': '/home/xelova/mcp-listing/FINAL_CLEAN_URLS_SORTED.txt'
        }
        
        for source_name, file_path in sources.items():
            try:
                with open(file_path, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
                all_urls.update(urls)
                self.logger.info(f"Loaded {len(urls)} URLs from {source_name}")
            except FileNotFoundError:
                self.logger.warning(f"{source_name} file not found: {file_path}")
        
        # Remove already processed URLs
        remaining_urls = all_urls - self.processed_urls
        self.logger.info(f"Total unique URLs: {len(all_urls)}, Remaining: {len(remaining_urls)}")
        return sorted(remaining_urls)
    
    def extract_github_info(self, github_url):
        """Extract information from GitHub repository with rate limiting"""
        if not self.check_github_rate_limit():
            self.wait_for_github_reset()
            if not self.check_github_rate_limit():
                self.failed_github_urls.append(github_url)
                return None
        
        try:
            path = urlparse(github_url).path.strip('/')
            if '/' not in path:
                return None
                
            owner, repo = path.split('/')[:2]
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            
            response = self.session.get(api_url)
            if response.status_code == 200:
                data = response.json()
                self.github_requests_remaining -= 1
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
            elif response.status_code in [429, 403]:
                self.failed_github_urls.append(github_url)
                self.logger.warning(f"GitHub rate limited: {github_url}")
                return None
            else:
                self.logger.warning(f"GitHub API error for {github_url}: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error extracting GitHub info for {github_url}: {e}")
            return None
    
    def extract_cursor_directory_info(self, url):
        """Extract information from Cursor Directory page"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
                
            content = response.text
            
            # Extract title from various places
            title_patterns = [
                r'<h1[^>]*>([^<]+)</h1>',
                r'<title>([^<]+)</title>',
                r'"name"\s*:\s*"([^"]+)"',
            ]
            title = ''
            for pattern in title_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    # Clean cursor directory suffix
                    title = re.sub(r'\s*-\s*MCP Server\s*-\s*Cursor Directory.*$', '', title, re.IGNORECASE)
                    break
            
            # Extract description
            desc_patterns = [
                r'<meta name="description" content="([^"]+)"',
                r'<meta property="og:description" content="([^"]+)"',
                r'"description"\s*:\s*"([^"]+)"',
                r'<p[^>]*class[^>]*description[^>]*>([^<]+)</p>'
            ]
            description = ''
            for pattern in desc_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    description = match.group(1).strip()
                    break
            
            # Look for GitHub links
            github_patterns = [
                r'https://github\.com/[^\s"\'<>]+',
                r'"github"\s*:\s*"([^"]+)"',
                r'"repository"\s*:\s*"([^"]+)"'
            ]
            github_url = ''
            for pattern in github_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    github_url = matches[0]
                    break
            
            # Extract category
            category_patterns = [
                r'"category"\s*:\s*"([^"]+)"',
                r'Category:\s*([^\n<]+)',
            ]
            category = 'Cursor Directory'
            for pattern in category_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    category = match.group(1).strip()
                    break
            
            return {
                'title': title or url.split('/')[-1],
                'description': description,
                'github_url': github_url,
                'category': category,
                'source_url': url
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting Cursor Directory info for {url}: {e}")
            return None
    
    def extract_pulsemcp_info(self, url):
        """Extract information from PulseMCP page"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
                
            content = response.text
            
            # Extract title
            title_patterns = [
                r'<h1[^>]*>([^<]+)</h1>',
                r'<title>([^<]+)</title>'
            ]
            title = ''
            for pattern in title_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                    title = re.sub(r'\s*-\s*PulseMCP.*$', '', title, re.IGNORECASE)
                    break
            
            # Extract description
            desc_patterns = [
                r'<meta name="description" content="([^"]+)"',
                r'<div[^>]*class[^>]*description[^>]*>([^<]+)</div>',
                r'<p[^>]*>([^<]+)</p>'
            ]
            description = ''
            for pattern in desc_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    description = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                    if len(description) > 50:  # Only use substantial descriptions
                        break
            
            # Look for GitHub links
            github_links = re.findall(r'https://github\.com/[^\s"\'<>]+', content)
            github_url = github_links[0] if github_links else ''
            
            return {
                'title': title or url.split('/')[-1],
                'description': description,
                'github_url': github_url,
                'category': 'PulseMCP',
                'source_url': url
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting PulseMCP info for {url}: {e}")
            return None
    
    def process_url(self, url):
        """Process a single URL and extract MCP information"""
        if url in self.processed_urls:
            return None
            
        self.processed_urls.add(url)
        
        # Determine source type and extract accordingly
        try:
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
                    info = {
                        'title': url.split('/')[-1],
                        'description': 'GitHub repository (details unavailable due to rate limiting)',
                        'github_url': url,
                        'category': 'GitHub Repository',
                        'source_url': url
                    }
            else:
                info = self.extract_generic_info(url)
            
            if info and info.get('github_url'):
                # Get GitHub details if not already retrieved
                if 'github_data' not in info:
                    github_info = self.extract_github_info(info['github_url'])
                    if github_info:
                        info['github_data'] = github_info
                
                # Check for duplicates based on GitHub URL
                github_key = info['github_url'].lower().strip('/')
                if github_key in self.github_repos:
                    self.logger.info(f"Duplicate GitHub repo found: {github_key}")
                    return None
                self.github_repos[github_key] = True
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error processing {url}: {e}")
            return None
    
    def extract_generic_info(self, url):
        """Generic web scraping for other URLs"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
                
            content = response.text
            
            title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else url.split('/')[-1]
            
            desc_match = re.search(r'<meta name="description" content="([^"]+)"', content, re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else ''
            
            github_links = re.findall(r'https://github\.com/[^\s"\'<>]+', content)
            github_url = github_links[0] if github_links else ''
            
            return {
                'title': title,
                'description': description,
                'github_url': github_url,
                'category': 'Web Resource',
                'source_url': url
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting generic info for {url}: {e}")
            return None
    
    def create_mcp_file(self, mcp_info):
        """Create individual MD file for MCP server"""
        if not mcp_info or not mcp_info.get('title'):
            return None
            
        # Create safe filename
        safe_name = re.sub(r'[^\w\-_]', '_', mcp_info['title'].lower())
        safe_name = re.sub(r'_+', '_', safe_name).strip('_')
        
        # Add source suffix to avoid conflicts
        source_suffix = ''
        if 'cursor.directory' in mcp_info.get('source_url', ''):
            source_suffix = '_cursor'
        elif 'pulsemcp.com' in mcp_info.get('source_url', ''):
            source_suffix = '_pulsemcp'
        elif 'github.com' in mcp_info.get('source_url', ''):
            source_suffix = '_github'
            
        filename = f"{safe_name}{source_suffix}.md"
        filepath = self.output_dir / filename
        
        # Skip if file already exists
        if filepath.exists():
            return filepath
        
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
- **Stars**: ⭐ {gh.get('stars', 0)}
- **Forks**: 🍴 {gh.get('forks', 0)}
- **Last Updated**: {gh.get('updated_at', 'N/A')}
- **License**: {gh.get('license', 'N/A')}

## Topics/Tags
{', '.join(gh.get('topics', [])) if gh.get('topics') else 'None'}

"""
        
        # Additional metadata
        content += f"""## Metadata
- **Extracted on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Source**: {urlparse(mcp_info.get('source_url', '')).netloc or 'Unknown'}
- **Filename**: `{filename}`

---
*This information was automatically extracted and may not be complete or up-to-date.*
"""
        
        # Write file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Created: {filename}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error writing file {filename}: {e}")
            return None
    
    def create_summary_index(self):
        """Create summary index of all MCP servers"""
        # Load all existing files
        existing_files = list(self.output_dir.glob("*.md"))
        existing_files = [f for f in existing_files if f.name not in ['INDEX.md', 'README.md']]
        
        index_content = f"""# MCP Servers Complete Index

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
Total MCP Servers: {len(existing_files)}

## Statistics
- **Total Files**: {len(existing_files)} servers documented
- **Successful Extractions**: {self.successful_extractions}
- **GitHub API Requests Used**: {5000 - self.github_requests_remaining if hasattr(self, 'github_requests_remaining') else 'Unknown'}

## File Structure
Each MCP server has its own markdown file with detailed information including:
- Basic information (name, category, source)
- Description and links
- GitHub repository details (when available)
- Topics/tags and metadata

## All MCP Servers

"""
        
        # List all files alphabetically
        for filepath in sorted(existing_files):
            filename = filepath.name
            display_name = filename.replace('.md', '').replace('_', ' ').title()
            index_content += f"- [{display_name}]({filename})\n"
        
        index_content += f"""

## Processing Status
- **URLs Processed**: {len(self.processed_urls)}
- **Failed GitHub URLs**: {len(self.failed_github_urls)}

## Next Steps
To resume processing remaining URLs, run the script again. It will automatically continue from where it left off.

---
*Generated by MCP Explorer V2*
"""
        
        # Write index file
        index_path = self.output_dir / "INDEX.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        self.logger.info(f"Created index: {index_path}")
    
    def run(self, max_urls=None, batch_size=100):
        """Main execution function with batching"""
        self.logger.info("Starting MCP Explorer V2...")
        
        # Check initial GitHub rate limit
        self.check_github_rate_limit()
        
        # Load all URLs
        urls = self.load_all_urls()
        if max_urls:
            urls = urls[:max_urls]
        
        # Process URLs in batches
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i+batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}: URLs {i+1}-{min(i+batch_size, len(urls))} of {len(urls)}")
            
            for j, url in enumerate(batch):
                try:
                    self.logger.info(f"Processing {i+j+1}/{len(urls)}: {url}")
                    mcp_info = self.process_url(url)
                    
                    if mcp_info:
                        self.mcp_data.append(mcp_info)
                        self.create_mcp_file(mcp_info)
                        self.successful_extractions += 1
                    
                    # Rate limiting pause
                    if (i+j) % 20 == 0:
                        time.sleep(2)
                        
                except Exception as e:
                    self.logger.error(f"Error processing {url}: {e}")
                    continue
            
            # Save progress after each batch
            self.save_progress()
            self.logger.info(f"Batch complete. Total successful extractions: {self.successful_extractions}")
        
        # Create final summary
        self.create_summary_index()
        
        self.logger.info(f"Completed! Processed {len(self.processed_urls)} URLs")
        self.logger.info(f"Successful extractions: {self.successful_extractions}")
        self.logger.info(f"Failed GitHub URLs: {len(self.failed_github_urls)}")
        self.logger.info(f"Files created in: {self.output_dir}")

if __name__ == "__main__":
    explorer = MCPExplorerV2()
    # Process in smaller batches to handle rate limiting better
    explorer.run(max_urls=1000, batch_size=50)  # Process 1000 URLs in batches of 50