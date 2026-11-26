import math
import sys

sys.path.insert(0, "src")

from quantized_attention import (
    QuantizedCausalAttention,
    qmatvec_int4,
    qmatvec_int8,
    quantize_int4,
    quantize_int8,
)


def test_int8_matvec_accuracy():
    W = [[1.5, -2.0, 0.5], [-0.8, 3.1, -1.2]]
    x = [0.5, 1.0, -1.5]
    q_w, scales = quantize_int8(W)
    res = qmatvec_int8(q_w, scales, x)
    expected = [sum(W[i][j] * x[j] for j in range(3)) for i in range(2)]
    for r, e in zip(res, expected):
        assert math.isclose(r, e, abs_tol=0.1)


def test_int4_matvec_accuracy():
    W = [[1.5, -2.0, 0.5, 0.1], [-0.8, 3.1, -1.2, 2.0]]
    x = [0.5, 1.0, -1.5, 0.5]
    q_w, scales = quantize_int4(W)
    res = qmatvec_int4(q_w, scales, x)
    expected = [sum(W[i][j] * x[j] for j in range(4)) for i in range(2)]
    for r, e in zip(res, expected):
        assert math.isclose(r, e, abs_tol=0.35)


def test_causal_attention_int8():
    dim = 4
    w = [[(i + j * 0.1) % 1.0 for j in range(dim)] for i in range(dim)]
    attn = QuantizedCausalAttention(dim, w, w, w, w, q_mode="int8")
    seq = [[0.1 * (i + 1)] * dim for i in range(3)]
    out = attn.forward(seq)
    assert len(out) == 3
    assert len(out[0]) == dim


def test_causal_attention_int4():
    dim = 4
    w = [[(i - j * 0.2) % 1.0 for j in range(dim)] for i in range(dim)]
    attn = QuantizedCausalAttention(dim, w, w, w, w, q_mode="int4")
    seq = [[0.2] * dim, [0.5] * dim]
    out = attn.forward(seq)
    assert len(out) == 2
    assert len(out[0]) == dim
