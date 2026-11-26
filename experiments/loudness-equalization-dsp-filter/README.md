# Loudness Equalization DSP Filter

A pure Python digital signal processing (DSP) pipeline inspired by reverse-engineered OS-level loudness equalization filters (such as Windows Loudness Equalization and PipeWire `pw-loudness-eq`).

## How It Works

1. **High-pass Pre-filter (Biquad)**: Cuts inaudible sub-bass content (rumble below 70 Hz) that biases RMS detection without contributing to perceived loudness.
2. **Dual-Time-Constant Envelope Detector**: Tracks RMS signal energy with an asymmetric response (fast attack ~10 ms to catch spikes, slow release ~150 ms to prevent pumping).
3. **Target Loudness Normalization & Noise Gating**: Evaluates deviation against a target dBFS level, capping maximum boost and gating near the noise floor to prevent amplifying background hiss.
4. **Lookahead Delay Buffer & Smoothing**: Delays the audio stream by 5 ms so gain adjustments lead transient peaks, interpolated to eliminate zipper noise.
5. **Soft-Knee Output Limiter**: Uses `tanh` saturation to prevent clipping distortion when applying boost.

## Running Tests

Run offline unit tests using `pytest`:

