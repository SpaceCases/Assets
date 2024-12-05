# SpaceCases Assets

This repository contains static assets and scripts for generating assets and item data for SpaceCases.

## Overview

This scripts in this repository generate:
1. Images for item skins and stickers (`gen_item_images.py`).
2. Item skin and sticker metadata (`gen_item_metadata.py`)


## Setup

```bash
git clone https://github.com/SpaceCases/Assets    # Clone the repository
cd Assets                                         # Move into the repository directory
python -m venv env                                # Create virtual environment
source env/bin/activate                           # Activate virtual environment
python -m pip install -r requirements.txt         # Install dependencies
python src/gen_item_images.py                     # Generate images for items
python src/gen_item_metadata.py                   # Generate item metadata JSON files
```
Then use whatever scheduling system you like to periodically run the `refresh_prices.py` script to refresh the item prices in `skin_metadata.json` and `sticker_metadata.json`. The `assets` folder can then be served using any HTTP server.
