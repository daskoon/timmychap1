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

# 1. Setup the Compositor for BLOOM (The "Secret Sauce" for Blender 5.0)
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
for node in tree.nodes:
    tree.nodes.remove(node)

render_layers = tree.nodes.new('CompositorNodeRLayers')
glare_node = tree.nodes.new('CompositorNodeGlare')
glare_node.glare_type = 'FOG_GLOW'
glare_node.size = 9
glare_node.threshold = 0.5

composite = tree.nodes.new('CompositorNodeComposite')

tree.links.new(render_layers.outputs['Image'], glare_node.inputs['Image'])
tree.links.new(glare_node.outputs['Image'], composite.inputs['Image'])

# 2. Refine Materials (Recursive Glass)
def polish_mat(name, color, emission_val):
    mat = bpy.data.materials.get(name)
    if mat:
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        # Lower base color brightness to let emission show through
        bsdf.inputs['Base Color'].default_value = [c * 0.1 for c in color[:3]] + [1.0]
        bsdf.inputs['Roughness'].default_value = 0.05
        bsdf.inputs['IOR'].default_value = 1.45
        bsdf.inputs['Transmission Weight'].default_value = 1.0
        bsdf.inputs['Emission Color'].default_value = color
        bsdf.inputs['Emission Strength'].default_value = emission_val
        mat.blend_method = 'HASHED' # High-end transparency

polish_mat('Glow_Blue', (0.0, 0.5, 1.0, 1.0), 10.0)
polish_mat('Glow_Gold', (1.0, 0.6, 0.0, 1.0), 8.0)

# 3. Add Volumetric Atmosphere (Mist)
bpy.ops.mesh.primitive_cube_add(size=100, location=(0,0,0))
vol = bpy.context.object
vol.name = "Atmosphere"
vol_mat = bpy.data.materials.new(name="Volume")
vol_mat.use_nodes = True
vol_nodes = vol_mat.node_tree.nodes
vol_nodes.remove(vol_nodes.get('Principled BSDF'))
v_scatter = vol_nodes.new('ShaderNodeVolumePrincipled')
v_scatter.inputs['Density'].default_value = 0.01
v_output = vol_nodes.get('Material Output')
vol_mat.node_tree.links.new(v_scatter.outputs['Volume'], v_output.inputs['Volume'])
vol.data.materials.append(vol_mat)

# 4. Cinematic Camera settings
cam = bpy.context.scene.camera
cam.data.dof.use_dof = True
cam.data.dof.focus_object = bpy.data.objects.get('Core_Layer_0')
cam.data.dof.aperture_fstop = 1.8 # Soft background blur
"""

print(send_blender_code(code))
