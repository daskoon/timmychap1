import bpy, math
from mathutils import Euler

def clear_scene(): bpy.ops.wm.read_factory_settings(use_empty=True)
def add_material(name, nodes_setup_func):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    nodes_setup_func(nodes, mat.node_tree.links)
    return mat

clear_scene()
scene = bpy.context.scene; scene.name = "Natural_Cage"
scene.render.engine = 'CYCLES'

for x in (-20, 20):
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x,0,0))
    pillar = bpy.context.object; pillar.scale = (1,1,25)
    gold_mat = add_material(f"Gold_{x}", lambda n,l: (
        bsdf := n.new('ShaderNodeBsdfPrincipled'),
        out := n.new('ShaderNodeOutputMaterial'),
        l.new(bsdf.outputs[0], out.inputs[0])
    ))
    bsdf = gold_mat.node_tree.nodes[0]
    bsdf.inputs["Base Color"].default_value = (0.83,0.63,0.09,1)
    bsdf.inputs["Metallic"].default_value = 1.0
    if "Anisotropy" in bsdf.inputs: bsdf.inputs["Anisotropy"].default_value = 0.3
    pillar.data.materials.append(gold_mat)
    pillar.location.z = 200
    pillar.keyframe_insert(data_path="location", frame=1)
    pillar.location.z = 0
    pillar.keyframe_insert(data_path="location", frame=18)

bpy.ops.object.camera_add(location=(0,-150,30))
cam = bpy.context.object; cam.rotation_euler = (math.radians(20), 0, 0); scene.camera = cam
print("Scene 3 Built.")
