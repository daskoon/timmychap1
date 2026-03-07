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

# 1. Create a solid core inside the wireframe
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.9, segments=64, ring_count=32, location=(0, 0, 0))
inner_core = bpy.context.object
inner_core.name = "Solid_Inner_Core"
bpy.ops.object.shade_smooth()

# 2. Material: Intense Glowing Cyan
mat = bpy.data.materials.new(name="Intense_Glow")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF')
color = (0, 0.5, 1, 1)
bsdf.inputs['Base Color'].default_value = color
try:
    bsdf.inputs['Emission Color'].default_value = color
    bsdf.inputs['Emission Strength'].default_value = 30.0
except:
    pass
inner_core.data.materials.append(mat)

# 3. Parenting
outer_core = bpy.data.objects.get('Quantum_Core')
if outer_core:
    inner_core.parent = outer_core
"""

print(send_blender_code(code))
