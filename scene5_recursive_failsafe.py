import bpy, math, random
from mathutils import Euler

def clear_scene(): bpy.ops.wm.read_factory_settings(use_empty=True)
def add_material(name, nodes_setup_func):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    nodes_setup_func(nodes, mat.node_tree.links)
    return mat

clear_scene()
scene = bpy.context.scene; scene.name = "Recursive_Failsafe"
scene.render.engine = 'CYCLES'

for i, R in enumerate([5,9,14,20]):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=0.2)
    ring = bpy.context.object; ring.name = f"Ring_{i+1}"
    red_mat = add_material(f"Red_{i}", lambda n,l: (
        emit := n.new('ShaderNodeEmission'),
        out := n.new('ShaderNodeOutputMaterial'),
        l.new(emit.outputs[0], out.inputs[0])
    ))
    red_mat.node_tree.nodes[0].inputs[1].default_value = 4.0
    ring.data.materials.append(red_mat)

bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=0.2)
eye = bpy.context.object; eye.name = "Eye_Iris"

bpy.ops.object.camera_add(location=(0,-10,2))
cam = bpy.context.object; cam.rotation_euler = (math.radians(10), 0, 0); scene.camera = cam
print("Scene 5 Built.")
