import bpy, math, random
from mathutils import Vector

def clear_scene(): bpy.ops.wm.read_factory_settings(use_empty=True)
def add_material(name, nodes_setup_func):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    nodes_setup_func(nodes, mat.node_tree.links)
    return mat

clear_scene()
scene = bpy.context.scene; scene.name = "Measurement_Cliffhanger"
scene.render.engine = 'CYCLES'

for i in range(10):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(random.uniform(-2,2), random.uniform(-2,2), random.uniform(-2,2)))
    sph = bpy.context.object; sph.name = f"Super_{i}"
    mat = add_material(f"Mat_{i}", lambda n,l: (
        emit := n.new('ShaderNodeEmission'),
        out := n.new('ShaderNodeOutputMaterial'),
        l.new(emit.outputs[0], out.inputs[0])
    ))
    sph.data.materials.append(mat)

bpy.ops.object.camera_add(location=(0, -150, 0))
cam = bpy.context.object; scene.camera = cam
for f in range(1, 301):
    cam.location.y = -150 + (f-1)*(150/300)
    cam.keyframe_insert(data_path="location", frame=f)

print("Scene 6 Built.")
