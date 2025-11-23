import time
import requests
from pathlib import Path


class Upload:
    def __init__(self, api_key, creator_user_id):
        self.api_key = api_key
        self.creator_user_id = creator_user_id
        self.headers = {"x-api-key": api_key}
        self.results = {}

    def _poll(self, op_id):
        url = f"https://apis.roblox.com/assets/v1/operations/{op_id}"

        while True:
            data = requests.get(url, headers=self.headers).json()

            if data.get("done"):
                return data["response"]["assetId"]

            time.sleep(0.05)

    def uploadMesh(self, fbx_path: str):
        fbx_path = Path(fbx_path)

        if not fbx_path.exists():
            print(f"[ERROR] FBX not found: {fbx_path}")
            return None

        request_payload = (
            None,
            '{{ "assetType": "Mesh", "displayName": "Item", '
            '"description": "Mesh upload", '
            '"creationContext": {{ "creator": {{ "userId": "{}" }} }} }}'
            .format(self.creator_user_id)
        )

        files = {
            "request": request_payload,
            "fileContent": (fbx_path.name, open(fbx_path, "rb"), "model/fbx"),
        }

        resp = requests.post(
            "https://apis.roblox.com/assets/v1/assets",
            headers=self.headers,
            files=files
        ).json()

        print(resp)

        op = resp.get("operationId")
        if not op:
            print("[ERROR] Mesh upload failed: no operationId")
            return None

        asset_id = self._poll(op)
        self.results[fbx_path.name] = asset_id
        return asset_id

    def uploadImage(self, resized_png_path: str):
        image_path = Path(resized_png_path)

        if not image_path.exists():
            print(f"[ERROR] 512x texture not found: {image_path}")
            return None

        request_json = (
            '{{'
            '"assetType": "Image", '
            f'"displayName": "{image_path.stem}", '
            '"description": "512x texture", '
            '"creationContext": {{ "creator": {{ "userId": "{}" }} }}'
            '}}'
        ).format(self.creator_user_id)

        files = {
            "request": (None, request_json, "application/json"),
            "fileContent": (image_path.name, open(image_path, "rb"), "image/png"),
        }

        resp = requests.post(
            "https://apis.roblox.com/assets/v1/assets",
            headers=self.headers,
            files=files
        ).json()

        op_id = resp.get("operationId")
        if not op_id:
            print("[ERROR] Image upload failed: no operationId")
            return None

        asset_id = self._poll(op_id)
        self.results[image_path.name] = asset_id
        return asset_id
