# Krita AI Model Downloader for ComfyUI

A lightweight Python utility for downloading AI model files for remote ComfyUI setups.

## Overview

This script is designed for users who run the Krita AI plugin and ComfyUI on different machines.
For example, in my case, ComfyUI runs on a remote server rather than on my local workstation.
The script provides a quick and convenient way to download all required models for your workflow.

## Files

- `get_models.py` — Main script for downloading model files using tag-based filtering
- `get_links.py` — Fetches and parses model data directly from the source webpage
- `links.json` — Structured model information including file paths, URLs, and tags

## Usage

### Load Model Data from the Web

```bash
python3 get_links.py
```

This retrieves data from
https://docs.interstice.cloud/models/
and saves it into links.json.

### Download Files by Tags

Run the script get_models.py **inside the ComfyUI subdirectory**, and specify one or more tags (AND logic):

```bash
python3 get_models.py [OPTIONS] tag1 tag2 tag3 ...
```

### Options

- `--help` or `-h` - Show help information
- `--tags` - Show all available tags
- `tag1 tag2 ...` - Download files matching ALL specified tags

### File Conflict Handling

If a file already exists, you can choose how to proceed:

- s — Skip this file
- r — Overwrite the existing file
- sa — Skip all existing files
- ra — Overwrite all existing files

### Examples

```bash
# Download ControlNet models for Stable Diffusion 1.5
python3 get_models.py cn sd15

# Download all upscaler models
python3 get_models.py up all

# Show all available tags
python3 get_models.py --tags

# Show help information
python3 get_models.py --help
```

## Requirements

- Python 3.x
- `requests` library (install with `pip install requests`)

## Directory Structure

get_models.py automatically creates folders using the path definitions inside links.json, such as:

- `models/controlnet/` - ControlNet models
- `models/upscale_models/` - Upscaler models
- `models/ipadapter/` - IP-Adapter models

## License

This project is created for educational and personal use and is distributed under the MIT License.
