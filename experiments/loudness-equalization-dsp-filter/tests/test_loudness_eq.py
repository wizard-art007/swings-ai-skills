import math
import sys

sys.path.insert(0, "src")

from loudness_eq import BiquadFilter, LoudnessEqualizer


def generate_tone(freq: float, amp: float, count: int, sr: int = 44100) -> list[float]:
    return [amp * math.sin(2.0 * math.pi * freq * i / sr) for i in range(count)]


def rms(samples: list[float]) -> float:
    return math.sqrt(sum(s * s for s in samples) / max(1, len(samples)))


def test_biquad_highpass_attenuates_low_frequencies():
    sr = 44100
    hp = BiquadFilter.highpass(sample_rate=sr, cutoff_hz=100.0)
    low_sine = generate_tone(15.0, 0.8, 1000, sr)
    out_low = [hp.process(s) for s in low_sine]
    # 15Hz should be significantly attenuated by 100Hz highpass
    assert rms(out_low[-200:]) < 0.25


def test_loudness_equalization_reduces_dynamic_range():
    sr = 44100
    eq = LoudnessEqualizer(sample_rate=sr, target_db=-14.0, max_boost_db=10.0)

    # 0.5s of quiet signal (-30 dBFS approx) followed by 0.5s of loud signal (~0 dBFS)
    quiet = generate_tone(440.0, 0.03, int(sr * 0.4), sr)
    loud = generate_tone(440.0, 0.90, int(sr * 0.4), sr)
    raw = quiet + loud
    processed = eq.process_stream(raw)

    raw_quiet_rms = rms(quiet[-2000:])
    raw_loud_rms = rms(loud[-2000:])
    proc_quiet_rms = rms(processed[int(sr * 0.2) : int(sr * 0.4)])
    proc_loud_rms = rms(processed[-2000:])

    raw_ratio = raw_loud_rms / raw_quiet_rms
    proc_ratio = proc_loud_rms / proc_quiet_rms

    # Equalization should compress the dynamic gap significantly
    assert proc_ratio < raw_ratio * 0.5
    assert all(-1.0 <= s <= 1.0 for s in processed)


def test_gate_avoids_amplifying_silence():
    sr = 44100
    eq = LoudnessEqualizer(sample_rate=sr, gate_db=-50.0)
    silence = [0.0] * 500
    out = eq.process_stream(silence)
    assert max(abs(s) for s in out) == 0.0
