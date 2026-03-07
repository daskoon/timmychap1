import socket
import json

def send_blender_code(code):
    host = 'localhost'
    port = 9876
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(15)
            s.connect((host, port))
            payload = {"type": "execute_code", "params": {"code": code}}
            s.sendall(json.dumps(payload).encode('utf-8'))
            return s.recv(8192).decode('utf-8')
    except Exception as e:
        return str(e)

overhaul_code = """
import bpy
import bmesh
import math
import random

# 1. CLEANUP
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. CREATE THE RECURSIVE CORE (Nested Dodecahedrons)
for i in range(3):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=(1 + i*0.5), location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = f"Core_Layer_{i}"
    
    # Material
    mat = bpy.data.materials.new(name=f"Glass_{i}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    # Cyan/Gold mix
    color = (0, 0.5, 1, 1) if i % 2 == 0 else (1, 0.8, 0, 1)
    bsdf.inputs[0].default_value = color
    bsdf.inputs['Transmission Weight'].default_value = 1.0 # Glassy
    bsdf.inputs['Roughness'].default_value = 0.1
    try:
        bsdf.inputs['Emission Color'].default_value = color
        bsdf.inputs['Emission Strength'].default_value = 10.0
    except:
        pass
    obj.data.materials.append(mat)
    
    # Animate Rotation
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    obj.rotation_euler.z = math.radians(360 * (1 if i%2==0 else -1))
    obj.keyframe_insert(data_path="rotation_euler", frame=250)

# 3. CREATE REFLECTING WAVE RINGS
for i in range(10):
    bpy.ops.mesh.primitive_torus_add(major_radius=10, minor_radius=0.02, location=(0,0,0))
    ring = bpy.context.object
    ring.name = f"Wave_{i}"
    
    # Animate Scale (Pulse)
    ring.scale = (0.1, 0.1, 0.1)
    ring.keyframe_insert(data_path="scale", frame=(i * 20))
    ring.scale = (2, 2, 2)
    ring.keyframe_insert(data_path="scale", frame=(i * 20 + 50))
    ring.scale = (0.1, 0.1, 0.1) # Reflect back
    ring.keyframe_insert(data_path="scale", frame=(i * 20 + 100))

# 4. CINEMATIC VORTEX CAMERA
bpy.ops.object.camera_add(location=(20, 0, 10))
cam = bpy.context.object
bpy.context.scene.camera = cam

# Spiral Path
for f in range(1, 251, 10):
    angle = math.radians(f * 2)
    dist = 25 - (f * 0.05)
    cam.location.x = math.cos(angle) * dist
    cam.location.y = math.sin(angle) * dist
    cam.location.z = 10 + math.sin(f*0.1) * 5
    cam.keyframe_insert(data_path="location", frame=f)

# Point at Core
track = cam.constraints.new(type='TRACK_TO')
track.target = bpy.data.objects.get("Core_Layer_0")
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# 5. STARS
for _ in range(200):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(random.uniform(-100,100), random.uniform(-100,100), random.uniform(-100,100)))

# 6. DARK WORLD
if 'World' in bpy.data.worlds:
    bpy.data.worlds['World'].node_tree.nodes['Background'].inputs[0].default_value = (0, 0, 0, 1)
"""

print(send_blender_code(overhaul_code))
