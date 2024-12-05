import os
import json
import requests
import random
from spacecases_common import remove_skin_name_formatting
from constants import OUTPUT_DIRECTORY, VANILLA_KNIVES
from decimal import Decimal
from statistics import mean
from util import Condition

GAMMA_DOPPLER_PHASES = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Emerald"]

DOPPLER_PHASES = [
    "Phase 1",
    "Phase 2",
    "Phase 3",
    "Phase 4",
    "Ruby",
    "Sapphire",
    "Black Pearl",
]


def fetch_skinport_data():
    """Fetch data from Skinport API or local cache."""
    try:
        with open("skinport_prices.json") as f:
            return json.load(f)
    except FileNotFoundError:
        with open("user_agents.txt") as f:
            user_agents = [line.strip() for line in f.readlines()]
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Encoding": "br, gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
        response = requests.get(
            "https://api.skinport.com/v1/items",
            headers=headers,
        )
        response.raise_for_status()
        skinport_item_data = response.json()

        # Optionally save fetched data for later use
        with open("skinport_prices.json", "w") as f:
            json.dump(skinport_item_data, f)
        return skinport_item_data


def aggregate_skinport_prices(prices: dict[str, list[int]], skinport_item_data):
    """Aggregate prices from the Skinport data."""
    for datum in skinport_item_data:
        market_hash_name = datum["market_hash_name"]
        if market_hash_name not in prices:
            continue
        price = datum["suggested_price"]
        if price is None:
            continue
        price = int(Decimal(price) * 100)

        if market_hash_name in VANILLA_KNIVES:
            for condition in Condition:
                new_name = f"{market_hash_name} ({condition})"
                prices[new_name].append(price)
            continue

        if "Gamma Doppler" in market_hash_name:
            for phase in GAMMA_DOPPLER_PHASES:
                new_name = market_hash_name.replace("(", f"- {phase} (")
                if new_name not in prices:
                    continue
                prices[new_name].append(price)
        elif "Doppler" in market_hash_name:
            for phase in DOPPLER_PHASES:
                new_name = market_hash_name.replace("(", f"- {phase} (")
                if new_name not in prices:
                    continue
                prices[new_name].append(price)
        else:
            prices[market_hash_name].append(price)


def aggregate_prices_for(file: str, skinport_item_data):
    """Process a single file and aggregate prices."""
    with open(os.path.join(OUTPUT_DIRECTORY, file)) as f:
        metadata = json.load(f)

    # Initialize the price aggregation dictionary
    prices: dict[str, list[int]] = {
        datum["formatted_name"]: [] for datum in metadata.values()
    }

    # Aggregate prices using Skinport data
    aggregate_skinport_prices(prices, skinport_item_data)

    # Calculate and assign mean prices to metadata
    for name, aggregated_prices in prices.items():
        unformatted_name = remove_skin_name_formatting(name)
        if len(aggregated_prices) == 0:
            price = 0
        else:
            mean_price = mean(aggregated_prices)
            price = int(mean_price)

        metadata[unformatted_name]["price"] = price

    # Write updated metadata back to file
    with open(os.path.join(OUTPUT_DIRECTORY, file), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # Fetch Skinport data once
    skinport_data = fetch_skinport_data()

    # Process files using the shared Skinport data
    aggregate_prices_for("skin_metadata.json", skinport_data)
    aggregate_prices_for("sticker_metadata.json", skinport_data)
