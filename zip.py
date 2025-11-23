from pathlib import Path
import zipfile
import shutil


class Zip:
    def __init__(self, assets_folder: Path, exported_folder: Path):
        self.assets_folder = Path(assets_folder)
        self.exported_folder = Path(exported_folder)
        self.assets_folder.mkdir(exist_ok=True)
        self.exported_folder.mkdir(exist_ok=True)

    def unzip_pack(self, zip_path: str, required_filenames: list[str]):
        zip_path = Path(zip_path)
        if not zip_path.exists():
            print(f"[ERROR] Zip not found: {zip_path}")
            return

        required = set(required_filenames)

        with zipfile.ZipFile(zip_path, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = Path(info.filename).name
                if name in required:
                    out_path = self.assets_folder / name
                    with zf.open(info, "r") as src, open(out_path, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    print(f"[OK] Extracted {name} -> {out_path}")

    def cleanup(self):
        if self.assets_folder.exists():
            shutil.rmtree(self.assets_folder, ignore_errors=True)
        if self.exported_folder.exists():
            shutil.rmtree(self.exported_folder, ignore_errors=True)
