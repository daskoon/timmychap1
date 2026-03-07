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

code = """
import bpy
import math

# 1. Clean the slate
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Setup the proper Blender 5.0 Glowing Material
def create_glow_mat(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    
    # Base Color
    bsdf.inputs['Base Color'].default_value = color
    
    # EEVEE Next Glass/Glow settings
    bsdf.inputs['Roughness'].default_value = 0.1
    
    # Transmission (Glass)
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 1.0
    
    # Emission (Glow) - Using explicit names for 5.0 compatibility
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = color
    if 'Emission Strength' in bsdf.inputs:
        bsdf.inputs['Emission Strength'].default_value = 15.0
        
    mat.blend_method = 'BLEND'
    return mat

mat_blue = create_glow_mat('Glow_Blue', (0.0, 0.5, 1.0, 1.0))
mat_gold = create_glow_mat('Glow_Gold', (1.0, 0.7, 0.0, 1.0))

# 3. Create High-Res Smooth Cores
for i in range(3):
    # Use UV sphere for smoothness instead of jagged icosphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=(1 + i*0.5), location=(0, 0, 0))
    obj = bpy.context.object
    bpy.ops.object.shade_smooth() # Make it perfectly smooth
    obj.name = f"Core_Layer_{i}"
    
    obj.data.materials.append(mat_blue if i % 2 == 0 else mat_gold)
    
    # Animate Rotation
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    obj.rotation_euler.z = math.radians(360 * (1 if i%2==0 else -1))
    obj.keyframe_insert(data_path="rotation_euler", frame=250)

# 4. Create Thick, Glowing Wave Rings
for i in range(5): # Reduced count for better visual clarity
    bpy.ops.mesh.primitive_torus_add(major_radius=10, minor_radius=0.1, major_segments=64, minor_segments=16, location=(0,0,0))
    ring = bpy.context.object
    bpy.ops.object.shade_smooth()
    ring.name = f"Wave_{i}"
    ring.data.materials.append(mat_blue)
    
    # Animate Scale
    ring.scale = (0.1, 0.1, 0.1)
    ring.keyframe_insert(data_path="scale", frame=(i * 30))
    ring.scale = (2.5, 2.5, 2.5)
    ring.keyframe_insert(data_path="scale", frame=(i * 30 + 80))
    ring.scale = (0.1, 0.1, 0.1)
    ring.keyframe_insert(data_path="scale", frame=(i * 30 + 160))

# 5. Reset the Camera
bpy.ops.object.camera_add(location=(15, -15, 8))
cam = bpy.context.object
bpy.context.scene.camera = cam

# Simple tracking
track = cam.constraints.new(type='TRACK_TO')
track.target = bpy.data.objects.get("Core_Layer_0")
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# 6. Ensure true black background for glow to pop
if 'World' in bpy.data.worlds:
    bpy.data.worlds['World'].node_tree.nodes['Background'].inputs[0].default_value = (0, 0, 0, 1)

# Set view to camera and render mode
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_perspective = 'CAMERA'
                space.shading.type = 'RENDERED'
"""

print(send_blender_code(code))
