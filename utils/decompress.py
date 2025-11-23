import base64
import json
import zstandard as zstd


print("Paste your texturepack: ")
data = input().strip()

parsed = json.loads(data)
b64 = parsed["zbase64"]
raw = base64.b64decode(b64)
dctx = zstd.ZstdDecompressor()
decompressed = dctx.decompress(raw)

obj = json.loads(decompressed)
print(json.dumps(obj, indent=4))