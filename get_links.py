#!/usr/bin/env python3
"""
Script to load and parse model data directly from the web page https://docs.interstice.cloud/models/
"""

import re
import json
import requests
from urllib.parse import urljoin, urlparse

url = "https://docs.interstice.cloud/models/"


def fetch_html_content(url):
    """Fetch HTML content from the given URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {str(e)}")
        return None


def extract_links_data(html_content):
    """Extract model data from HTML content."""
    # Find all table rows (excluding header)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html_content, re.DOTALL)

    data = []

    # Process each row
    for row in rows:
        # Skip header row and rows with display: none
        if 'display: none' in row or '<thead>' in row or '<th>' in row:
            continue

        # Extract name (first cell)
        name_match = re.search(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if not name_match:
            continue

        name = re.sub(r'<[^>]+>', '', name_match.group(1)).strip()

        # Extract files section (second cell)
        cells = re.findall(r'<td[^>]*>.*?</td>', row, re.DOTALL)
        if len(cells) < 2:
            continue

        files_section = cells[1]

        # Extract all file entries from the files section
        files = []
        file_entries = re.findall(r'<p>(.*?)</p>', files_section, re.DOTALL)

        for entry in file_entries:
            # Extract filename and URL
            link_match = re.search(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', entry, re.DOTALL)
            if link_match:
                url = link_match.group(1).strip()
                filename = link_match.group(2).strip()

                # Extract directory path by parsing the span elements properly
                dir_path = ""
                # Find all span elements that contain text (not just separators)
                spans = re.findall(r'<span[^>]*>(.*?)</span>', entry, re.DOTALL)
                for i, span in enumerate(spans):
                    if span.strip() == '/':
                        dir_path += "/"
                    elif span.strip() and not span.strip().startswith('models/'):
                        # This is a path component
                        dir_path += span.strip()
                    elif span.strip() == 'models':
                        dir_path += span.strip()

                # Clean up the directory path
                if dir_path.startswith('/'):
                    dir_path = dir_path[1:]

                # Remove any remaining HTML tags from the path
                dir_path = re.sub(r'<[^>]+>', '', dir_path)
                dir_path = re.sub(r'/+', '/', dir_path)  # Replace multiple slashes with single slash
                dir_path = dir_path.rstrip('/')  # Remove trailing slash

                files.append({
                    'filename': filename,
                    'path': dir_path,
                    'url': url
                })

        # Extract tags (third cell)
        tags = []
        if len(cells) > 2:
            try:
                tags_section = cells[2]

                # Extract badge classes and text
                badge_matches = re.findall(r'<span[^>]*class=["\'][^"\']*sl-badge[^"\']*["\'][^>]*>(.*?)</span>',
                                           tags_section, re.DOTALL)
                for badge in badge_matches:
                    tag_text = re.sub(r'<[^>]+>', '', badge).strip()
                    if tag_text:
                        # Split tags that contain | separator (like sd15|sdxl)
                        if '|' in tag_text:
                            sub_tags = tag_text.split('|')
                            tags.extend([t.strip() for t in sub_tags if t.strip()])
                        else:
                            tags.append(tag_text)
            except:
                pass

        # Create entry
        entry = {
            'name': name,
            'files': files,
            'tags': tags
        }

        data.append(entry)

    return data


def save_to_json(data, filename):
    """Save data to JSON file."""
    try:
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=2)
        print(f"Successfully saved {len(data)} entries to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {str(e)}")
        return False


def main():
    """Main function to load and parse data from web page."""

    print(f"Fetching data from: {url}")

    # Fetch HTML content
    html_content = fetch_html_content(url)
    if not html_content:
        print("Failed to fetch HTML content")
        return

    # Extract data
    print("Parsing data...")
    data = extract_links_data(html_content)

    if not data:
        print("No data found in the HTML content")
        return

    # Save to JSON file
    print(f"Saving {len(data)} entries to links.json...")
    if save_to_json(data, 'links.json'):
        print("Data successfully loaded and saved!")
    else:
        print("Failed to save data")


if __name__ == "__main__":
    main()
