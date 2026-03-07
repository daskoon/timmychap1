import asyncio
import edge_tts
import os
import subprocess

ALARM_AUDIO = r"C:\Users\transmacsual\projects\timmy theroum\production\audio\alarm.mp3"

async def generate_alarm():
    if not os.path.exists(ALARM_AUDIO):
        print("Generating emergency alarm audio...")
        communicate = edge_tts.Communicate("Attention. Someone tell skoon there is a problem with my A I. I am stuck.", "en-US-EmmaNeural", rate="-10%", volume="+50%")
        await communicate.save(ALARM_AUDIO)
        print("Alarm audio generated.")

def play_alarm():
    print("PLAYING ALARM...")
    wmp_path = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"
    if os.path.exists(wmp_path):
        subprocess.Popen([wmp_path, ALARM_AUDIO])
    else:
        # Fallback to default system player
        os.startfile(ALARM_AUDIO)

if __name__ == '__main__':
    asyncio.run(generate_alarm())
    # We won't play it right now, this script will be called by my other scripts if they fail.
    print("Alarm system primed and ready.")
