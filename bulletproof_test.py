import os
import subprocess
import time

ffmpeg_path = r'C:\Users\transmacsual\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe'
visuals_dir = r'C:\Users\transmacsual\projects\timmy theroum\production\visuals'
audio_file = r'C:\Users\transmacsual\projects\timmy theroum\production\audio\ch1_full_timed_draft.mp3'
output_file = r'C:\Users\transmacsual\projects\timmy theroum\production\short_test_v2.mp4'
temp_dir = r'C:\Users\transmacsual\projects\timmy theroum\production\temp_test'

if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

motions = [
    "zoompan=z='min(zoom+0.0005,1.2)':d=500:s=1920x1080",
    "zoompan=z='1.2':d=500:x='(iw-iw/zoom)*(t/500)':s=1920x1080",
    "zoompan=z='min(zoom+0.001,1.5)':d=500:s=1920x1080",
    "zoompan=z='1.3':d=500:y='(ih-ih/zoom)*(1-t/500)':s=1920x1080",
    "zoompan=z='min(zoom+0.0008,1.3)':d=500:s=1920x1080",
    "zoompan=z='1.2':d=500:x='(iw-iw/zoom)*(1-t/500)':s=1920x1080"
]

clip_list = []

for i in range(6):
    input_img = os.path.join(visuals_dir, f"test_v2_{i+1}.png")
    output_clip = os.path.join(temp_dir, f"shot_{i}.mp4")
    print(f"Rendering Shot {i+1}/6...")
    cmd = f'"{ffmpeg_path}" -loop 1 -i "{input_img}" -vf "scale=2560:-1,crop=1920:1080,{motions[i]},fade=t=in:st=0:d=1,fade=t=out:st=19:d=1" -c:v libx264 -t 20 -pix_fmt yuv420p "{output_clip}" -y'
    subprocess.run(cmd, shell=True)
    clip_list.append(output_clip)

print("Waiting for file handles to release...")
time.sleep(3)

list_path = os.path.join(temp_dir, "list.txt")
with open(list_path, "w") as f:
    for clip in clip_list:
        # Use forward slashes and full paths for maximum compatibility
        p = os.path.abspath(clip).replace("\\", "/")
        f.write(f"file '{p}'\n")

print("Step 2: Merging shots into a 2-minute master...")
# Using full absolute path for audio too
audio_p = audio_file.replace("\\", "/")
out_p = output_file.replace("\\", "/")
cmd_merge = f'"{ffmpeg_path}" -f concat -safe 0 -i "{list_path}" -i "{audio_p}" -c:v copy -c:a aac -shortest "{out_p}" -y'
subprocess.run(cmd_merge, shell=True)

print(f"DONE! Test video produced at: {output_file}")
