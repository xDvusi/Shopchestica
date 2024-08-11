import json
from litemapy import Schematic
import sys
import csv


def extract_sign_data(file_path):
    schematic = Schematic.load(file_path)
    shop_name = file_path.lstrip(".\\").rstrip(".litematic")
    sign_data = []
    for region in schematic.regions.values():
        for tile_entity in region.tile_entities:
            if (
                "id" in tile_entity.to_nbt()
                and tile_entity.to_nbt()["id"] == "minecraft:sign"
            ):
                sign_entity = tile_entity.to_nbt()
                text_fields = []
                for item in sign_entity["front_text"]["messages"]:
                    json_obj = json.loads(item)
                    if len(json_obj) > 2:
                        continue

                    if ":" in json_obj["text"]:
                        split_text = json_obj["text"].split(":", 1)
                        first_part = split_text[0].strip()
                        second_part = split_text[1].strip()
                        text_fields.append(first_part)
                        text_fields.append(second_part)
                        continue
                    for text in json_obj:
                        text_fields.append(json_obj["text"])
                sign = {
                    "Text": text_fields,
                }
                sign_data.append(sign)
    csv_sheet = []
    for entry in sign_data:
        if "" in entry["Text"]:
            continue
        text = entry["Text"]
        csv_sort = {
            "Product": text[-1],
            "Quantity": text[0],
            "Sell Price": None,
            "Buy Price": None,
        }

        for line in text[1:-1]:
            if line.startswith("S"):
                csv_sort["Sell Price"] = line[1:].strip()
            elif line.startswith(" S"):
                csv_sort["Sell Price"] = line[2:].strip()
            elif line.startswith("B"):
                csv_sort["Buy Price"] = line[1:].strip()
            elif line.startswith(" B"):
                csv_sort["Buy Price"] = line[2:].strip()

        csv_sheet.append(csv_sort)

    csv_file = shop_name + ".csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["Product", "Quantity", "Sell Price", "Buy Price"]
        )
        writer.writeheader()
        writer.writerows(csv_sheet)

    print("Saved shop data to " + csv_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_sign_data.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    extract_sign_data(file_path)
