from pathlib import Path


def is_mcpack_file(path: str | Path) -> bool:
    return Path(path).suffix.lower() == ".mcpack"


def get_mcpack_file_base(base: str) -> str:
    if base.startswith("clay_"):
        color = base.split("_", 1)[1]
        if color == "grey":
            color = "gray"
        return f"wool_colored_{color}"

    overrides = {
        "gold_apple": "apple_golden",
        "pearl": "ender_pearl",
        "jump_potion": "potion_bottle_jump",
        "speed_potion": "potion_bottle_moveSpeed",
        "wooden_sword": "wood_sword",
        "wooden_pickaxe": "wood_pickaxe",
        "sword": "iron_sword",
        "pickaxe": "stone_pickaxe",
        "iron": "iron_ingot",
        "gold_sword": "gold_sword",
        "gold_pickaxe": "gold_pickaxe",
        "diamond_sword": "diamond_sword",
        "diamond_pickaxe": "diamond_pickaxe",
        "bow0": "bow_standby",
        "bow1": "bow_pulling_0",
        "bow2": "bow_pulling_1",
        "bow3": "bow_pulling_2",
        "default_bow": "bow_standby",
    }
    return overrides.get(base, base)
