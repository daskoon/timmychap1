import bpy, math
from mathutils import Euler

def clear_scene(): bpy.ops.wm.read_factory_settings(use_empty=True)
def add_material(name, nodes_setup_func):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    nodes_setup_func(nodes, mat.node_tree.links)
    return mat

clear_scene()
scene = bpy.context.scene; scene.name = "Causal_Firewall"
scene.render.engine = 'CYCLES'

bpy.ops.mesh.primitive_uv_sphere_add(radius=3)
earth = bpy.context.object; earth.name = "Earth_Core"
earth_mat = add_material("Earth_Mat", lambda n,l: (
    bsdf := n.new('ShaderNodeBsdfPrincipled'),
    out := n.new('ShaderNodeOutputMaterial'),
    l.new(bsdf.outputs[0], out.inputs[0])
))
earth.data.materials.append(earth_mat)

bpy.ops.mesh.primitive_uv_sphere_add(radius=18)
shell = bpy.context.object; shell.name = "Light_Shell"
shell_mat = add_material("Shell_Mat", lambda n,l: (
    emit := n.new('ShaderNodeEmission'),
    out := n.new('ShaderNodeOutputMaterial'),
    l.new(emit.outputs[0], out.inputs[0])
))
shell_mat.node_tree.nodes[0].inputs[1].default_value = 120.0
shell.data.materials.append(shell_mat)
shell_emit = shell_mat.node_tree.nodes[0]
for f in range(1, 301, 5):
    strength = 100 + 20*math.sin(2*math.pi*(f%30)/30)
    shell_emit.inputs[1].default_value = strength
    shell_emit.inputs[1].keyframe_insert(data_path="default_value", frame=f)

bpy.ops.object.camera_add(location=(0,0,-5))
cam = bpy.context.object; cam.name = "Cam_Firewall"
for f in range(1, 151):
    cam.location.z = -5 - f*0.1
    cam.keyframe_insert(data_path="location", frame=f)

print("Scene 4 Built.")
