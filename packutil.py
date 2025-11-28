import base64
import zstandard as zstd
import json

class PackUtil:
    @staticmethod
    def compress_json(raw_json_text):
        raw_bytes = raw_json_text.encode("utf-8")
        cctx = zstd.ZstdCompressor(level=0)
        compressed = cctx.compress(raw_bytes)
        b64 = base64.b64encode(compressed).decode("utf-8")
        final_obj = {"m": None, "t": "buffer", "zbase64": b64}
        return json.dumps(final_obj)

    @staticmethod
    def decompress_json(json_data):
        parsed = json.loads(json_data)
        compressed = base64.b64decode(parsed["zbase64"])
        dctx = zstd.ZstdDecompressor()
        raw = dctx.decompress(compressed)
        return raw.decode("utf-8")
