#!/usr/bin/env python3
"""
Script to download files from links.json based on tags using AND rule.
Usage: python get_models.py [OPTIONS] tag1 tag2 tag3 ...
"""

import json
import os
import sys
import requests
from urllib.parse import urlparse

# Global variables to track "all" behavior
skip_all = False
rewrite_all = False


def load_links():
    """Load links from links.json file."""
    try:
        with open('links.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: links.json file not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in links.json file.")
        sys.exit(1)


def download_file(url, filepath):
    """Download a file from URL to specified filepath."""
    global skip_all, rewrite_all
    
    try:
        # Check if file or symlink already exists
        if os.path.exists(filepath) or os.path.islink(filepath):
            # If skip_all or rewrite_all is set, use that decision
            if skip_all:
                print(f"Skipping (all): {filepath}")
                return False
            elif rewrite_all:
                print(f"Rewriting (all): {filepath}")
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                print(f"Downloading {url} to {filepath}")
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"Downloaded successfully: {filepath}")
                return True
            
            print(f"File already exists: {filepath}")
            print("Options:")
            print("1. Skip (s)")
            print("2. Rewrite (r)")
            print("3. Skip all (sa)")
            print("4. Rewrite all (ra)")
            
            while True:
                choice = input("Enter your choice (s/r/sa/ra): ").strip().lower()
                if choice in ['s', 'skip']:
                    print("Skipping file download.")
                    return False
                elif choice in ['r', 'rewrite']:
                    print("Rewriting existing file.")
                    break
                elif choice in ['sa', 'skip all']:
                    print("Skipping this file and all future existing files.")
                    skip_all = True
                    return False
                elif choice in ['ra', 'rewrite all']:
                    print("Rewriting this file and all future existing files.")
                    rewrite_all = True
                    break
                else:
                    print("Invalid choice. Please enter s, r, sa, or ra.")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        print(f"Downloading {url} to {filepath}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Downloaded successfully: {filepath}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False


def get_files_by_tags(links, tags):
    """Get all files that match ALL specified tags (AND logic)."""
    matching_files = []
    
    for item in links:
        # Check if item has all the required tags
        item_tags = set(item.get('tags', []))
        required_tags = set(tags)
        
        # AND logic: item must have ALL required tags
        if required_tags.issubset(item_tags):
            # Add all files from this item
            for file_info in item.get('files', []):
                matching_files.append({
                    'name': item['name'],
                    'filename': file_info['filename'],
                    'path': file_info['path'],
                    'url': file_info['url']
                })
    
    return matching_files


def get_all_tags(links):
    """Get all unique tags from the links data."""
    all_tags = set()
    for item in links:
        tags = item.get('tags', [])
        all_tags.update(tags)
    return sorted(list(all_tags))


def show_available_tags(links):
    """Display all available tags."""
    tags = get_all_tags(links)
    print("Available tags:")
    for tag in tags:
        print(f"  {tag}")


def main():
    global skip_all, rewrite_all
    
    # Initialize global variables
    skip_all = False
    rewrite_all = False
    
    # Check if --help or -h is provided
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python get_models.py [OPTIONS] tag1 tag2 tag3 ...")
        print("")
        print("Options:")
        print("  --help, -h     Show this help message")
        print("  --tags         Show all available tags")
        print("")
        print("Examples:")
        print("  python get_models.py cn sd15      # Download ControlNet files for SD1.5")
        print("  python get_models.py up all       # Download all upscaler files")
        print("  python get_models.py --tags       # Show all available tags")
        sys.exit(0)
    
    # Check if --tags is provided
    if '--tags' in sys.argv:
        links = load_links()
        show_available_tags(links)
        sys.exit(0)
    
    # Check if tags are provided
    if len(sys.argv) < 2:
        print("Usage: python get_models.py [OPTIONS] tag1 tag2 tag3 ...")
        print("Use --help for more information or --tags to see all available tags")
        sys.exit(1)
    
    # Get tags from command line arguments (excluding options)
    args = sys.argv[1:]
    if '--tags' in args:
        args.remove('--tags')
    
    if not args:
        print("No tags provided. Use --help for usage information or --tags to see available tags.")
        sys.exit(1)
    
    tags = args
    print(f"Searching for files with tags: {', '.join(tags)}")
    
    # Load links data
    links = load_links()
    
    # Find matching files using AND logic
    matching_files = get_files_by_tags(links, tags)
    
    if not matching_files:
        print("No files found matching all specified tags.")
        sys.exit(0)
    
    print(f"Found {len(matching_files)} file(s) matching all tags:")
    
    # Download each matching file
    success_count = 0
    for file_info in matching_files:
        # Construct local filepath
        filepath = os.path.join(file_info['path'], file_info['filename'])
        
        # Download the file
        if download_file(file_info['url'], filepath):
            success_count += 1
    
    print(f"\nDownloaded {success_count} out of {len(matching_files)} files successfully.")


if __name__ == "__main__":
    main()