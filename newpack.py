from pathlib import Path
import zipfile

# file names for the new clay textures
NEW_CLAY_BLOCK_NAMES = {
    "ClayBlue": "blue_terracotta.png",
    "ClayRed": "red_terracotta.png",
    "ClayWhite": "white_terracotta.png",
}

# this is to detect if a texturepack is a new texturepack
NEW_PACK_MARKERS = {
    "netherite_ingot.png",
    "trident.png",
    "goat_horn.png",
    "trial_key.png",
    "wind_charge.png",
    "wolf_armor.png",
    "mace.png",
}


def is_new_java_pack(zip_path: str | Path) -> bool:
    zip_path = Path(zip_path)
    if not zip_path.exists() or zip_path.suffix.lower() != ".zip":
        return False

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            entries = [info.filename for info in zf.infolist()]
    except Exception:
        return False

    base_names = {Path(n).name for n in entries if not n.endswith("/")}
    if base_names.intersection(NEW_PACK_MARKERS):
        return True

def get_new_base(base: str) -> str:
    if base.startswith("clay_"):
        color = base.split("_", 1)[1]
        if color == "grey":
            color = "gray"
        return f"{color}_terracotta"

    overrides = {
        "gold_apple": "golden_apple",
        "pearl": "ender_pearl",
        "jump_potion": "potion",
        "speed_potion": "potion",
        "wooden_sword": "wooden_sword",
        "wooden_pickaxe": "wooden_pickaxe",
        "sword": "iron_sword",
        "pickaxe": "stone_pickaxe",
        "iron": "iron_ingot",
        "gold_sword": "golden_sword",
        "gold_pickaxe": "golden_pickaxe",
        "diamond_sword": "diamond_sword",
        "diamond_pickaxe": "diamond_pickaxe",
        "bow0": "bow",
        "bow1": "bow_pulling_0",
        "bow2": "bow_pulling_1",
        "bow3": "bow_pulling_2",
        "default_bow": "bow",
    }
    return overrides.get(base, base)
