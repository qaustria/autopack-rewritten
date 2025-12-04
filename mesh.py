import bpy
import os
import math
from pathlib import Path
from collections import deque
from PIL import Image


class Mesh:
    def __init__(self, base_folder, output_path, find_asset_fn):
        self.base_folder = Path(base_folder)
        self.output_path = Path(output_path)
        self.find_asset = find_asset_fn
        os.makedirs(self.output_path, exist_ok=True)

    def _edge_expand_512(self, img, max_dist=48, opacity_threshold=0, force_opaque=False):
        src = img.resize((512, 512), Image.Resampling.NEAREST)
        w, h = src.size
        src_pixels = src.load()

        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        nsrc_x = [[-1] * w for _ in range(h)]
        nsrc_y = [[-1] * w for _ in range(h)]
        q = deque()

        for y in range(h):
            for x in range(w):
                r, g, b, a = src_pixels[x, y]
                if a > opacity_threshold:
                    dist[y][x] = 0
                    nsrc_x[y][x] = x
                    nsrc_y[y][x] = y
                    q.append((x, y))

        while q:
            x, y = q.popleft()
            d = dist[y][x]
            if d >= max_dist:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h:
                    continue
                nd = d + 1
                if nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    nsrc_x[ny][nx] = nsrc_x[y][x]
                    nsrc_y[ny][nx] = nsrc_y[y][x]
                    q.append((nx, ny))

        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        out_pixels = out.load()
        inv_max = 1.0 / max_dist

        for y in range(h):
            for x in range(w):
                d = dist[y][x]
                if d == INF or d > max_dist:
                    continue

                sx = nsrc_x[y][x]
                sy = nsrc_y[y][x]
                if sx < 0 or sy < 0:
                    continue

                r, g, b, a = src_pixels[sx, sy]
                src_alpha = 255 if force_opaque else a

                alpha = max(0.0, (max_dist - float(d)) * inv_max)
                alpha = alpha * alpha

                out_a = int(alpha * src_alpha + 0.5)
                if out_a <= 0:
                    continue

                out_pixels[x, y] = (r, g, b, out_a)

        return out

    def createMesh(self, image_name):
        image_path = self.find_asset(f"{image_name}.png")
        if not image_path:
            print(f"Image does not exist! ({image_name})")
            return None

        ctx_obj = getattr(bpy.context, "object", None)
        if ctx_obj and ctx_obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

        export_name = self.output_path / f"{image_name}.fbx"

        base_img = Image.open(image_path).convert("RGBA")
        w, h = base_img.size
        if w != h:
            raise ValueError("Image must be square")

        original_resolution = w
        pixel_size = 2.0 / float(original_resolution)
        pixels = base_img.load()

        expanded = self._edge_expand_512(base_img, max_dist=48, opacity_threshold=0, force_opaque=False)
        resize_path = self.base_folder / f"{image_name}_resized.png"
        expanded.save(resize_path)

        mesh = bpy.data.meshes.new(image_name)
        obj = bpy.data.objects.new(image_name, mesh)
        bpy.context.collection.objects.link(obj)

        verts = []
        faces = []
        uvs = []

        x_off = original_resolution / 2.0
        y_off = original_resolution / 2.0

        for y in range(original_resolution):
            for x in range(original_resolution):
                r, g, b, a = pixels[x, y]
                if a <= 0:
                    continue

                z = 0.0

                v1 = ((x - x_off) * pixel_size, (y_off - y) * pixel_size, z)
                v2 = ((x + 1 - x_off) * pixel_size, (y_off - y) * pixel_size, z)
                v3 = ((x + 1 - x_off) * pixel_size, (y_off - (y + 1)) * pixel_size, z)
                v4 = ((x - x_off) * pixel_size, (y_off - (y + 1)) * pixel_size, z)

                base_idx = len(verts)
                verts.extend([v1, v2, v3, v4])
                faces.append([base_idx, base_idx + 1, base_idx + 2, base_idx + 3])

                uv1 = (x / original_resolution, (original_resolution - y) / original_resolution)
                uv2 = ((x + 1) / original_resolution, (original_resolution - y) / original_resolution)
                uv3 = ((x + 1) / original_resolution, (original_resolution - (y + 1)) / original_resolution)
                uv4 = (x / original_resolution, (original_resolution - (y + 1)) / original_resolution)

                uvs.extend([uv1, uv2, uv3, uv4])

        mesh.from_pydata(verts, [], faces)
        mesh.update()

        if uvs:
            uv_layer = mesh.uv_layers.new(name="UVMap")
            for i, uv in enumerate(uvs):
                uv_layer.data[i].uv = uv
            mesh.uv_layers.active = uv_layer
            mesh.uv_layers.active_index = 0

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        solid = obj.modifiers.new(name="Solidify", type="SOLIDIFY")
        solid.thickness = 0.13

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        valid_names = ["iron_ingot", "diamond", "ender_pearl", "emerald", "apple_golden"]
        rot_x = math.radians(90)
        rot_y = math.radians(-45)

        if image_name in valid_names:
            obj.rotation_euler[0] = rot_x
        else:
            obj.rotation_euler[0] = rot_x
            obj.rotation_euler[1] = rot_y

        mat = bpy.data.materials.new(name="PixelArtMaterial")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        for node in list(nodes):
            nodes.remove(node)

        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        tex_node = nodes.new("ShaderNodeTexImage")

        tex_node.image = bpy.data.images.load(str(resize_path))
        tex_node.interpolation = "Closest"

        links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

        obj.data.materials.append(mat)
        obj.data.materials[0] = mat

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.export_scene.fbx(
            filepath=str(export_name),
            global_scale=0.01,
            use_selection=True,
            add_leaf_bones=False,
            mesh_smooth_type="OFF",
            use_tspace=True,
        )

        print(f"Object exported to {self.output_path}")
        return str(export_name)
