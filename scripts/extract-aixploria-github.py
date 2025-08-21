#!/usr/bin/env python3
import re

def extract_github_links():
    """Extract and clean GitHub links from aixploria results"""
    
    github_urls = set()
    
    # Read the raw URLs file
    try:
        with open('/home/xelova/mcp-listing/aixploria_urls.txt', 'r') as f:
            lines = f.readlines()
            
        repo_count = 0
        for line in lines:
            line = line.strip()
            
            # Check if line matches GitHub repo pattern (owner/repo)
            if re.match(r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$', line):
                full_url = f"https://github.com/{line}"
                github_urls.add(full_url)
                repo_count += 1
            # Check for full GitHub URLs
            elif 'github.com/' in line:
                github_matches = re.findall(r'https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+', line)
                github_urls.update(github_matches)
        
        print(f"Processed {len(lines)} lines, found {repo_count} repo patterns")
    
    except FileNotFoundError:
        print("aixploria_urls.txt not found")
    
    # Also check the markdown file for any additional GitHub links
    try:
        with open('/home/xelova/mcp-listing/aixploria-mcp-servers.md', 'r') as f:
            content = f.read()
            
        # Look for GitHub repository patterns
        repo_patterns = [
            r'- ([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)(?:\s|$)',  # Lines starting with "- owner/repo"
            r'https://github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)',
        ]
        
        for pattern in repo_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if '/' in match and not match.startswith('http'):
                    # Convert "owner/repo" to full GitHub URL
                    full_url = f"https://github.com/{match}"
                    github_urls.add(full_url)
                elif match.startswith('https://github.com/'):
                    github_urls.add(match)
    
    except FileNotFoundError:
        print("aixploria-mcp-servers.md not found")
    
    print(f"Raw github_urls set size: {len(github_urls)}")
    if len(github_urls) > 0:
        print("Sample URLs:", list(github_urls)[:5])
    
    # Clean and validate URLs
    clean_urls = set()
    for url in github_urls:
        # Remove .git suffix and any trailing unwanted characters
        url = re.sub(r'\.git.*$', '', url)
        url = re.sub(r'[?#].*$', '', url)  # Remove query params and fragments
        
        # Ensure proper format
        if url.startswith('https://github.com/'):
            # Make sure it has at least owner/repo format
            path = url.replace('https://github.com/', '')
            if '/' in path and len(path.split('/')) >= 2:
                # Take only owner/repo part (ignore subpaths)
                parts = path.split('/')
                clean_path = f"{parts[0]}/{parts[1]}"
                clean_url = f"https://github.com/{clean_path}"
                clean_urls.add(clean_url)
    
    print(f"Clean urls set size: {len(clean_urls)}")
    return sorted(clean_urls)

def main():
    print("Extracting GitHub links from Aixploria results...")
    
    github_urls = extract_github_links()
    
    print(f"Found {len(github_urls)} unique GitHub repositories")
    
    # Save GitHub URLs
    with open('/home/xelova/mcp-listing/aixploria-github-links.txt', 'w') as f:
        for url in github_urls:
            f.write(f"{url}\n")
    
    # Create organized markdown
    with open('/home/xelova/mcp-listing/aixploria-github-repos.md', 'w') as f:
        f.write("# Aixploria GitHub Repositories\n\n")
        f.write(f"Total GitHub repositories found: {len(github_urls)}\n\n")
        
        for url in github_urls:
            # Extract owner/repo for cleaner display
            repo_path = url.replace('https://github.com/', '')
            f.write(f"- [{repo_path}]({url})\n")
    
    print(f"Results saved to aixploria-github-links.txt and aixploria-github-repos.md")
    
    return github_urls

if __name__ == "__main__":
    main()