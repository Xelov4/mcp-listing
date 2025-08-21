#!/usr/bin/env python3
import os
from datetime import datetime

def combine_all_sources():
    """Combine all MCP sources including the new Aixploria results"""
    
    all_urls = set()
    sources = {}
    
    # Read existing sources
    
    # 1. Cursor Directory (1606 unique)
    try:
        with open('/home/xelova/mcp-listing/FINAL_CLEAN_URLS_SORTED.txt', 'r') as f:
            cursor_urls = set(line.strip() for line in f.readlines() if line.strip())
        all_urls.update(cursor_urls)
        sources['Cursor Directory'] = len(cursor_urls)
        print(f"Loaded {len(cursor_urls)} URLs from Cursor Directory")
    except FileNotFoundError:
        print("Cursor Directory file not found")
        cursor_urls = set()
        sources['Cursor Directory'] = 0
    
    # 2. PulseMCP (5671)
    try:
        with open('/home/xelova/mcp-listing/pulsemcp_server_urls.txt', 'r') as f:
            pulse_urls = set(line.strip() for line in f.readlines() if line.strip())
        all_urls.update(pulse_urls)
        sources['PulseMCP'] = len(pulse_urls)
        print(f"Loaded {len(pulse_urls)} URLs from PulseMCP")
    except FileNotFoundError:
        print("PulseMCP file not found")
        pulse_urls = set()
        sources['PulseMCP'] = 0
    
    # 3. Category Collections (8035)
    try:
        with open('/home/xelova/mcp-listing/all_mcp_urls_clean.txt', 'r') as f:
            content = f.read()
            # Handle escaped newlines
            if '\\n' in content and '\n' not in content:
                category_urls = set(url.strip() for url in content.split('\\n') if url.strip())
            else:
                category_urls = set(line.strip() for line in content.split('\n') if line.strip())
        all_urls.update(category_urls)
        sources['Category Collections'] = len(category_urls)
        print(f"Loaded {len(category_urls)} URLs from Category Collections")
    except FileNotFoundError:
        print("Category Collections file not found")
        category_urls = set()
        sources['Category Collections'] = 0
    
    # 4. NEW: Aixploria GitHub Links (705)
    try:
        with open('/home/xelova/mcp-listing/aixploria-github-links.txt', 'r') as f:
            aixploria_github_urls = set(line.strip() for line in f.readlines() if line.strip())
        all_urls.update(aixploria_github_urls)
        sources['Aixploria GitHub'] = len(aixploria_github_urls)
        print(f"Loaded {len(aixploria_github_urls)} URLs from Aixploria GitHub")
    except FileNotFoundError:
        print("Aixploria GitHub file not found")
        aixploria_github_urls = set()
        sources['Aixploria GitHub'] = 0
    
    # Count overlaps for statistics
    previous_total = len(cursor_urls | pulse_urls | category_urls)
    new_total = len(all_urls)
    new_unique_from_aixploria = new_total - previous_total
    
    print(f"\nStatistics:")
    print(f"Previous total: {previous_total}")
    print(f"New total: {new_total}")
    print(f"New unique URLs from Aixploria: {new_unique_from_aixploria}")
    print(f"Aixploria overlap: {len(aixploria_github_urls) - new_unique_from_aixploria}")
    
    return all_urls, sources, new_unique_from_aixploria

