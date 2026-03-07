import socket
import json

def send_blender_code(code):
    host = 'localhost'
    port = 9876
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((host, port))
            payload = {
                "type": "execute_code",
                "params": {"code": code}
            }
            s.sendall(json.dumps(payload).encode('utf-8'))
            response = s.recv(4096).decode('utf-8')
            return json.loads(response)
    except Exception as e:
        return {"status": "error", "message": str(e)}

# The Blender Python code to build our scene
blender_code = """
import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create Causal Horizon Sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=5, location=(0, 0, 0))
sphere = bpy.context.object
sphere.name = "Causal_Horizon"

# Create a glowing material
mat = bpy.data.materials.new(name="Causal_Glow")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Get the Principled BSDF node
bsdf = nodes.get("Principled BSDF")

# Set Emission (Using index for compatibility with different Blender versions)
# In Blender 4.0+, Emission is a separate color and strength
if bsdf:
    # Try 4.0+ style first
    try:
        bsdf.inputs['Emission Color'].default_value = (0, 0.5, 1, 1) # Cyan
        bsdf.inputs['Emission Strength'].default_value = 5.0
    except:
        # Fallback for older versions
        bsdf.inputs['Emission'].default_value = (0, 0.5, 1, 1)
        bsdf.inputs['Emission Strength'].default_value = 5.0

sphere.data.materials.append(mat)

# Add a camera
bpy.ops.object.camera_add(location=(15, -15, 10), rotation=(1.1, 0, 0.78))
bpy.context.scene.camera = bpy.context.object

# Add a light
bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
"""

result = send_blender_code(blender_code)
print(json.dumps(result, indent=2))
