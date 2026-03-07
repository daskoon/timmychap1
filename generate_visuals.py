import requests
import io
from PIL import Image
import time
import os

API_URL = 'https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell'
headers = {'Authorization': 'Bearer YOUR_HF_TOKEN_HERE'}

prompts = [
    'Wide cinematic shot of an infinite starry cosmos with subtle digital scanline artifacts, purple and gold glow.',
    'A high-end 3D HUD overlay showing a Stamina Bar at 10% hovering in deep space over a black hole.',
    'A messy workbench covered in copper wires, glowing crystals, and a laptop showing quantum wave simulations.',
    'A marble classical column in space shattering into glowing golden cubes and mathematical formulas.',
    'A split screen: left is a chaotic static noise, right is a perfectly ordered crystal lattice of light.',
    'An ancient scroll with glowing blue circuit traces drawn on it, floating in a vacuum.',
    'A beam of light hitting an invisible wall and rippling like water in 3D space.',
    'Hyper-detailed close up of a circuit board where the traces are made of flowing liquid starlight.',
    'A glowing blue Causal Horizon bubble surrounding a tiny earth-like planet in a vast dark void.',
    'A human brain silhouette where the neurons are glowing golden quantum field lines.'
]

if not os.path.exists('production/visuals'):
    os.makedirs('production/visuals')

for i, p in enumerate(prompts):
    print(f'Generating Visual {i+1}...')
    try:
        response = requests.post(API_URL, headers=headers, json={'inputs': p})
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            img.save(f'production/visuals/dna_test_{i+1}.png')
            time.sleep(1)
        else:
            print(f'Visual {i+1} failed with status {response.status_code}')
    except Exception as e:
        print(f'Visual {i+1} error: {e}')