def create_updated_master_collection():
    """Create updated master collection with Aixploria data"""
    
    all_urls, sources, new_unique = combine_all_sources()
    
    # Create the updated master collection markdown
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    content = f"""# Master MCP Collection - All Sources Combined (Updated with Aixploria)

## Summary
- **Total URLs collected**: {len(all_urls)}
- **Unique URLs**: {len(all_urls)}
- **Date compiled**: {timestamp}
- **New URLs added from Aixploria**: {new_unique}

## Sources Breakdown

### 1. Cursor Directory Supabase API ({sources.get('Cursor Directory', 0)} URLs)
- Source: https://cursor.directory/mcp
- Method: Direct Supabase API extraction
- Total extracted: {sources.get('Cursor Directory', 0)} unique MCP servers

### 2. PulseMCP Sitemap ({sources.get('PulseMCP', 0)} URLs)  
- Source: https://www.pulsemcp.com/sitemap.xml
- Method: XML parsing for */servers/* URLs
- Total extracted: {sources.get('PulseMCP', 0)} server URLs

### 3. Category Collections ({sources.get('Category Collections', 0)} URLs)
- Source: 22 cat_* directory files in mcp-listing
- Method: Pattern matching across category files
- Total extracted: {sources.get('Category Collections', 0)} unique URLs

### 4. Aixploria GitHub Repositories ({sources.get('Aixploria GitHub', 0)} URLs) **NEW**
- Source: https://www.aixploria.com/en/list-best-mcp-servers-directory-ai/
- Method: JavaScript content extraction + GitHub link parsing
- Total extracted: {sources.get('Aixploria GitHub', 0)} GitHub repositories
- New unique URLs: {new_unique}

## Collection Statistics

| Source | Total URLs | % of Collection |
|--------|------------|-----------------|
| Category Collections | {sources.get('Category Collections', 0)} | {sources.get('Category Collections', 0)/len(all_urls)*100:.1f}% |
| PulseMCP | {sources.get('PulseMCP', 0)} | {sources.get('PulseMCP', 0)/len(all_urls)*100:.1f}% |
| Cursor Directory | {sources.get('Cursor Directory', 0)} | {sources.get('Cursor Directory', 0)/len(all_urls)*100:.1f}% |
| Aixploria GitHub | {sources.get('Aixploria GitHub', 0)} | {sources.get('Aixploria GitHub', 0)/len(all_urls)*100:.1f}% |

## Key Achievements

1. **Comprehensive Coverage**: Combined 4 major MCP sources for maximum coverage
2. **JavaScript Handling**: Successfully bypassed dynamic content loading limitations  
3. **API Discovery**: Found and utilized backend APIs for complete data extraction
4. **Deduplication**: Applied across all sources to ensure unique URL collection
5. **GitHub Integration**: Added extensive GitHub repository coverage from Aixploria

## Technical Methods Used

- **Supabase API**: Direct database querying for Cursor Directory
- **XML Parsing**: Sitemap processing for PulseMCP
- **Pattern Matching**: Regex-based URL extraction from category files
- **JavaScript Analysis**: Content extraction from dynamic web pages
- **Repository Parsing**: GitHub URL extraction and validation

## Next Steps

- Analyze repository activity and popularity metrics
- Categorize servers by functionality and use cases  
- Implement automated updates for dynamic sources
- Create search and filtering capabilities
- Develop quality scoring based on GitHub stars, activity, etc.

---

*Generated by MCP Collection Script*
*Last updated: {timestamp}*
"""

    # Write the updated master collection
    with open('/home/xelova/mcp-listing/MASTER_MCP_COLLECTION_UPDATED.md', 'w') as f:
        f.write(content)
    
    # Save all URLs to text file
    with open('/home/xelova/mcp-listing/MASTER_MCP_URLS_UPDATED.txt', 'w') as f:
        for url in sorted(all_urls):
            f.write(f"{url}\\n")
    
    print(f"\\nUpdated master collection saved:")
    print(f"- MASTER_MCP_COLLECTION_UPDATED.md ({len(all_urls)} total URLs)")
    print(f"- MASTER_MCP_URLS_UPDATED.txt")
    
    return len(all_urls)

def main():
    print("Creating updated master MCP collection with Aixploria data...")
    total_urls = create_updated_master_collection()
    print(f"\\nCompleted! Master collection now contains {total_urls} unique MCP URLs.")

if __name__ == "__main__":
    main()