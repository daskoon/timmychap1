import bpy, math, random
from mathutils import Euler

def clear_scene(): bpy.ops.wm.read_factory_settings(use_empty=True)
def add_material(name, nodes_setup_func):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    nodes_setup_func(nodes, mat.node_tree.links)
    return mat

def set_keyframe(obj, data_path, frame, value, interpolation='LINEAR'):
    setattr(obj, data_path, value)
    obj.keyframe_insert(data_path=data_path, frame=frame)
    try:
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            # Blender 5.0 slotted animation support
            if hasattr(action, "layers"):
                for layer in action.layers:
                    fcurve = layer.fcurves.find(data_path)
                    if fcurve:
                        for kp in fcurve.keyframe_points:
                            if abs(kp.co.x - frame) < 0.1: kp.interpolation = interpolation; break
    except: pass

clear_scene()
scene = bpy.context.scene; scene.name = "Recursive_Failsafe"
scene.render.engine = 'CYCLES'

# 1️⃣ Rings
rings = []
for i, R in enumerate([5,9,14,20]):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=0.2)
    ring = bpy.context.object; ring.name = f"Ring_{i+1}"
    rings.append(ring)
    mat = add_material(f"RingMat_{i}", lambda n,l: (
        emit := n.new('ShaderNodeEmission'),
        out := n.new('ShaderNodeOutputMaterial'),
        l.new(emit.outputs[0], out.inputs[0])
    ))
    ring.data.materials.append(mat)
    emit = mat.node_tree.nodes[0]
    emit.inputs[0].default_value = (0.8, 0.07, 0.0, 1) # Chaotic Red
    emit.inputs[1].default_value = 4.0

# 2️⃣ Eye Iris & Blink
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=0.2)
eye = bpy.context.object; eye.name = "Eye_Iris"

# Blink Elements (Using Scale for robust animation)
blinkers = []
for i in range(2):
    bpy.ops.mesh.primitive_plane_add(size=3)
    b = bpy.context.object; b.name = f"Blinker_{i}"
    b.location.z = 0.2; b.rotation_euler.x = math.radians(90 if i==0 else -90)
    # Add dark material
    b.data.materials.append(add_material(f"BlinkMat_{i}", lambda n,l: (
        n.new('ShaderNodeBsdfDiffuse').inputs[0].default_value = (0.01, 0.01, 0.01, 1)
    )))
    blinkers.append(b)

# Blink Animation logic
for f in range(1, 600, 60):
    for b in blinkers:
        set_keyframe(b, "scale", f, (1, 1, 1))
        set_keyframe(b, "scale", f+8, (1, 0.01, 1)) # Close
        set_keyframe(b, "scale", f+16, (1, 1, 1)) # Open

# 3️⃣ Red -> Blue Cascade (on frame 120)
for i, ring in enumerate(rings):
    start_f = 120 + (i * 8)
    mat = ring.data.materials[0]
    emit = mat.node_tree.nodes[0]
    # Keyframe via NodeTree for reliability in 5.0
    emit.inputs[0].default_value = (0.8, 0.07, 0.0, 1)
    mat.node_tree.keyframe_insert(data_path=f'nodes["{emit.name}"].inputs[0].default_value', frame=start_f)
    emit.inputs[0].default_value = (0.0, 0.33, 1.0, 1) # Stable Blue
    mat.node_tree.keyframe_insert(data_path=f'nodes["{emit.name}"].inputs[0].default_value', frame=start_f + 20)

bpy.ops.object.camera_add(location=(0,-15,5))
cam = bpy.context.object; cam.rotation_euler = (math.radians(15), 0, 0); scene.camera = cam
print("Scene 5 Fixed and Ready.")
