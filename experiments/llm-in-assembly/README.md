# Qwen-ASM: Bare-Metal LLM Inference Simulation & Quantizer

An experimental project inspired by extreme low-level LLM implementations (running miniature language models directly in assembly/bare-metal environments). 

This package provides:
1. **Qwen-ASM Quantizer & Matrix Engine**: Quantizes lightweight transformer weights down to packed INT2/INT4 formats optimized for bare-metal execution.
2. **x86-64 Assembly Code Generator**: Emits pure NASM assembly loops for matrix-vector multiplication (`dot_product` and RMSNorm/RoPE steps) utilizing AVX2/FMA instructions or raw scalar loops.
3. **Bare-Metal Bootsector Simulator**: A simulated 16-bit/32-bit real-mode bootloader runtime that loads embedded quantized weights and executes inference cycle-by-cycle without an operating system.

## How It Works
- **Quantization**: Compresses standard floating-point attention weights and MLP projections into low-bit integers to fit within tight L1/L2 cache and real-mode memory footprints (under 512 bytes for the boot stub, weights mapped right after).
- **Assembly Generation**: Translates transformer forward passes into tight assembly routines using register accumulation.
- **Simulator**: Simulates CPU execution registers, serial output (COM1 port simulation), and token generation loop.

## How to Run

Run unit tests:
