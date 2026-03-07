import asyncio
import edge_tts
import os

# Script for the first 2 minutes, split for variable pacing
sections = [
    # Hank Green Hook: Fast, energetic
    {'text': 'Okay, so... we need to talk about the fact that the universe is basically a giant developer oversight.', 'rate': '+15%'},
    {'text': 'Think about it. On one hand, space is infinite. No edge, no walls, just... everything... forever.', 'rate': '+5%'},
    {'text': 'But on the other hand, everything inside that infinite space is behaving like it’s stuck in a very strict, very finite rulebook.', 'rate': '+10%'},
    # Michael Reeves Analogy: Fast, conversational
    {'text': 'Electrons have a speed limit. Energy can’t just vanish into the void. It’s like being in a massive open-world game with no boundaries, but for some reason, you’re still limited by a level-10 stamina bar.', 'rate': '+15%'},
    # Neil deGrasse Tyson Moment: Slow, thoughtful
    {'text': 'Why? Why hasn’t the whole thing just... dissolved into a giant puddle of cosmic soup?', 'rate': '-5%'},
    {'text': 'If there’s nothing at the end of the universe to keep things in check, what is stopping the chaos from just taking over?', 'rate': '+0%'},
    # The Reveal
    {'text': 'Well, we are diving into a framework today that actually has an answer.', 'rate': '+10%'},
    {'text': 'It suggest that the universe isn’t just a collection of random stuff—it’s a self-regulating system that uses physical law and consciousness to keep itself from exploding.', 'rate': '+5%'},
    # The Aristotle Glitch (Wizard Vibe)
    {'text': 'This isn’t a new problem. Even the ancients were stressing about this. Aristotle looked at the stars and basically asked: How can you have infinite space and finite order at the same time?', 'rate': '+5%'},
    {'text': 'See, if the universe is truly boundless, what’s stopping an infinite amount of energy from just... transferring everywhere at once?', 'rate': '+10%'}
]

async def build():
    full_audio_path = 'production/audio/dna_test_v2.mp3'
    # For this test, I will join them with pauses manually in the final video
    # But for simplicity, I'll generate one long file with pauses
    all_text = ""
    for s in sections:
        # Pacing: using commas and periods for natural edge-tts pausing
        all_text += s['text'] + " ... "
    
    communicate = edge_tts.Communicate(all_text, 'en-US-AvaNeural', rate='+5%')
    await communicate.save(full_audio_path)
    print(f"Audio generated: {full_audio_path}")

if __name__ == '__main__':
    asyncio.run(build())
