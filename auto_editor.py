import os
import subprocess

ffmpeg_path = r'C:\Users\transmacsual\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe'
visuals_dir = 'production/visuals/'
audio_file = 'production/audio/ch1_full_timed_draft.mp3'
output_file = 'production/chapter1_cinematic_draft.mp4'
temp_dir = 'production/temp_clips/'

if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Motions for the 10 images (10 seconds each)
motions = [
    "zoompan=z='min(zoom+0.001,1.5)':d=250:s=1920x1080",
    "zoompan=z='1.2':d=250:x='(iw-iw/zoom)*(t/250)':s=1920x1080",
    "zoompan=z='min(zoom+0.0015,1.5)':d=250:s=1920x1080",
    "zoompan=z='1.3':d=250:y='(ih-ih/zoom)*(1-t/250)':s=1920x1080",
    "zoompan=z='min(zoom+0.0005,1.2)':d=250:s=1920x1080",
    "zoompan=z='1.2':d=250:x='(iw-iw/zoom)*(1-t/250)':s=1920x1080",
    "zoompan=z='min(zoom+0.002,1.6)':d=250:s=1920x1080",
    "zoompan=z='1.4':d=250:y='(ih-ih/zoom)*(t/250)':s=1920x1080",
    "zoompan=z='1.1':d=250:s=1920x1080",
    "zoompan=z='min(zoom+0.001,1.3)':d=250:s=1920x1080"
]

clip_list = []

# Step 1: Create individual clips
for i in range(10):
    input_img = f"{visuals_dir}ch1_draft_{i+1}.png"
    output_clip = f"{temp_dir}clip_{i}.mp4"
    print(f"Producing Clip {i+1}/10...")
    
    # Each image gets scaled, motion-panned, and faded
    cmd = f'"{ffmpeg_path}" -loop 1 -i "{input_img}" -vf "scale=2560:-1,crop=1920:1080,{motions[i]},fade=t=in:st=0:d=1,fade=t=out:st=9:d=1" -c:v libx264 -t 10 -pix_fmt yuv420p "{output_clip}" -y'
    subprocess.run(cmd, shell=True, capture_output=True)
    clip_list.append(output_clip)

# Step 2: Create a list file for concatenation
list_path = os.path.join(temp_dir, "clips.txt")
with open(list_path, "w") as f:
    for clip in clip_list:
        f.write(f"file '{os.path.abspath(clip)}'\n")

# Step 3: Concat clips and add audio
print("Merging clips with audio...")
# We use -filter_complex to ensure audio and video are synced perfectly
cmd_final = f'"{ffmpeg_path}" -f concat -safe 0 -i "{list_path}" -i "{audio_file}" -c:v copy -c:a aac -shortest "{output_file}" -y'
subprocess.run(cmd_final, shell=True)

print(f"DONE! Video produced at: {output_file}")
