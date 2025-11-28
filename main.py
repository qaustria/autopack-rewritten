from mesh import Mesh
from upload import Upload
from zip import Zip
from packutil import PackUtil
from config import API_KEY, CREATOR_USER_ID
from pathlib import Path
from PIL import Image
import json
import re
import os
import time
import tkinter as tk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor

def pick_zip_file():
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    fp = filedialog.askopenfilename(title="Select your texture pack (.zip)", filetypes=[("Zip Files", "*.zip")])
    root.destroy()
    return fp

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"
EXPORT_DIR = BASE_DIR / "exported"
EXPORT_DIR.mkdir(exist_ok=True)

CLAY_BLOCK_NAMES = {
    "ClayBlue": "hardened_clay_stained_blue.png",
    "ClayRed": "hardened_clay_stained_red.png",
    "ClayWhite": "hardened_clay_stained_white.png"
}

def find_asset(filename):
    p = ASSET_DIR / filename
    return str(p) if p.exists() else None

TEMPLATE_KEYS = [
    "JumpPotionMesh","GoldAppleTexture","Bow0Texture","ClayWhite","Bow1Texture","Bow2Texture","ClayGreen",
    "BlocksVPImage","ClayOrange","ClayGrey","SpeedPotionVPImage","GoldSwordVPImage","JumpPotionTexture",
    "SwordTexture","Bow2Mesh","PearlVPImage","SwordMesh","PearlTexture","DiamondSwordVPImage",
    "JumpPotionVPImage","IronVPImage","SpeedPotionMesh","SpeedPotionTexture","PearlMesh","Bow0Mesh",
    "EmeraldVPImage","DiamondVPImage","EmeraldTexture","GoldAppleMesh","Bow3Texture","GoldPickaxeTexture",
    "Bow1Mesh","ClayYellow","PickaxeVPImage","Bow3Mesh","DefaultBowVPImage","GoldAppleVPImage","IronTexture",
    "ClayPurple","PickaxeTexture","WoodenSwordTexture","DiamondSwordTexture","WoodenPickaxeTexture",
    "GoldPickaxeVPImage","PickaxeMesh","GoldSwordTexture","DiamondTexture","WoodenPickaxeVPImage","ClayCyan",
    "ClayRed","SwordVPImage","WoodenSwordVPImage","DiamondMesh","DiamondPickaxeVPImage","IronMesh",
    "DiamondPickaxeTexture","EmeraldMesh","ClayBlue"
]

def camel_to_snake(n):
    n1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", n)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", n1).lower()

def get_base_name(k):
    if k.startswith("Clay"):
        return camel_to_snake(k), "Texture"
    for suf in ("Mesh","Texture","VPImage"):
        if k.endswith(suf):
            return camel_to_snake(k[:-len(suf)]), suf
    return None, None

def get_file_base(base):
    if base.startswith("clay_"):
        c = base.split("_")[1]
        if c == "grey":
            c = "gray"
        return f"wool_colored_{c}"
    o = {
        "gold_apple":"apple_golden","pearl":"ender_pearl","jump_potion":"potion_bottle_drinkable",
        "speed_potion":"potion_bottle_drinkable","wooden_sword":"wood_sword","wooden_pickaxe":"wood_pickaxe",
        "sword":"iron_sword","pickaxe":"stone_pickaxe","iron":"iron_ingot","gold_sword":"gold_sword",
        "gold_pickaxe":"gold_pickaxe","diamond_sword":"diamond_sword","diamond_pickaxe":"diamond_pickaxe",
        "bow0":"bow_standby","bow1":"bow_pulling_0","bow2":"bow_pulling_1","bow3":"bow_pulling_2",
        "default_bow":"bow_standby"
    }
    return o.get(base, base)

required_pngs = []
for k in TEMPLATE_KEYS:
    base, kind = get_base_name(k)
    if base:
        required_pngs.append(get_file_base(base) + ".png")
required_pngs.extend(CLAY_BLOCK_NAMES.values())

zipper = Zip(assets_folder=ASSET_DIR, exported_folder=EXPORT_DIR)
zp = pick_zip_file()
if not zp:
    raise SystemExit
