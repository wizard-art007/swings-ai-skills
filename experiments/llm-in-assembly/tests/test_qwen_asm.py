import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from qwen_asm import QwenQuantizer, AssemblyGenerator, BareMetalSimulator

def test_quantizer_4bit():
    weights = [0.0, 0.5, 1.0, -1.0]
    packed, min_w, scale = QwenQuantizer.quantize_weights(weights, bits=4)
    assert isinstance(packed, bytes)
    assert len(packed) == 2  # 4 values packed into 2 bytes for 4-bit
    assert min_w == -1.0
    assert scale == 2.0

def test_assembly_generator():
    asm = AssemblyGenerator.generate_matvec_kernel(bits=4)
    assert "qwen_matvec_kernel" in asm
    assert "section .text" in asm

def test_bare_metal_simulator():
    sim = BareMetalSimulator(vocab_size=1000)
    output = sim.simulate_boot([65, 66, 67])
    assert isinstance(output, str)
    assert len(output) == 3
    assert len(sim.serial_log) == 3
