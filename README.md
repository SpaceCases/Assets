# SpaceCases Assets

This repository contains scripts and static assets used for generating and serving item skins and related data for SpaceCases.

## Overview

This scripts in this repository generate:
1. Images for item skins (`gen_skin_images.py`).
2. Item skin data (`gen_skin_data.py`)


## Setup

```bash
git clone https://github.com/SpaceCases/Assets    # Clone the repository
cd Assets                                         # Move into the repository directory
python -m venv env                                # Create virtual environment
source env/bin/activate                           # Activate virtual environment
python -m pip install -r requirements.txt         # Install dependencies
python src/gen_skin_images.py                     # Generate images for items
python src/gen_skin_data.py                       # Generate item data JSON file
```
Then use whatever scheduling system you like to periodically run the `refresh_prices.py` script to refresh the item prices in `skin_data.json`. The `assets` folder can then be served using any HTTP server.
