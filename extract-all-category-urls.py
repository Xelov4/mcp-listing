#!/usr/bin/env python3

import os
import glob
import re
from datetime import datetime

def extract_all_category_urls():
    """Extract all URLs from cat_* directory files"""
    
    print("🔍 Extracting URLs from all cat_* directories...")
    
    # Find all cat_* URL files
    url_files = glob.glob('/home/xelova/mcp-listing/cat_*/*urls*.md')
    
    print(f"Found {len(url_files)} category files to process:")
    for file in url_files:
        category = file.split('/')[-2].replace('cat_', '')
        print(f"  • {category}")
    
    all_urls = []
    category_stats = {}
    
    # Process each category file
    for url_file in url_files:
        category = os.path.basename(os.path.dirname(url_file)).replace('cat_', '')
        
        print(f"\n📂 Processing {category}...")
        
        try:
            with open(url_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract URLs using multiple patterns
            url_patterns = [
                r'https?://[^\s\)\]]+',
                r'\[.*?\]\((https?://[^\)]+)\)',
                r'<(https?://[^>]+)>',
            ]
            
            file_urls = []
            for pattern in url_patterns:
                matches = re.findall(pattern, content)
                file_urls.extend(matches)
            
            # Clean and deduplicate URLs
            cleaned_urls = []
            for url in file_urls:
                # Clean URL (remove trailing punctuation)
                url = re.sub(r'[,;.\)\]]+$', '', url.strip())
                if url and url.startswith('http') and url not in cleaned_urls:
                    cleaned_urls.append(url)
            
            print(f"   Found {len(cleaned_urls)} URLs")
            all_urls.extend(cleaned_urls)
            category_stats[category] = len(cleaned_urls)
            
        except Exception as e:
            print(f"   ❌ Error reading {url_file}: {e}")
            category_stats[category] = 0
    
    # Remove duplicates from all URLs
    print(f"\n🧹 Deduplicating URLs...")
    unique_urls = list(dict.fromkeys(all_urls))  # Preserves order
    
    print(f"📊 Results:")
    print(f"   • Total URLs found: {len(all_urls)}")
    print(f"   • Unique URLs: {len(unique_urls)}")
    print(f"   • Duplicates removed: {len(all_urls) - len(unique_urls)}")
    
    return unique_urls, category_stats

def create_master_list():
    """Create comprehensive master MCP list combining all sources"""
    
    print("\n🚀 Creating comprehensive master MCP list...")
    
    # Extract URLs from categories
    category_urls, category_stats = extract_all_category_urls()
    
    # Read existing lists
    existing_lists = {}
    
    # Cursor Directory URLs
    try:
        with open('/home/xelova/mcp-listing/FINAL_CLEAN_URLS_SORTED.txt', 'r') as f:
            cursor_urls = [line.strip() for line in f if line.strip()]
        existing_lists['Cursor Directory'] = cursor_urls
        print(f"📁 Cursor Directory: {len(cursor_urls)} URLs")
    except FileNotFoundError:
        cursor_urls = []
        print("📁 Cursor Directory: File not found")
    
    # PulseMCP URLs
    try:
        with open('/home/xelova/mcp-listing/pulsemcp_server_urls.txt', 'r') as f:
            pulse_urls = [line.strip() for line in f if line.strip()]
        existing_lists['PulseMCP'] = pulse_urls
        print(f"📁 PulseMCP: {len(pulse_urls)} URLs")
    except FileNotFoundError:
        pulse_urls = []
        print("📁 PulseMCP: File not found")
    
    # Combine all URLs
    all_sources_urls = category_urls + cursor_urls + pulse_urls
    
    # Remove duplicates
    master_urls = list(dict.fromkeys(all_sources_urls))
    
    # Generate master list markdown
    markdown = f"""# Master MCP Collection - All Sources Combined

## Summary
- **Total URLs collected**: {len(all_sources_urls)}
- **Unique URLs**: {len(master_urls)}
- **Duplicates removed**: {len(all_sources_urls) - len(master_urls)}
- **Date compiled**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Sources Breakdown

### Category Collections ({len(category_urls)} URLs)
"""
    
    for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        markdown += f"- **{category.replace('_', ' ').title()}**: {count} URLs\n"
    
    markdown += f"""
### External Collections
- **Cursor Directory**: {len(cursor_urls)} URLs
- **PulseMCP**: {len(pulse_urls)} URLs

## Complete URL List

"""
    
    # Add all URLs numbered
    for i, url in enumerate(master_urls, 1):
        markdown += f"{i}. {url}\n"
    
    # Save master list
    with open('/home/xelova/mcp-listing/MASTER_MCP_COLLECTION.md', 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    # Save simple URL list
    with open('/home/xelova/mcp-listing/MASTER_MCP_URLS.txt', 'w') as f:
        for url in master_urls:
            f.write(url + '\n')
    
    print(f"\n✅ Master lists created:")
    print(f"   📄 MASTER_MCP_COLLECTION.md - Complete formatted list")
    print(f"   📄 MASTER_MCP_URLS.txt - Simple URL list")
    print(f"   📊 Total unique URLs: {len(master_urls)}")
    
    return master_urls, existing_lists, category_stats

if __name__ == '__main__':
    create_master_list()