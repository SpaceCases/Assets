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


def aggregate_skinport_prices(prices: dict[str, list[int]]):
    # for debugging to avoid ratelimiting
    try:
        with open("skinport_prices.json") as f:
            skinport_item_data = json.load(f)
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

    for datum in skinport_item_data:
        market_hash_name: str = datum["market_hash_name"]
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
            if market_hash_name not in prices:
                continue
            prices[market_hash_name].append(price)


if __name__ == "__main__":
    with open(os.path.join(OUTPUT_DIRECTORY, "skin_data.json")) as f:
        skin_data = json.load(f)

    # aggregate all prices from different sources
    prices: dict[str, list[int]] = {
        datum["formatted_name"]: []
        for datum in skin_data.values()
    }
    aggregate_skinport_prices(prices)

    # get means of all aggregated prices
    for name, aggregated_prices in prices.items():
        unformatted_name = remove_skin_name_formatting(name)
        if len(aggregated_prices) == 0:
            price = 0
        else:
            mean_price = mean(aggregated_prices)
            price = int(mean_price)

        skin_data[unformatted_name]["price"] = price

    # write back to skin_data.json
    with open(os.path.join(OUTPUT_DIRECTORY, "skin_data.json"),
              "w",
              encoding="utf-8") as f:
        json.dump(skin_data, f, indent=4, ensure_ascii=False)
