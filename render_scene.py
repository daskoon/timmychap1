import bpy
import bmesh
import math

# ==========================================================
# 1. SCENE CLEANUP & ENGINE SETUP
# ==========================================================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128 # Higher for final, 128 for CLI speed
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'

# ==========================================================
# 2. THE QUANTUM CORE (Central Light Source)
# ==========================================================
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
core = bpy.context.active_object
core.name = "Quantum_Core"

core_mat = bpy.data.materials.new(name="Core_Glow")
core_mat.use_nodes = True
nodes = core_mat.node_tree.nodes
nodes.clear()

# Emission Node for that blinding Cyan
node_emission = nodes.new(type='ShaderNodeEmission')
node_emission.inputs[0].default_value = (0.0, 0.8, 1.0, 1.0) # Cyan
node_emission.inputs[1].default_value = 50.0 # Intensity

node_output = nodes.new(type='ShaderNodeOutputMaterial')
core_mat.node_tree.links.new(node_emission.outputs[0], node_output.inputs[0])
core.data.materials.append(core_mat)

# ==========================================================
# 3. THE "CAGES" (Geometric Ring Structure)
# ==========================================================
def create_cage(name, radius, thickness, rotation_speed):
    # Using standard primitive_torus_add parameters
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(0,0,0), 
                                     major_radius=radius, minor_radius=thickness)
    ring = bpy.context.active_object
    ring.name = name
    
    # Material: Dark Brushed Metal
    mat = bpy.data.materials.new(name=f"Metal_{name}")
    mat.use_nodes = True
    m_nodes = mat.node_tree.nodes
    bsdf = m_nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1) # Near black
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.2
    ring.data.materials.append(mat)
    
    # Animation: Harmonic Rotation
    ring.rotation_mode = 'XYZ'
    ring.keyframe_insert(data_path="rotation_euler", frame=1)
    ring.rotation_euler.x = math.radians(360) * rotation_speed
    ring.keyframe_insert(data_path="rotation_euler", frame=250)
    
    return ring

# Build nested layers
create_cage("Inner_Cage", 2.5, 0.05, 1.0)
create_cage("Mid_Cage", 3.5, 0.08, -0.5)
create_cage("Outer_Cage", 5.0, 0.12, 0.2)

# ==========================================================
# 4. CAMERA & MACRO DEPTH OF FIELD
# ==========================================================
bpy.ops.object.camera_add(location=(12, -12, 8), rotation=(math.radians(60), 0, math.radians(45)))
cam = bpy.context.active_object
scene.camera = cam
cam.data.lens = 85 # Macro lens focal length

# Shallow DOF setup
cam.data.dof.use_dof = True
cam.data.dof.focus_object = core
cam.data.dof.aperture_fstop = 1.8 # Blurs the background rings

# ==========================================================
# 5. LIGHTING (Void Setup)
# ==========================================================
if "World" in bpy.data.worlds:
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

print("Scene construction complete. Ready for CLI Render.")