zipper.unzip_pack(zp, required_pngs)

generator = Mesh(base_folder=ASSET_DIR, output_path=EXPORT_DIR, find_asset_fn=find_asset)
uploader = Upload(api_key=API_KEY, creator_user_id=CREATOR_USER_ID)

base_info = {}
for k in TEMPLATE_KEYS:
    base, kind = get_base_name(k)
    if not base:
        continue
    d = base_info.setdefault(base, {"mesh":[], "tex":[], "vp":[]})
    d["mesh"].append(k) if kind=="Mesh" else d["vp"].append(k) if kind=="VPImage" else d["tex"].append(k)

mesh_jobs = []
resize_jobs = []
upload_jobs = []
new_values = {}
clay_json = {}
total_timer_start = time.time()
clay_blocks = {}

for ck, fname in CLAY_BLOCK_NAMES.items():
    candidate = ASSET_DIR / fname
    if candidate.exists():
        clay_blocks[ck] = candidate

if not clay_blocks:
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    folder = filedialog.askdirectory(title="Locate clay textures (hardened_clay_*.png)")
    root.destroy()
    if folder:
        folder = Path(folder)
        for ck, fname in CLAY_BLOCK_NAMES.items():
            candidate = folder / fname
            if candidate.exists():
                clay_blocks[ck] = candidate

for base, info in base_info.items():
    file_base = get_file_base(base)
    src_png = ASSET_DIR / f"{file_base}.png"
    if not src_png.exists():
        continue
    with Image.open(src_png) as img:
        w, h = img.size
    if info["mesh"] and w != h:
        info["mesh"] = []
    if info["mesh"]:
        mesh_jobs.append((file_base, info["mesh"]))
    if info["tex"]:
        dst = ASSET_DIR / f"{file_base}_resized.png"
        resize_jobs.append((src_png,dst,info["tex"]))
    if info["vp"]:
        dst = ASSET_DIR / f"{file_base}_vp.png"
        resize_jobs.append((src_png,dst,info["vp"]))

for ck, cp in clay_blocks.items():
    dst = ASSET_DIR / f"{ck}_clay_resized.png"
    resize_jobs.append((cp,dst,f"CLAY:{ck}"))

def resize_worker(a):
    src, dst, keys = a
    img = Image.open(src).convert("RGBA")
    img = img.resize((512,512), Image.Resampling.NEAREST)
    img.save(dst)
    return dst, keys

def mesh_worker(a):
    file_base, keys = a
    fbx = generator.createMesh(file_base)
    return fbx, keys

resize_duration = 0.0
if resize_jobs:
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as p:
        for dst, keys in p.map(resize_worker, resize_jobs):
            upload_jobs.append((str(dst),"tex",keys))
    resize_duration = time.time() - t0

mesh_duration = 0.0
if mesh_jobs:
    t0 = time.time()
    for fbx, keys in map(mesh_worker, mesh_jobs):
        if fbx:
            upload_jobs.append((fbx,"mesh",keys))
    mesh_duration = time.time() - t0

def upload_worker(a):
    path, typ, keys = a
    aid = uploader.uploadMesh(path) if typ=="mesh" else uploader.uploadImage(path)
    return aid, keys

upload_duration = 0.0
if upload_jobs:
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as p:
        for aid, keys in p.map(upload_worker, upload_jobs):
            if not aid:
                continue
            if isinstance(keys, list):
                for k in keys:
                    new_values[k] = str(aid)
            elif isinstance(keys, str) and keys.startswith("CLAY:"):
                ck = keys.split(":",1)[1]
                clay_json[ck] = str(aid)
    upload_duration = time.time() - t0
total_duration = time.time() - total_timer_start

print(f"Resize time: {resize_duration:.2f}s")
print(f"Mesh time: {mesh_duration:.2f}s")
print(f"Upload time: {upload_duration:.2f}s")
print(f"Total time: {total_duration:.2f}s")

final_data = {k: new_values.get(k,"0") for k in TEMPLATE_KEYS}

compressed = PackUtil.compress_json(json.dumps(final_data))
print(compressed)
print(json.dumps(clay_json, indent=4))

zipper.cleanup()
