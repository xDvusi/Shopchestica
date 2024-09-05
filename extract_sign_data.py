import json
from litemapy import Schematic
import sys
import csv


def extract_sign_data(file_path, export_type):
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
                    if ":" in json_obj["text"]:
                        split_text = json_obj["text"].split(":", 1)
                        first_part = split_text[0].strip()
                        second_part = split_text[1].strip()
                        text_fields.append(first_part)
                        text_fields.append(second_part)
                        continue
                    else:
                        text_fields.append(json_obj["text"])
                if "[ChestShop]" not in text_fields:
                    continue
                else:
                    sign_data.append(text_fields)
    if export_type == "csv":
        csv_export(sign_data, shop_name)
    elif export_type == "json":
        json_export(sign_data, shop_name)
    else:
        print("Unsupported filetype, exiting")
        return


def json_export(sign, shop):
    shop_name = shop.replace("'", "")
    shop_data = {}
    for entry in sign:
        if "" in entry:
            continue
        text = entry
        for line in text[1:-1]:
            if "S" in line:
                sell_value = line.strip("S")
            elif "B" in line:
                buy_value = line.strip("B")
        item_name = text[-1]
        shop_data.setdefault(item_name, [])
        shop_data[item_name].append(
            {
                "Quantity": text[1],
                "Sell_price": sell_value,
                "Buy_price": buy_value,
            }
        )
    with open(f"{shop_name}.json", "w", encoding="utf-8") as o:
        json.dump(shop_data, o, ensure_ascii=False, indent=4)

    print(f"Saved shop data to {shop_name}.json")


def csv_export(sign, shop):
    csv_sheet = []
    for entry in sign:
        if "" in entry:
            continue
        text = entry
        csv_sort = {
            "Product": text[-1],
            "Quantity": text[1],
            "Sell Price": None,
            "Buy Price": None,
        }

        for line in text[1:-1]:
            if "S" in line:
                csv_sort["Sell Price"] = line.strip("S")
            elif "B" in line:
                csv_sort["Buy Price"] = line.strip("B")

        csv_sheet.append(csv_sort)

    csv_file = shop + ".csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["Product", "Quantity", "Sell Price", "Buy Price"]
        )
        writer.writeheader()
        writer.writerows(csv_sheet)

    print("Saved shop data to " + csv_file)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_sign_data.py [csv/json] <file_path>")
        sys.exit(1)
    export_type = sys.argv[1].lower()
    file_path = sys.argv[2]
    extract_sign_data(file_path, export_type)
