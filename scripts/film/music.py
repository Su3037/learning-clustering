"""Original ambient score, synthesised with NumPy (no samples, no third-party music).
Slow minor-key pad, a soft low pulse, and a quiet bell on each scene cue. The level stays low
(about −24 dBFS RMS) so it never competes with reading; the film has no voice-over.
Licence: part of this course's original media (CC BY 4.0, confirmed by the author 2026-10-23).
"""
import wave
import numpy as np

SR = 48000
# A minor → F → C → G (and a variant per film via `mood`), each chord 8 s.
PROGRESSIONS = {
    "calm": [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)],
    "curious": [(57, 60, 64), (55, 59, 62), (53, 57, 60), (52, 55, 59)],
    "steady": [(50, 53, 57), (55, 58, 62), (53, 57, 60), (48, 52, 55)],
}


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def pad(duration, mood="calm", seed=7):
    rng = np.random.default_rng(seed)
    n = int(duration * SR)
    t = np.arange(n) / SR
    prog = PROGRESSIONS.get(mood, PROGRESSIONS["calm"])
    chord_len = 8.0
    out = np.zeros(n)
    for ci in range(int(np.ceil(duration / chord_len)) + 1):
        start, end = ci * chord_len, (ci + 1) * chord_len + 2.0
        a, b = int(start * SR), min(n, int(end * SR))
        if a >= n:
            break
        seg_t = t[a:b] - start
        env = np.clip(seg_t / 2.5, 0, 1) * np.clip((end - start - seg_t) / 2.5, 0, 1)
        for note in prog[ci % len(prog)]:
            f = midi(note)
            detune = 1 + rng.uniform(-0.0015, 0.0015)
            out[a:b] += env * (0.5 * np.sin(2 * np.pi * f * detune * seg_t) + 0.18 * np.sin(2 * np.pi * 2 * f * seg_t + 0.3))
        out[a:b] += env * 0.35 * np.sin(2 * np.pi * midi(prog[ci % len(prog)][0] - 12) * seg_t)
    # slow breathing tremolo
    out *= 0.8 + 0.2 * np.sin(2 * np.pi * t / 11.0)
    return out


def pulse(duration, bpm=66):
    n = int(duration * SR)
    out = np.zeros(n)
    beat = 60.0 / bpm
    k = np.arange(int(0.35 * SR)) / SR
    hit = np.sin(2 * np.pi * 55 * k) * np.exp(-k * 9)
    for i in range(int(duration / beat)):
        if i % 2:
            continue
        a = int(i * beat * SR)
        out[a:a + len(hit)] += hit[: max(0, min(len(hit), n - a))]
    return out


def bells(duration, cues):
    n = int(duration * SR)
    out = np.zeros(n)
    k = np.arange(int(2.4 * SR)) / SR
    for c in cues:
        a = int(c * SR)
        if a >= n:
            continue
        f = midi(76)
        tone = (np.sin(2 * np.pi * f * k) + 0.4 * np.sin(2 * np.pi * 2.01 * f * k)) * np.exp(-k * 2.2)
        m = min(len(tone), n - a)
        out[a:a + m] += 0.5 * tone[:m]
    return out


def score(duration, cues, mood="calm", seed=7):
    x = 0.55 * pad(duration, mood, seed) + 0.35 * pulse(duration) + 0.22 * bells(duration, cues)
    # fade in/out
    n = len(x)
    f = int(min(3.0, duration / 4) * SR)
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    rms = np.sqrt(np.mean(x ** 2)) or 1
    x *= 10 ** (-24 / 20) / rms
    peak = np.max(np.abs(x))
    if peak > 0.5:
        x *= 0.5 / peak
    # gentle stereo width: tiny delay on the right channel
    d = int(0.011 * SR)
    left, right = x, np.concatenate([np.zeros(d), x[:-d]])
    return np.stack([left, right], axis=1)


def write_wav(path, stereo):
    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
