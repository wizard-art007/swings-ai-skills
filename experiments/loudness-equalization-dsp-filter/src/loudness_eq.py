import math
from collections import deque


class BiquadFilter:
    """Second-order IIR filter for pre-weighting audio signals."""

    def __init__(self, b0: float, b1: float, b2: float, a1: float, a2: float):
        self.b0, self.b1, self.b2 = b0, b1, b2
        self.a1, self.a2 = a1, a2
        self.x1 = self.x2 = self.y1 = self.y2 = 0.0

    @classmethod
    def highpass(cls, sample_rate: int, cutoff_hz: float = 60.0, q: float = 0.707):
        w0 = 2.0 * math.pi * cutoff_hz / sample_rate
        alpha = math.sin(w0) / (2.0 * q)
        cos_w0 = math.cos(w0)
        a0 = 1.0 + alpha
        return cls(
            (1.0 + cos_w0) / 2.0 / a0,
            -(1.0 + cos_w0) / a0,
            (1.0 + cos_w0) / 2.0 / a0,
            (-2.0 * cos_w0) / a0,
            (1.0 - alpha) / a0,
        )

    def process(self, x: float) -> float:
        y = self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2 - self.a1 * self.y1 - self.a2 * self.y2
        self.x1, self.x2 = x, self.x1
        self.y1, self.y2 = y, self.y1
        return y


class LoudnessEqualizer:
    """Dynamic range compressor and loudness equalizer with lookahead."""

    def __init__(
        self,
        sample_rate: int = 44100,
        target_db: float = -14.0,
        attack_sec: float = 0.010,
        release_sec: float = 0.150,
        lookahead_sec: float = 0.005,
        max_boost_db: float = 12.0,
        gate_db: float = -55.0,
    ):
        self.sample_rate = sample_rate
        self.target_db = target_db
        self.max_boost_db = max_boost_db
        self.gate_db = gate_db

        self.alpha_att = math.exp(-1.0 / (sample_rate * max(attack_sec, 1e-4)))
        self.alpha_rel = math.exp(-1.0 / (sample_rate * max(release_sec, 1e-4)))

        self.pre_filter = BiquadFilter.highpass(sample_rate, cutoff_hz=70.0)
        self.env = 0.0
        self.smooth_gain = 1.0

        delay_samples = max(1, int(sample_rate * lookahead_sec))
        self.delay_buf = deque([0.0] * delay_samples, maxlen=delay_samples)

    def _calc_target_gain(self, env_rms: float) -> float:
        if env_rms < 1e-6:
            return 1.0
        env_db = 20.0 * math.log10(env_rms)
        if env_db <= self.gate_db:
            return 1.0  # Noise floor gating
        needed_db = self.target_db - env_db
        gain_db = max(-30.0, min(self.max_boost_db, needed_db))
        return 10.0 ** (gain_db / 20.0)

    def process_sample(self, x: float) -> float:
        filtered = self.pre_filter.process(x)
        sq = filtered * filtered
        coeff = self.alpha_att if sq > self.env else self.alpha_rel
        self.env = coeff * self.env + (1.0 - coeff) * sq
        rms = math.sqrt(max(0.0, self.env))

        target_gain = self._calc_target_gain(rms)
        self.smooth_gain += 0.05 * (target_gain - self.smooth_gain)

        delayed_x = self.delay_buf[0]
        self.delay_buf.append(x)
        out = delayed_x * self.smooth_gain
        return math.tanh(out)  # Soft knee limiter

    def process_stream(self, samples: list[float]) -> list[float]:
        return [self.process_sample(s) for s in samples]
