import socket
import json

def send_blender_code(code):
    host = 'localhost'
    port = 9876
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(20)
            s.connect((host, port))
            payload = {"type": "execute_code", "params": {"code": code}}
            s.sendall(json.dumps(payload).encode('utf-8'))
            return s.recv(8192).decode('utf-8')
    except Exception as e:
        return str(e)

code = """
import bpy
import math

# 1. CLEANUP
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. CREATE THE QUANTUM CRYSTAL CORE
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=2, location=(0, 0, 0))
core = bpy.context.object
core.name = "Quantum_Core"

# Add Wireframe for technical look
wire = core.modifiers.new(name="Wire", type='WIREFRAME')
wire.thickness = 0.05

# Material: Glowing Neon Cyan
mat = bpy.data.materials.new(name="Neon_Cyan")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get('Principled BSDF')
bsdf.inputs[0].default_value = (0, 0.8, 1, 1) # Base
try:
    bsdf.inputs['Emission Color'].default_value = (0, 0.5, 1, 1)
    bsdf.inputs['Emission Strength'].default_value = 10.0
except:
    pass
core.data.materials.append(mat)

# 3. INTERNAL LIGHT
bpy.ops.object.light_add(type='POINT', radius=1, location=(0, 0, 0))
light = bpy.context.object
light.data.color = (0, 0.5, 1)
light.data.energy = 500

# 4. PULSING WAVE RINGS
for i in range(5):
    bpy.ops.mesh.primitive_torus_add(major_radius=10, minor_radius=0.05, location=(0,0,0))
    ring = bpy.context.object
    ring.name = f"Wave_{i}"
    ring.data.materials.append(mat)
    ring.rotation_euler = (math.radians(45), math.radians(i*30), 0)
    
    # Animate Scale
    ring.scale = (0.1, 0.1, 0.1)
    ring.keyframe_insert(data_path="scale", frame=(i * 40))
    ring.scale = (3, 3, 3)
    ring.keyframe_insert(data_path="scale", frame=(i * 40 + 60))
    ring.scale = (0.1, 0.1, 0.1)
    ring.keyframe_insert(data_path="scale", frame=(i * 40 + 120))

# 5. CAMERA FLY-BY
bpy.ops.object.camera_add(location=(15, -15, 10))
cam = bpy.context.object
bpy.context.scene.camera = cam
cam.location = (5, -5, 3)
cam.keyframe_insert(data_path="location", frame=1)
cam.location = (25, -25, 15)
cam.keyframe_insert(data_path="location", frame=250)

track = cam.constraints.new(type='TRACK_TO')
track.target = core
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# 6. BLACK SPACE
if 'World' in bpy.data.worlds:
    bpy.data.worlds['World'].node_tree.nodes['Background'].inputs[0].default_value = (0, 0, 0, 1)
"""

print(send_blender_code(code))
