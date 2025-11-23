from mesh import Mesh
from upload import Upload
from zip import Zip

try:
    from config import API_KEY, CREATOR_USER_ID
except ImportError:
    print("[ERROR] config.py not found!")
    print("Please copy config.example.py to config.py and add your API key and user ID.")
    raise SystemExit(1)

from pathlib import Path
from PIL import Image
import json
import re
import os
import tkinter as tk
from tkinter import filedialog

from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def pick_zip_file():
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    file_path = filedialog.askopenfilename(
        title="Select your texture pack (.zip)",
        filetypes=[("Zip Files", "*.zip")]
    )
    root.destroy()
    return file_path


CLAY_MODE = input("Pick a block mode (clay/wool): ").strip().lower()
if CLAY_MODE not in ("clay", "wool"):
    CLAY_MODE = "wool"

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"
EXPORT_DIR = BASE_DIR / "exported"
EXPORT_DIR.mkdir(exist_ok=True)


def find_asset(filename: str) -> str | None:
    p = ASSET_DIR / filename
    return str(p) if p.exists() else None


TEMPLATE_KEYS = [
    "JumpPotionMesh", "GoldAppleTexture", "Bow0Texture", "ClayWhite", "Bow1Texture",
    "Bow2Texture", "ClayGreen", "BlocksVPImage", "ClayOrange", "ClayGrey",
    "SpeedPotionVPImage", "GoldSwordVPImage", "JumpPotionTexture", "SwordTexture",
    "Bow2Mesh", "PearlVPImage", "SwordMesh", "PearlTexture", "DiamondSwordVPImage",
    "JumpPotionVPImage", "IronVPImage", "SpeedPotionMesh", "SpeedPotionTexture",
    "PearlMesh", "Bow0Mesh", "EmeraldVPImage", "DiamondVPImage", "EmeraldTexture",
    "GoldAppleMesh", "Bow3Texture", "GoldPickaxeTexture", "Bow1Mesh", "ClayYellow",
    "PickaxeVPImage", "Bow3Mesh", "DefaultBowVPImage", "GoldAppleVPImage",
    "IronTexture", "ClayPurple", "PickaxeTexture", "WoodenSwordTexture",
    "DiamondSwordTexture", "WoodenPickaxeTexture", "GoldPickaxeVPImage",
    "PickaxeMesh", "GoldSwordTexture", "DiamondTexture", "WoodenPickaxeVPImage",
    "ClayCyan", "ClayRed", "SwordVPImage", "WoodenSwordVPImage", "DiamondMesh",
    "DiamondPickaxeVPImage", "IronMesh", "DiamondPickaxeTexture", "EmeraldMesh",
    "ClayBlue"
]


def camel_to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def get_base_name(key: str):
    if key.startswith("Clay"):
        return camel_to_snake(key), "Texture"
    for suf in ("Mesh", "Texture", "VPImage"):
        if key.endswith(suf):
            base = camel_to_snake(key[:-len(suf)])
            return base, suf
    return None, None


def get_file_base(base: str):
    if base.startswith("clay_"):
        color = base.split("_")[1]
        if color == "grey":
            color = "gray"
        return f"wool_colored_{color}" if CLAY_MODE == "wool" else f"hardened_clay_stained_{color}"

    overrides = {
        "gold_apple": "apple_golden",
        "pearl": "ender_pearl",
        "jump_potion": "potion_bottle_drinkable",
        "speed_potion": "potion_bottle_drinkable",
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


required_pngs = []
for k in TEMPLATE_KEYS:
    base, kind = get_base_name(k)
    if base:
        required_pngs.append(get_file_base(base) + ".png")

zipper = Zip(assets_folder=ASSET_DIR, exported_folder=EXPORT_DIR)

zip_path = pick_zip_file()
if not zip_path:
    print("No pack selected. Exiting.")
    raise SystemExit

zipper.unzip_pack(zip_path, required_pngs)


generator = Mesh(
    base_folder=ASSET_DIR,
    output_path=EXPORT_DIR,
    find_asset_fn=find_asset
)

uploader = Upload(api_key=API_KEY, creator_user_id=CREATOR_USER_ID)

base_info = {}
for key in TEMPLATE_KEYS:
    base, kind = get_base_name(key)
    if not base:
        continue
    info = base_info.setdefault(base, {"mesh": [], "tex": [], "vp": []})
    if kind == "Mesh":
        info["mesh"].append(key)
    elif kind == "VPImage":
        info["vp"].append(key)
    else:
        info["tex"].append(key)

resize_jobs = []
upload_jobs = []
new_values = {}


mesh_total_start = time.time()

for base, info in base_info.items():
    file_base = get_file_base(base)
    src_png = ASSET_DIR / f"{file_base}.png"

    if not src_png.exists():
        print(f"[WARN] Missing PNG: {src_png}")
        continue

    w, h = Image.open(src_png).size
    if info["mesh"] and w != h:
        print(f"[SKIP] Mesh for '{file_base}' — texture not square ({w}x{h})")
        info["mesh"] = []

    if info["mesh"]:
        start = time.time()
        fbx_path = generator.createMesh(file_base)
        took = time.time() - start
        print(f"[TIME] Mesh for {file_base} took {took:.3f}s")

        if fbx_path:
            upload_jobs.append((fbx_path, "mesh", info["mesh"]))

    if info["tex"]:
        resized = ASSET_DIR / f"{file_base}_resized.png"
        resize_jobs.append((src_png, resized, info["tex"]))
    
    if info["vp"]:
        vp_resized = ASSET_DIR / f"{file_base}_vp.png"
        resize_jobs.append((src_png, vp_resized, info["vp"]))

mesh_total = time.time() - mesh_total_start
print(f"[TOTAL TIME] Mesh creation: {mesh_total:.3f}s")


def resize_worker(args):
    src, dst, keys = args
    start = time.time()

    if not dst.exists():
        img = Image.open(src).convert("RGBA")
        img = img.resize((512, 512), Image.Resampling.NEAREST)
        img.save(dst)

    took = time.time() - start
    print(f"[TIME] Resized {src.name} in {took:.3f}s")
    return dst, keys


resize_total_start = time.time()

with ThreadPoolExecutor(max_workers=8) as pool:
    for dst, keys in pool.map(resize_worker, resize_jobs):
        upload_jobs.append((str(dst), "tex", keys))

resize_total = time.time() - resize_total_start
print(f"[TOTAL TIME] Texture resizing: {resize_total:.3f}s")


def upload_worker(job):
    path, typ, keys = job
    start = time.time()

    if typ == "mesh":
        asset_id = uploader.uploadMesh(path)
    else:
        asset_id = uploader.uploadImage(path)

    took = time.time() - start
    print(f"[TIME] Upload ({typ}) {path} in {took:.3f}s")

    return asset_id, keys


upload_total_start = time.time()

with ThreadPoolExecutor(max_workers=8) as pool:
    for asset_id, keys in pool.map(upload_worker, upload_jobs):
        for k in keys:
            new_values[k] = str(asset_id)

upload_total = time.time() - upload_total_start
print(f"[TOTAL TIME] Uploading: {upload_total:.3f}s")


final_data = {k: new_values.get(k, "0") for k in TEMPLATE_KEYS}

out_path = BASE_DIR / "generated_items.json"
with out_path.open("w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=4)

print(f"[✓] Wrote {out_path}")

zipper.cleanup()
print("[✓] Cleanup done.")
