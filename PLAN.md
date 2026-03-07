# Project Plan: Timothy V. Lanno - YouTube Series Production

## Overview
Automated production of a 6-episode YouTube series based on the thesis "Cosmic Regulation Through Consciousness."

---

## Phase 0: Pre-Flight Validation (CRITICAL)
*Objective: Verify hardware stability and asset quality before starting long renders.*

- [ ] **Stress Test:** Render Frame 1 of `scene1_echo_hook.py` (80k particles) to estimate total render time.
- [ ] **Scene Integrity Check:** Verify `scene5_recursive_failsafe.py` blink logic works in viewport.
- [ ] **Audio Benchmark:** Generate 30s of "Hank Green Pacing" audio via `build_audio_v2.py` and verify against "Jessica DNA" requirement.
- [ ] **Engine Toggle:** Use EEVEE for rapid iteration and CYCLES only for final pass.

---

## 1. Episode 1 (Chapter 1) - "The Echo Hook"
**Status:** Reconstruction Complete (All 6 scenes verified).

### Phase 1: Scene Execution
- [ ] `scene1_echo_hook.py`
- [ ] `scene2_aristotle_glitch.py`
- [ ] `scene3_natural_cage.py`
- [ ] `scene4_causal_firewall.py`
- [ ] `scene5_recursive_failsafe.py`
- [ ] `scene6_measurement_cliffhanger.py`

### Phase 2: Audio Production
- [ ] **Draft Audio:** Edge-TTS/Kokoro.
- [ ] **Pacing Engine:** Hank Green logic sync.
- [ ] **Credit Approval:** Final TwelveLabs pass (169 remaining).

### Phase 3: Assembly
- [ ] Merge FLUX overlays (`generate_visuals.py`).
- [ ] VFX Polish (`vfx_polish.py`).
- [ ] Final MP4 Render.

---

## 2. Full Series Roadmap (Chapters 2-6)
*Refer to original PLAN.md for chapter themes.*

## 3. Immediate Technical Task
Execute: `& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --background --python scene1_echo_hook.py --frame-start 1 --frame-end 1`
