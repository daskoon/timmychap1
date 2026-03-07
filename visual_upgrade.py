import socket
import json

def send_blender_code(code):
    host = 'localhost'
    port = 9876
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(30)
            s.connect((host, port))
            payload = {"type": "execute_code", "params": {"code": code}}
            s.sendall(json.dumps(payload).encode('utf-8'))
            return s.recv(8192).decode('utf-8')
    except Exception as e:
        return str(e)

code = """
import bpy
import math

# 1. Setup Scene
scene = bpy.context.scene
for obj in bpy.data.objects:
    if 'Quantum_Core_Light' in obj.name or 'Main_Camera' in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

# 2. World Environment
world = bpy.context.scene.world
if world:
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    node_env = nodes.new('ShaderNodeTexEnvironment')
    for img in bpy.data.images:
        if 'studio_small_03' in img.name:
            node_env.image = img
            break
            
    node_mix = nodes.new('ShaderNodeMixShader')
    node_light_path = nodes.new('ShaderNodeLightPath')
    node_bg_hdri = nodes.new('ShaderNodeBackground')
    node_bg_black = nodes.new('ShaderNodeBackground')
    node_output = nodes.new('ShaderNodeOutputWorld')
    
    node_bg_black.inputs[0].default_value = (0, 0, 0, 1)
    
    links.new(node_env.outputs['Color'], node_bg_hdri.inputs['Color'])
    links.new(node_light_path.outputs['Is Camera Ray'], node_mix.inputs['Fac'])
    links.new(node_bg_hdri.outputs['Background'], node_mix.inputs[1])
    links.new(node_bg_black.outputs['Background'], node_mix.inputs[2])
    links.new(node_mix.outputs['Shader'], node_output.inputs['Surface'])

# 3. Materials
mat_metal = bpy.data.materials.new(name="DarkMetal_V3")
mat_metal.use_nodes = True
bsdf = mat_metal.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.1

for obj in bpy.data.objects:
    if obj.type == 'MESH' and ('brass' in obj.name.lower() or 'ring' in obj.name.lower() or 'base' in obj.name.lower()):
        obj.data.materials.clear()
        obj.data.materials.append(mat_metal)

# 4. Point Light
light_data = bpy.data.lights.new(name="Quantum_Core_Light", type='POINT')
light_data.energy = 2000
light_data.color = (0, 1, 1)
light_obj = bpy.data.objects.new(name="Quantum_Core_Light", object_data=light_data)
scene.collection.objects.link(light_obj)
light_obj.location = (0, 0, 0.5)

# 5. Camera
cam_data = bpy.data.cameras.new(name="Main_Camera")
cam_obj = bpy.data.objects.new(name="Main_Camera", object_data=cam_data)
scene.collection.objects.link(cam_obj)
cam_obj.location = (0, -4.5, 1)
cam_obj.rotation_euler = (math.radians(85), 0, 0)
scene.camera = cam_obj

cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 4.0
cam_data.dof.aperture_fstop = 1.2

# 6. Render Settings
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = 'C:/Users/transmacsual/projects/timmy theroum/production/visuals/ch1_master_upgrade.png'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

bpy.ops.render.render(write_still=True)
"""

print(send_blender_code(code))
