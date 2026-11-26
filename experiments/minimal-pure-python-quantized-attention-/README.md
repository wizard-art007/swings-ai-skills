# Minimal Pure-Python Quantized Attention & Generation Kernel

A zero-dependency, bare-metal inspired implementation of INT8 and INT4 (nibble-packed) matrix-vector multiplication (GEMV) and single-layer causal self-attention in pure Python 3.

## Overview & How It Works

1. **Quantization Schemes**:
   - **INT8 Symmetric**: Quantizes float matrices into signed 8-bit integers (`[-128, 127]`) with per-row scale factors.
   - **INT4 Packed Symmetric**: Quantizes float matrices into 4-bit integers (`[-8, 7]`) packed two nibbles per byte (`0xV2V1`).

2. **Quantized Matrix-Vector Multiplication (qmatvec / GEMV)**:
   - Performs matrix multiplication directly on quantized integer weights and floating-point activation vectors, scaling accumulated integer dot products back to float range.

3. **Causal Self-Attention Layer**:
   - Applies INT8/INT4 quantized weight matrices for $Q, K, V, O$ projections.
   - Computes causal scaled dot-product attention scores across sequence steps.

## How to Run

Run the offline pytest suite:

