# AutoPack
Automatic Texturepack creator for [BridgeDuel](https://www.roblox.com/games/139566161526375/Bridge-Duel)
For support, join our [Discord server](https://discord.gg/Rz6QKYWgYj)
## Requirements

- Python 3.11
- bpy
- Roblox API key

## Setup

### Quick Install (Recommended)

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

**Or use the Python installer (cross-platform):**
```bash
python install.py
```

### Manual Install

1. Install Python dependencies:
```bash
pip install bpy==4.5.4 --extra-index-url https://download.blender.org/pypi/
pip install Pillow
pip install requests
pip install zstandard
```

2. Configure your API credentials:
   - Copy `config.example.py` to `config.py`
   - Add your Roblox API key and user ID to `config.py`

## Usage

Run the main script:
```bash
python main.py
```

The script will:
1. Ask you to select a texture pack (.zip file)
2. Choose between clay/wool block mode
3. Extract required textures
4. Generate meshes for square textures
5. Resize textures to 512x512
6. Upload assets to Roblox
7. Generate `generated_items.json` with asset IDs

## Files

- `main.py` - Main entry point
- `mesh.py` - Blender mesh generation
- `upload.py` - Roblox asset uploader
- `zip.py` - Texture pack extraction
- `utils/compress.py` - Compress texture pack JSON
- `utils/decompress.py` - Decompress texture pack JSON

## Notes

- Only square textures will have meshes generated
- Non-square textures will be uploaded as images only
- The `assets/` and `exported/` folders are automatically created and cleaned up

