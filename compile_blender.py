from moviepy import ImageSequenceClip
import os

frames_dir = r'C:\Users\transmacsual\projects\timmy theroum\production\visuals\blender_frames'
output_dir = r'C:\Users\transmacsual\projects\timmy theroum\production\videos'
output_file = os.path.join(output_dir, 'blender_master_loop.mp4')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get sorted list of frames
frames = [os.path.join(frames_dir, f) for f in sorted(os.listdir(frames_dir)) if f.endswith('.png')]

print(f'Found {len(frames)} frames. Compiling video...')

# Create a clip from the sequence at 25 fps (10 seconds total)
clip = ImageSequenceClip(frames, fps=25)

print('Rendering master loop...')
clip.write_videofile(output_file, codec='libx264', fps=25)

print(f'DONE! Master loop saved to {output_file}')
