from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import os

visuals_dir = r'C:\Users\transmacsual\projects\timmy theroum\production\visuals'
audio_file = r'C:\Users\transmacsual\projects\timmy theroum\production\audio\ch1_full_timed_draft.mp3'
output_file = r'C:\Users\transmacsual\projects\timmy theroum\production\moviepy_test.mp4'

clips = []
# Rendering 6 images, 20 seconds each
for i in range(1, 7):
    img_path = os.path.join(visuals_dir, f'test_v2_{i}.png')
    print(f'Processing Image {i}...')
    
    # Create simple 20 second clip
    clip = ImageClip(img_path).with_duration(20).with_fps(24)
    clips.append(clip)

print('Combining clips...')
# Method 'chain' is the simplest way to join clips
video = concatenate_videoclips(clips, method='chain')

print('Adding audio...')
audio = AudioFileClip(audio_file).subclipped(0, 120) # First 2 minutes
video = video.with_audio(audio)

print('Rendering final video (this may take a minute)...')
video.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=24)

print(f'DONE! Video produced at: {output_file}')
