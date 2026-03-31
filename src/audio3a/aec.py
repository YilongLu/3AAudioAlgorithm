from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .types import FloatArray


@dataclass(slots=True)
class NLMSAcousticEchoCanceller:
    """Simple NLMS AEC for single-channel reference.

    mic = near_end + echo(ref). We estimate echo from far-end reference and subtract it.
    """

    filter_length: int = 256
    step_size: float = 0.2
    eps: float = 1e-6
    _weights: FloatArray = field(init=False)
    _x_hist: FloatArray = field(init=False)

    def __post_init__(self) -> None:
        self._weights = np.zeros(self.filter_length, dtype=np.float32)
        self._x_hist = np.zeros(self.filter_length, dtype=np.float32)

    def process(self, mic_frame: FloatArray, ref_frame: FloatArray) -> FloatArray:
        if mic_frame.ndim != 1 or ref_frame.ndim != 1:
            raise ValueError("AEC currently supports mono frames only")
        if mic_frame.shape[0] != ref_frame.shape[0]:
            raise ValueError("mic and ref frame sizes must match")

        out = np.zeros_like(mic_frame)

        for n in range(mic_frame.shape[0]):
            self._x_hist[1:] = self._x_hist[:-1]
            self._x_hist[0] = ref_frame[n]

            y_hat = float(np.dot(self._weights, self._x_hist))
            err = mic_frame[n] - y_hat

            power = float(np.dot(self._x_hist, self._x_hist)) + self.eps
            mu = self.step_size / power
            self._weights += mu * err * self._x_hist

            out[n] = err

        return out
