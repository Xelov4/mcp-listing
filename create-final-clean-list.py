#!/usr/bin/env python3

def create_final_clean_list():
    """Create final clean and readable MCP list"""
    
    print("Creating final clean MCP list...")
    
    # Read the clean URLs
    with open('/home/xelova/mcp-listing/all_mcp_urls_clean.txt', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Processing {len(urls)} URLs...")
    
    # Create simple clean list
    clean_content = f"""# Cursor Directory - Complete MCP Collection

## Summary
- **Total MCPs**: {len(urls)}
- **Source**: cursor.directory via Supabase API
- **Duplicates removed**: Yes
- **Date extracted**: 2025-08-20

## All MCP URLs

"""
    
    # Add numbered list
    for i, url in enumerate(urls, 1):
        # Extract name from slug
        slug = url.split('/mcp/')[-1]
        name = slug.replace('-', ' ').title()
        clean_content += f"{i}. [{name}]({url})\n"
    
    # Save final clean version
    with open('/home/xelova/mcp-listing/FINAL_MCP_LIST_CLEAN.md', 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    # Also create simple URL-only list
    with open('/home/xelova/mcp-listing/FINAL_MCP_URLS_ONLY.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
    
    print(f"✅ Final clean files created:")
    print(f"   • FINAL_MCP_LIST_CLEAN.md - {len(urls)} MCPs with names")
    print(f"   • FINAL_MCP_URLS_ONLY.txt - {len(urls)} URLs only")
    
    return urls

if __name__ == '__main__':
    create_final_clean_list()