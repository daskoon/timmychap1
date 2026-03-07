from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import os

visuals_dir = r'C:\Users\transmacsual\projects\timmy theroum\production\visuals'
audio_file = r'C:\Users\transmacsual\projects\timmy theroum\production\audio\dna_test_v2.mp3'
output_file = r'C:\Users\transmacsual\projects\timmy theroum\production\dna_vibe_check.mp4'

audio = AudioFileClip(audio_file)
audio_duration = audio.duration
print(f'Audio duration: {audio_duration} seconds.')

num_images = 10
duration_per_image = audio_duration / num_images

clips = []
for i in range(1, num_images + 1):
    img_path = os.path.join(visuals_dir, f'dna_test_{i}.png')
    print(f'Processing Shot {i}/{num_images}...')
    
    clip = ImageClip(img_path).with_duration(duration_per_image).with_fps(24)
    # Slow zoom-in effect
    clip = clip.resized(lambda t: 1 + 0.04 * t / duration_per_image)
    clips.append(clip)

print('Combining shots...')
video = concatenate_videoclips(clips, method='chain')
video = video.with_audio(audio)

print('Rendering final Vibe Check...')
video.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=24)

print(f'DONE! Vibe Check produced at: {output_file}')
