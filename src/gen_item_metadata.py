"""
Aggregate all CS2 skin data into a json file, including price field but set to zero.
"""

import os
import re
import sys
import json
import requests
import argparse
from typing import NamedTuple
from dataclasses import asdict
from constants import OUTPUT_DIRECTORY, DEFAULT_ASSET_DOMAIN
from spacecases_common import (
    remove_skin_name_formatting,
    SkinMetadatum,
    StickerMetadatum,
    Rarity,
)
from constants import VANILLA_KNIVES
from util import Condition


class Result(NamedTuple):
    skin_metadata: dict[str, SkinMetadatum]
    sticker_metadata: dict[str, StickerMetadatum]


def create_image_url(name: str, asset_domain: str) -> str:
    return os.path.join(
        asset_domain,
        "generated",
        "images",
        "unformatted",
        f"{name}.png",
    )


def process_skin_json(metadata: dict[str, SkinMetadatum], datum, asset_domain: str):
    if datum["name"] in VANILLA_KNIVES:
        process_vanilla_knife(metadata, datum, asset_domain)
    else:
        process_non_vanilla_knife(metadata, datum, asset_domain)


def process_vanilla_knife(metadata: dict[str, SkinMetadatum], datum, asset_domain: str):
    formatted_name_no_wear = datum["name"]
    for condition in Condition:
        formatted_name = f"{formatted_name_no_wear} ({condition})"
        unformatted_name = remove_skin_name_formatting(formatted_name)
        rarity = Rarity.Ancient
        min_float = 0.0
        max_float = 1.0
        description = None
        image_url = create_image_url(unformatted_name, asset_domain)
        metadata[unformatted_name] = SkinMetadatum(
            formatted_name, rarity, 0, image_url, description, min_float, max_float
        )


def process_non_vanilla_knife(
    metadata: dict[str, SkinMetadatum], datum, asset_domain: str
):
    # name
    formatted_name = datum["name"]
    if "Doppler" in formatted_name:
        phase = datum["phase"]
        split = formatted_name.split("(")
        name_no_wear = split[0].strip()
        condition = f"({split[1].strip()}"
        formatted_name = f"{name_no_wear} - {phase} {condition}"
    unformatted_name = remove_skin_name_formatting(formatted_name)
    # rarity
    rarity = {
        "rarity_common_weapon": Rarity.Common,
        "rarity_uncommon_weapon": Rarity.Uncommon,
        "rarity_rare_weapon": Rarity.Rare,
        "rarity_mythical_weapon": Rarity.Mythical,
        "rarity_legendary_weapon": Rarity.Legendary,
        "rarity_ancient_weapon": Rarity.Ancient,
        "rarity_ancient": Rarity.Ancient,
        "rarity_contraband_weapon": Rarity.Contraband,
    }[datum["rarity"]["id"]]
    # float range
    min_float = datum.get("min_float", 0.0)
    max_float = datum.get("max_float", 1.0)
    # description
    description_match = re.search(r"<i>(.*?)</i>", datum["description"])
    if description_match:
        description = description_match.group(1)
    else:
        description = None
    # image url
    image_url = create_image_url(unformatted_name, asset_domain)
    # insert
    skin_datum = SkinMetadatum(
        formatted_name,
        rarity,
        0,
        image_url,
        description,
        min_float,
        max_float,
    )
    metadata[unformatted_name] = skin_datum


def process_sticker_json(
    metadata: dict[str, StickerMetadatum], datum, asset_domain: str
):
    formatted_name = datum["name"]
    unformatted_name = remove_skin_name_formatting(formatted_name)
    rarity = {
        "rarity_default": Rarity.Common,
        "rarity_rare": Rarity.Rare,
        "rarity_mythical": Rarity.Mythical,
        "rarity_legendary": Rarity.Legendary,
        "rarity_ancient": Rarity.Ancient,
        "rarity_contraband": Rarity.Contraband,
    }[datum["rarity"]["id"]]
    image_url = create_image_url(unformatted_name, asset_domain)
    metadata[unformatted_name] = StickerMetadatum(
        formatted_name, rarity, 0, image_url
    )


def run(api_data, asset_domain: str) -> Result:
    skin_metadata: dict[str, SkinMetadatum] = {}
    sticker_metadata: dict[str, StickerMetadatum] = {}
    for name, datum in api_data.items():
        if "skin" in name:
            process_skin_json(skin_metadata, datum, asset_domain)
        elif "sticker" in name:
            process_sticker_json(sticker_metadata, datum, asset_domain)
    return Result(skin_metadata, sticker_metadata)


if __name__ == "__main__":
    # argument parsing
    parser = argparse.ArgumentParser(
        prog="get_item_data",
        description=sys.modules[__name__].__doc__,
        epilog="Report bugs to https://github.com/SpaceCases/Assets/issues",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d", "--domain", default=DEFAULT_ASSET_DOMAIN, help="asset domain URL"
    )
    args = parser.parse_args()
    # folder structure
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    # get api data
    api_data = requests.get("https://bymykel.github.io/CSGO-API/api/en/all.json").json()
    # run
    skin_metadata, sticker_metadata = run(api_data, args.domain)
    # output
    with open(f"{OUTPUT_DIRECTORY}/skin_metadata.json", "w+", encoding="utf-8") as f:
        json.dump(
            {key: asdict(value) for key, value in skin_metadata.items()},
            f,
            ensure_ascii=False,
            indent=4,
        )
    with open(f"{OUTPUT_DIRECTORY}/sticker_metadata.json", "w+", encoding="utf-8") as f:
        json.dump(
            {key: asdict(value) for key, value in sticker_metadata.items()},
            f,
            ensure_ascii=False,
            indent=4,
        )
