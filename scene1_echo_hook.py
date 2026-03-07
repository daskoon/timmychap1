import bpy, math, random
from mathutils import Vector, Euler

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def make_collection(name):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll

def add_material(name, nodes_setup_func):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    nodes_setup_func(nodes, mat.node_tree.links)
    return mat

def set_keyframe(obj, data_path, frame, value, interpolation='LINEAR'):
    setattr(obj, data_path, value)
    obj.keyframe_insert(data_path=data_path, frame=frame)
    try:
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            fcurve = None
            if hasattr(action, "fcurves"): fcurve = action.fcurves.find(data_path)
            elif hasattr(action, "layers"):
                for layer in action.layers:
                    fcurve = layer.fcurves.find(data_path)
                    if fcurve: break
            if fcurve:
                for kp in fcurve.keyframe_points:
                    if abs(kp.co.x - frame) < 0.1:
                        kp.interpolation = interpolation
                        break
    except: pass

def setup_compositor(scene):
    scene.use_nodes = True
    nodes = scene.node_tree.nodes
    nodes.clear()
    rl = nodes.new('CompositorNodeRLayers')
    glare = nodes.new('CompositorNodeGlare')
    glare.glare_type = 'STREAKS'
    comp = nodes.new('CompositorNodeComposite')
    scene.node_tree.links.new(rl.outputs[0], glare.inputs[0])
    scene.node_tree.links.new(glare.outputs[0], comp.inputs[0])

clear_scene()
scene = bpy.context.scene
scene.name = "Echo_Hook"
scene.render.engine = 'CYCLES'
scene.cycles.samples = 512
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080

star_coll = make_collection("Stars")
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02)
star_proto = bpy.context.object
star_proto.name = "Star_Proto"
star_proto.hide_render = True
star_mat = add_material("Star_Emission", lambda n, l: (
    emit := n.new('ShaderNodeEmission'),
    out := n.new('ShaderNodeOutputMaterial'),
    l.new(emit.outputs[0], out.inputs[0])
))
star_proto.data.materials.append(star_mat)

bpy.ops.mesh.primitive_uv_sphere_add(radius=10000)
star_field = bpy.context.object
ps = star_field.modifiers.new(name="Stars_PS", type='PARTICLE_SYSTEM')
psettings = ps.particle_system.settings
psettings.count = 80000
psettings.frame_start = psettings.frame_end = 1
psettings.lifetime = 1000
psettings.render_type = 'OBJECT'
psettings.instance_object = star_proto
psettings.use_render_emitter = False

nebula_coll = make_collection("Nebula")
bpy.ops.mesh.primitive_cube_add(size=2000)
nebula = bpy.context.object
nebula_mat = add_material("Nebula_Fog_Mat", lambda n,l: (
    vol := n.new('ShaderNodeVolumePrincipled'),
    out := n.new('ShaderNodeOutputMaterial'),
    l.new(vol.outputs[0], out.inputs[1])
))
nebula_mat.node_tree.nodes[0].inputs["Emission Strength"].default_value = 0.03
nebula.data.materials.append(nebula_mat)

bpy.ops.mesh.primitive_torus_add(major_radius=0.0, minor_radius=0.015)
ring = bpy.context.object
ring_mat = add_material("Ring_Emission", lambda n,l: (
    emit := n.new('ShaderNodeEmission'),
    out := n.new('ShaderNodeOutputMaterial'),
    l.new(emit.outputs[0], out.inputs[0])
))
ring_mat.node_tree.nodes[0].inputs[1].default_value = 18.0
ring.data.materials.append(ring_mat)
set_keyframe(ring, "scale", 1, (0,0,0))
set_keyframe(ring, "scale", 130, (65, 65, 0))

bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,85))
grid = bpy.context.object
grid.rotation_euler = (math.radians(2), 0, 0)
grid_mat = add_material("Grid_Mat", lambda n,l: (
    emit := n.new('ShaderNodeEmission'),
    out := n.new('ShaderNodeOutputMaterial'),
    l.new(emit.outputs[0], out.inputs[0])
))
grid.data.materials.append(grid_mat)
grid_emit = grid_mat.node_tree.nodes[0]
for f in range(1, 271, 5):
    val = 1.25 + 0.25*math.sin(2*math.pi*(f%90)/90)
    grid_emit.inputs[1].default_value = val
    grid_emit.inputs[1].keyframe_insert(data_path="default_value", frame=f)

bpy.ops.object.camera_add(location=(0, -200, -200))
cam = bpy.context.object
cam.data.lens = 35
cam.rotation_euler = (math.radians(8), 0, 0)
for f in range(1, 271):
    dz = (0.15 * (f-1)) * min(1, (f-1)/210)
    cam.location.z = -200 + dz
    cam.keyframe_insert(data_path="location", frame=f)

setup_compositor(scene)
print("Scene 1 Built.")
