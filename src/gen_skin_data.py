"""
Aggregate all skin data into a json file, including price field but set to zero
"""

import os
import re
import json
import requests
import dataclasses
from dataclasses import asdict
from constants import OUTPUT_DIRECTORY, ASSETS_DOMAIN
from spacecases_common import (
    remove_skin_name_formatting,
    Skin,
)
from util import get_all_conditions_for_float_range


def run(api_data) -> dict[str, Skin]:
    result = {}
    for datum in api_data:
        # extract information
        formatted_name = datum["name"]
        # float range
        min_float = datum["min_float"]
        if min_float is None:
            min_float = 0.0
        max_float = datum["max_float"]
        if max_float is None:
            max_float = 1.0
        # all available conditions
        available_conditions = get_all_conditions_for_float_range(min_float, max_float)
        for condition in available_conditions:
            # if its a doppler include its phase in the name
            if "Doppler" in formatted_name:
                phase = datum["phase"]
                full_formatted_name = f"{formatted_name} - {phase} ({condition})"
            else:
                full_formatted_name = f"{formatted_name} ({condition})"
            # the flavour text is between the italic html tags
            full_unformatted_name = remove_skin_name_formatting(full_formatted_name)
            description_match = re.search(r"<i>(.*?)</i>", datum["description"])
            if description_match:
                description = description_match.group(1)
            else:
                description = None
            # result data
            skin_datum = Skin(
                full_formatted_name,
                description,
                os.path.join(
                    ASSETS_DOMAIN,
                    "generated",
                    "images",
                    "unformatted",
                    f"{full_unformatted_name}.png",
                ),
                datum["rarity"]["name"],
                min_float,
                max_float,
                0,
            )
            # add for normal variation
            result[full_unformatted_name] = skin_datum
            # add for stattrak variation
            if datum.get("stattrak", False):
                if "★" in full_formatted_name:
                    stattrak_full_formatted_name = full_formatted_name.replace(
                        "★", "★ StatTrak™"
                    )
                else:
                    stattrak_full_formatted_name = f"StatTrak™ {full_formatted_name}"
                stattrak_full_unformatted_name = remove_skin_name_formatting(
                    stattrak_full_formatted_name
                )
                stattrak_skin_datum = dataclasses.replace(skin_datum)
                stattrak_skin_datum.formatted_name = stattrak_full_formatted_name
                stattrak_skin_datum.image_url = os.path.join(
                    ASSETS_DOMAIN,
                    "generated",
                    "images",
                    "unformatted",
                    f"{stattrak_full_unformatted_name}.png",
                )
                result[stattrak_full_unformatted_name] = stattrak_skin_datum
            # add for souvenir version
            if datum.get("souvenir", False):
                souvenir_full_formatted_name = f"Souvenir {full_formatted_name}"
                souvenir_full_unformatted_name = remove_skin_name_formatting(
                    souvenir_full_formatted_name
                )
                souvenir_skin_datum = dataclasses.replace(skin_datum)
                souvenir_skin_datum.formatted_name = souvenir_full_formatted_name
                souvenir_skin_datum.image_url = os.path.join(
                    ASSETS_DOMAIN,
                    "generated",
                    "images",
                    "unformatted",
                    f"{souvenir_full_unformatted_name}.png",
                )
                result[souvenir_full_unformatted_name] = souvenir_skin_datum
    return result


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    api_data = requests.get(
        "https://bymykel.github.io/CSGO-API/api/en/skins.json"
    ).json()
    result = run(api_data)
    out_result = {key: asdict(value) for key, value in result.items()}
    with open(f"{OUTPUT_DIRECTORY}/skin_data.json", "w+", encoding="utf-8") as f:
        json.dump(out_result, f, ensure_ascii=False, indent=4)
