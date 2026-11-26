import math


def quantize_int8(matrix):
    """Symmetric per-row INT8 quantization for a 2D float matrix."""
    q_matrix, scales = [], []
    for row in matrix:
        max_val = max(abs(x) for x in row) or 1e-8
        scale = max_val / 127.0
        q_row = [max(-128, min(127, round(x / scale))) for x in row]
        q_matrix.append(q_row)
        scales.append(scale)
    return q_matrix, scales


def quantize_int4(matrix):
    """Symmetric per-row INT4 packed quantization (2 nibbles per byte)."""
    packed_matrix, scales = [], []
    for row in matrix:
        max_val = max(abs(x) for x in row) or 1e-8
        scale = max_val / 7.0
        q_vals = [max(-8, min(7, round(x / scale))) for x in row]
        packed = []
        for i in range(0, len(q_vals), 2):
            v1 = q_vals[i] & 0x0F
            v2 = (q_vals[i + 1] & 0x0F) if i + 1 < len(q_vals) else 0
            packed.append((v2 << 4) | v1)
        packed_matrix.append(packed)
        scales.append(scale)
    return packed_matrix, scales


def qmatvec_int8(q_matrix, scales, vec):
    """Quantized matrix-vector multiplication (GEMV) for INT8 weights."""
    return [
        scale * sum(qw * v for qw, v in zip(q_row, vec))
        for q_row, scale in zip(q_matrix, scales)
    ]


def qmatvec_int4(packed_matrix, scales, vec):
    """Quantized matrix-vector multiplication (GEMV) for INT4 packed weights."""
    out = []
    for packed_row, scale in zip(packed_matrix, scales):
        acc, idx = 0.0, 0
        for byte in packed_row:
            v1 = byte & 0x0F
            if v1 >= 8:
                v1 -= 16
            acc += v1 * vec[idx]
            idx += 1
            if idx < len(vec):
                v2 = (byte >> 4) & 0x0F
                if v2 >= 8:
                    v2 -= 16
                acc += v2 * vec[idx]
                idx += 1
        out.append(acc * scale)
    return out


def softmax(vec):
    max_v = max(vec) if vec else 0.0
    exps = [math.exp(x - max_v) for x in vec]
    sum_e = sum(exps) or 1e-8
    return [e / sum_e for e in exps]


class QuantizedCausalAttention:
    """Minimal single-head causal self-attention using INT8 or INT4 quantized projections."""

    def __init__(self, dim, w_q, w_k, w_v, w_o, q_mode="int8"):
        self.dim = dim
        self.q_mode = q_mode
        q_fn = quantize_int4 if q_mode == "int4" else quantize_int8
        self.q_q, self.s_q = q_fn(w_q)
        self.q_k, self.s_k = q_fn(w_k)
        self.q_v, self.s_v = q_fn(w_v)
        self.q_o, self.s_o = q_fn(w_o)
        self.matvec = qmatvec_int4 if q_mode == "int4" else qmatvec_int8

    def forward(self, x_seq):
        seq_len = len(x_seq)
        Q = [self.matvec(self.q_q, self.s_q, x) for x in x_seq]
        K = [self.matvec(self.q_k, self.s_k, x) for x in x_seq]
        V = [self.matvec(self.q_v, self.s_v, x) for x in x_seq]

        out = []
        scale = 1.0 / math.sqrt(self.dim)
        for i in range(seq_len):
            scores = [
                sum(Q[i][d] * K[j][d] for d in range(self.dim)) * scale
                for j in range(i + 1)
            ]
            weights = softmax(scores)
            context = [
                sum(weights[j] * V[j][d] for j in range(i + 1))
                for d in range(self.dim)
            ]
            out.append(self.matvec(self.q_o, self.s_o, context))
        return out
