#!/usr/bin/env python3

import re
from collections import defaultdict
import json

def clean_mcp_list():
    """Clean and organize the MCP URLs list"""
    
    print("Cleaning MCP URLs list...")
    
    # Read the URLs
    with open('/home/xelova/mcp-listing/all_mcp_urls.txt', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(urls)} total URLs")
    
    # Remove duplicates while preserving order
    unique_urls = []
    seen = set()
    
    for url in urls:
        if url not in seen:
            unique_urls.append(url)
            seen.add(url)
    
    print(f"After removing duplicates: {len(unique_urls)} URLs")
    
    # Extract slug names and organize
    mcp_data = []
    
    for url in unique_urls:
        # Extract slug from URL
        match = re.match(r'https://www\.cursor\.directory/mcp/(.+)', url)
        if match:
            slug = match.group(1)
            
            # Clean up the name (remove numbers, hyphens, make readable)
            display_name = slug.replace('-', ' ').title()
            
            # Remove trailing numbers for versions
            display_name = re.sub(r'\s+\d+$', '', display_name)
            
            mcp_data.append({
                'name': display_name,
                'slug': slug,
                'url': url
            })
    
    # Sort by name
    mcp_data.sort(key=lambda x: x['name'].lower())
    
    # Create categorized lists
    categories = defaultdict(list)
    
    for mcp in mcp_data:
        name_lower = mcp['name'].lower()
        
        # Categorize based on keywords
        if any(word in name_lower for word in ['google', 'facebook', 'instagram', 'linkedin', 'twitter', 'youtube', 'reddit', 'slack', 'discord', 'telegram']):
            categories['Social & Communication'].append(mcp)
        elif any(word in name_lower for word in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'vercel', 'heroku', 'netlify', 'cloudflare']):
            categories['Cloud & Infrastructure'].append(mcp)
        elif any(word in name_lower for word in ['database', 'mysql', 'postgresql', 'mongodb', 'supabase', 'firebase', 'sql', 'redis', 'elastic']):
            categories['Databases'].append(mcp)
        elif any(word in name_lower for word in ['browser', 'puppeteer', 'playwright', 'selenium', 'scraping', 'crawl']):
            categories['Browser Automation & Scraping'].append(mcp)
        elif any(word in name_lower for word in ['payment', 'stripe', 'paypal', 'razorpay', 'commerce', 'shop']):
            categories['E-commerce & Payments'].append(mcp)
        elif any(word in name_lower for word in ['ai', 'openai', 'anthropic', 'machine learning', 'ml', 'neural']):
            categories['AI & Machine Learning'].append(mcp)
        elif any(word in name_lower for word in ['analytics', 'tracking', 'metrics', 'monitoring', 'observability']):
            categories['Analytics & Monitoring'].append(mcp)
        elif any(word in name_lower for word in ['api', 'webhook', 'rest', 'graphql', 'sdk']):
            categories['APIs & SDKs'].append(mcp)
        elif any(word in name_lower for word in ['productivity', 'task', 'todo', 'calendar', 'notes', 'notion', 'obsidian']):
            categories['Productivity Tools'].append(mcp)
        elif any(word in name_lower for word in ['design', 'figma', 'sketch', 'ui', 'ux', 'mockup']):
            categories['Design Tools'].append(mcp)
        else:
            categories['Other Tools'].append(mcp)
    
    # Generate clean markdown
    markdown = '# Cursor Directory - Clean MCP List\\n\\n'
    markdown += f'**Total MCPs**: {len(unique_urls)}\\n\\n'
    markdown += f'**Categories**: {len(categories)}\\n\\n'
    
    # Add table of contents
    markdown += '## Categories\\n\\n'
    for category in sorted(categories.keys()):
        count = len(categories[category])
        markdown += f'- [{category}](#{category.lower().replace(" & ", "-").replace(" ", "-")}) ({count} MCPs)\\n'
    
    markdown += '\\n---\\n\\n'
    
    # Add categorized listings
    for category in sorted(categories.keys()):
        mcps = categories[category]
        markdown += f'## {category}\\n\\n'
        
        for mcp in mcps:
            markdown += f'- **[{mcp["name"]}]({mcp["url"]})** - `{mcp["slug"]}`\\n'
        
        markdown += '\\n'
    
    # Save cleaned markdown
    with open('/home/xelova/mcp-listing/cursor_directory_clean_organized.md', 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    # Save cleaned URL list (no duplicates)
    with open('/home/xelova/mcp-listing/all_mcp_urls_clean.txt', 'w') as f:
        for url in unique_urls:
            f.write(url + '\\n')
    
    # Save as JSON for easy processing
    with open('/home/xelova/mcp-listing/mcp_data_clean.json', 'w') as f:
        json.dump(mcp_data, f, indent=2)
    
    # Generate statistics
    stats = {
        'total_mcps': len(unique_urls),
        'duplicates_removed': len(urls) - len(unique_urls),
        'categories': {cat: len(mcps) for cat, mcps in categories.items()},
        'top_categories': sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    }
    
    print("\\n📊 CLEANING RESULTS:")
    print(f"✅ Total unique MCPs: {stats['total_mcps']}")
    print(f"🗑️  Duplicates removed: {stats['duplicates_removed']}")
    print(f"📁 Categories created: {len(stats['categories'])}")
    
    print("\\n🏆 TOP CATEGORIES:")
    for category, mcps in stats['top_categories']:
        print(f"   • {category}: {len(mcps)} MCPs")
    
    print("\\n📄 FILES CREATED:")
    print("   • cursor_directory_clean_organized.md - Organized by categories")
    print("   • all_mcp_urls_clean.txt - Clean URL list (no duplicates)")  
    print("   • mcp_data_clean.json - Structured data")
    
    return stats

if __name__ == '__main__':
    clean_mcp_list()