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
    enabled: bool = True
    adaptation_enabled: bool = True
    double_talk_ratio: float = 2.0
    _weights: FloatArray = field(init=False)
    _x_hist: FloatArray = field(init=False)
    _head: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._weights = np.zeros(self.filter_length, dtype=np.float32)
        self._x_hist = np.zeros(self.filter_length, dtype=np.float32)
        self._head = 0

    def _ordered_history_views(self) -> tuple[FloatArray, FloatArray, int]:
        tail = self._x_hist[self._head :]
        head = self._x_hist[: self._head]
        return tail, head, tail.shape[0]

    def process(self, mic_frame: FloatArray, ref_frame: FloatArray) -> FloatArray:
        if mic_frame.ndim != 1 or ref_frame.ndim != 1:
            raise ValueError("AEC currently supports mono frames only")
        if mic_frame.shape[0] != ref_frame.shape[0]:
            raise ValueError("mic and ref frame sizes must match")
        if not self.enabled:
            return mic_frame.astype(np.float32, copy=True)

        out = np.zeros_like(mic_frame)

        for n in range(mic_frame.shape[0]):
            self._head = (self._head - 1) % self.filter_length
            self._x_hist[self._head] = ref_frame[n]

            tail, head, split = self._ordered_history_views()
            y_hat = float(np.dot(self._weights[:split], tail))
            if head.size:
                y_hat += float(np.dot(self._weights[split:], head))
            err = mic_frame[n] - y_hat

            far_power = float(np.dot(tail, tail))
            if head.size:
                far_power += float(np.dot(head, head))
            near_power = float(err * err)
            if self.adaptation_enabled and far_power > self.eps and near_power <= self.double_talk_ratio * far_power:
                mu = self.step_size / (far_power + self.eps)
                self._weights[:split] += mu * err * tail
                if head.size:
                    self._weights[split:] += mu * err * head

            out[n] = err

        return out
