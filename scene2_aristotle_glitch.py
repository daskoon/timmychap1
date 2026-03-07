import bpy, math, random
from mathutils import Euler

def clear_scene(): bpy.ops.wm.read_factory_settings(use_empty=True)
def add_material(name, nodes_setup_func):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    nodes_setup_func(nodes, mat.node_tree.links)
    return mat
def setup_compositor(scene):
    scene.use_nodes = True; nodes = scene.node_tree.nodes; nodes.clear()
    rl = nodes.new('CompositorNodeRLayers'); comp = nodes.new('CompositorNodeComposite')
    glare = nodes.new('CompositorNodeGlare'); glare.glare_type = 'STREAKS'
    scene.node_tree.links.new(rl.outputs[0], glare.inputs[0])
    scene.node_tree.links.new(glare.outputs[0], comp.inputs[0])

clear_scene()
scene = bpy.context.scene; scene.name = "Aristotle_Glitch"
scene.render.engine = 'CYCLES'; scene.cycles.samples = 512

scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0,0,0,1)

bpy.ops.object.light_add(type='AREA', location=(-5,5,5))
bpy.context.object.data.energy = 400

bpy.ops.mesh.primitive_uv_sphere_add(radius=1)
bust = bpy.context.object
marble_mat = add_material("Marble_Mat", lambda n,l: (
    bsdf := n.new('ShaderNodeBsdfPrincipled'),
    out := n.new('ShaderNodeOutputMaterial'),
    l.new(bsdf.outputs[0], out.inputs[0])
))
bsdf = marble_mat.node_tree.nodes[0]
bsdf.inputs["Base Color"].default_value = (0.94,0.92,0.89,1)
bsdf.inputs["Subsurface Weight"].default_value = 0.08
bsdf.inputs["Specular IOR Level"].default_value = 0.6
bsdf.inputs["Roughness"].default_value = 0.15
bust.data.materials.append(marble_mat)

bpy.ops.mesh.primitive_plane_add(size=2)
line = bpy.context.object; line.scale = (1, 0.0025, 1); line.location.z = 0.5
scan_mat = add_material("ScanLine_Mat", lambda n,l: (
    emit := n.new('ShaderNodeEmission'),
    out := n.new('ShaderNodeOutputMaterial'),
    l.new(emit.outputs[0], out.inputs[0])
))
scan_mat.node_tree.nodes[0].inputs[1].default_value = 25.0
line.data.materials.append(scan_mat)

for f in range(1, 241):
    t = min(1.0, (f-1)/80.0)
    line.location.y = 0.5 - t + random.uniform(-0.02, 0.02)
    line.keyframe_insert(data_path="location", frame=f)

bpy.ops.object.camera_add(location=(0,-2,0.2))
cam = bpy.context.object; cam.rotation_euler = (math.radians(10), 0, 0); scene.camera = cam
setup_compositor(scene)
print("Scene 2 Built.")
