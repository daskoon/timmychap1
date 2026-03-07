import os
import subprocess

ffmpeg_path = r'C:\Users\transmacsual\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe'
temp_dir = r'C:\Users\transmacsual\projects\timmy theroum\production\temp_clips'
audio_file = r'C:\Users\transmacsual\projects\timmy theroum\production\audio\ch1_full_timed_draft.mp3'
output_file = r'C:\Users\transmacsual\projects\timmy theroum\production\chapter1_cinematic_draft.mp4'

# Fixing the list file
list_path = os.path.join(temp_dir, 'clips.txt')
with open(list_path, 'w') as f:
    for i in range(10):
        f.write(f"file 'clip_{i}.mp4'\n")

print('Merging clips with audio...')
os.chdir(temp_dir)
cmd_final = f'"{ffmpeg_path}" -f concat -safe 0 -i clips.txt -i "{audio_file}" -c:v copy -c:a aac -shortest "{output_file}" -y'
subprocess.run(cmd_final, shell=True)
print('DONE!')
