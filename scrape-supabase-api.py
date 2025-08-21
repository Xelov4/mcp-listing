#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def scrape_supabase_mcps():
    """Scrape MCPs directly from the Supabase API"""
    
    base_url = "https://knhgkaawjfqqwmsgmxns.supabase.co"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtuaGdrYWF3amZxcXdtc2dteG5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2NDAzMTksImV4cCI6MjA1NTIxNjMxOX0.1Uc-at_fT0Tf1MsNuewJf1VR0yiynPzrPvF0uWvTNnk"
    
    headers = {
        'apikey': api_key,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    all_mcps = []
    page = 1
    limit = 100  # Standard pagination limit
    
    print("Scraping MCPs from Supabase API...")
    
    while True:
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build the API URL with query parameters
        # Equivalent to: .from("mcps").select("*").eq("active",!0).order("company_id",{ascending:!0,nullsFirst:!1})
        params = {
            'select': '*',
            'active': 'eq.true',
            'order': 'company_id.asc.nullslast',
            'limit': limit,
            'offset': offset
        }
        
        url = f"{base_url}/rest/v1/mcps"
        
        try:
            print(f"Fetching page {page} (offset {offset})...")
            response = requests.get(url, headers=headers, params=params)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                break
                
            data = response.json()
            
            if not data or len(data) == 0:
                print("No more data found")
                break
                
            print(f"Found {len(data)} MCPs on page {page}")
            all_mcps.extend(data)
            
            # If we got less than limit, we've reached the end
            if len(data) < limit:
                break
                
            page += 1
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            break
    
    print(f"\\nTotal MCPs found: {len(all_mcps)}")
    
    if all_mcps:
        # Generate comprehensive markdown
        markdown = '# Cursor Directory - Complete MCP Database\\n\\n'
        markdown += f'Extracted from: Supabase API (https://knhgkaawjfqqwmsgmxns.supabase.co)\\n'
        markdown += f'Date: {datetime.now().isoformat()}\\n'
        markdown += f'Total MCPs found: {len(all_mcps)}\\n\\n'
        
        # Add summary statistics
        active_mcps = [mcp for mcp in all_mcps if mcp.get('active', False)]
        with_logos = [mcp for mcp in all_mcps if mcp.get('logo')]
        with_descriptions = [mcp for mcp in all_mcps if mcp.get('description')]
        
        markdown += '## Summary Statistics\\n\\n'
        markdown += f'- Total MCPs: {len(all_mcps)}\\n'
        markdown += f'- Active MCPs: {len(active_mcps)}\\n'
        markdown += f'- MCPs with logos: {len(with_logos)}\\n'
        markdown += f'- MCPs with descriptions: {len(with_descriptions)}\\n\\n'
        
        # Create comprehensive list
        markdown += '## Complete MCP Listings\\n\\n'
        
        for i, mcp in enumerate(all_mcps, 1):
            name = mcp.get('name', 'Unknown')
            slug = mcp.get('slug', '')
            description = mcp.get('description', '').strip()
            website = mcp.get('website', '')
            active = mcp.get('active', False)
            
            # Create cursor.directory URL
            cursor_url = f"https://www.cursor.directory/mcp/{slug}" if slug else ""
            
            markdown += f'### {i}. {name}\\n\\n'
            
            if cursor_url:
                markdown += f'**URL**: [{cursor_url}]({cursor_url})\\n\\n'
                
            if website:
                markdown += f'**Website**: [{website}]({website})\\n\\n'
                
            if description:
                # Limit description length and clean it
                desc = description[:500] + "..." if len(description) > 500 else description
                markdown += f'**Description**: {desc}\\n\\n'
                
            markdown += f'**Active**: {"✅ Yes" if active else "❌ No"}\\n\\n'
            
            if slug:
                markdown += f'**Slug**: `{slug}`\\n\\n'
                
            markdown += '---\\n\\n'
        
        # Add raw JSON data at the end for reference
        markdown += '## Raw Data (JSON)\\n\\n'
        markdown += f'```json\\n{json.dumps(all_mcps[:10], indent=2)}\\n```\\n\\n'
        markdown += f'*Note: Only showing first 10 entries in JSON format*\\n\\n'
        
        # Save to file
        filename = '/home/xelova/mcp-listing/cursor_directory_complete_mcp_database.md'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown)
            
        print(f"Complete database saved to: {filename}")
        
        # Also create a simple list of URLs
        url_list = []
        for mcp in all_mcps:
            slug = mcp.get('slug', '')
            if slug:
                url_list.append(f"https://www.cursor.directory/mcp/{slug}")
        
        url_filename = '/home/xelova/mcp-listing/all_mcp_urls.txt'
        with open(url_filename, 'w') as f:
            for url in url_list:
                f.write(url + '\n')
                
        print(f"URL list saved to: {url_filename}")
        print(f"Total URLs: {len(url_list)}")
        
    return all_mcps

if __name__ == '__main__':
    mcps = scrape_supabase_mcps()
    if mcps:
        print("\\n✅ SUCCESS: Complete MCP database extracted!")
        print(f"Found {len(mcps)} MCPs total")
    else:
        print("❌ FAILED: No MCPs found")