import socket
import json

def send_blender_code(code):
    host = 'localhost'
    port = 9876
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            payload = {"type": "execute_code", "params": {"code": code}}
            s.sendall(json.dumps(payload).encode('utf-8'))
            return s.recv(4096).decode('utf-8')
    except Exception as e:
        return str(e)

code = """
import bpy
import random

# Clear stars first to avoid duplicates
for obj in bpy.data.objects:
    if obj.name.startswith("Star"):
        bpy.data.objects.remove(obj, do_unlink=True)

# Add 100 stars
for i in range(100):
    x = random.uniform(-100, 100)
    y = random.uniform(-100, 100)
    z = random.uniform(-100, 100)
    if abs(x) < 15 and abs(y) < 15 and abs(z) < 15: continue
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(x, y, z))
    bpy.context.object.name = f"Star_{i}"

# Glow up the sphere
sphere = bpy.data.objects.get('Causal_Horizon')
if sphere:
    mat = sphere.data.materials[0]
    nodes = mat.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')
    if bsdf:
        try:
            # Modern Blender 4.0+
            bsdf.inputs['Emission Color'].default_value = (0, 0.5, 1, 1)
            bsdf.inputs['Emission Strength'].default_value = 20.0
        except:
            # Fallback
            bsdf.inputs['Emission'].default_value = (0, 0.5, 1, 1)
            bsdf.inputs['Emission Strength'].default_value = 20.0

# Wide angle camera
cam = bpy.context.scene.camera
if cam:
    cam.data.lens = 24
"""

print(send_blender_code(code))
