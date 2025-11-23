import base64
import json
import zstandard as zstd
import sys

print("Paste your texturepacks JSON: ")

lines = []
while True:
    line = sys.stdin.readline()
    if not line or line.strip() == "":
        break
    if line.strip().startswith(">>"):
        line = line.strip()[2:].strip()
    lines.append(line.rstrip())
data = "\n".join(lines).strip()

if not data.startswith("{"):
    data = "{\n" + data
if not data.endswith("}"):
    data = data + "\n}"

parsed = json.loads(data)
json_bytes = json.dumps(parsed, separators=(",", ":")).encode("utf-8")
cctx = zstd.ZstdCompressor(level=3)
compressed = cctx.compress(json_bytes)
b64 = base64.b64encode(compressed).decode("utf-8")


final_obj = {
    "m": None,
    "t": "buffer",
    "zbase64": b64
}