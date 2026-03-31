from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .types import FloatArray


@dataclass(slots=True)
class RMSAutomaticGainControl:
    """Frame-wise AGC targeting RMS level with smooth attack/release."""

    target_rms: float = 0.1
    max_gain_db: float = 20.0
    attack: float = 0.2
    release: float = 0.95
    _smooth_gain: float = 1.0

    def process(self, frame: FloatArray) -> FloatArray:
        if frame.ndim != 1:
            raise ValueError("AGC currently supports mono frames only")

        rms = float(np.sqrt(np.mean(frame * frame) + 1e-10))
        desired_gain = self.target_rms / max(rms, 1e-6)
        max_gain = 10 ** (self.max_gain_db / 20.0)
        desired_gain = min(desired_gain, max_gain)

        if desired_gain > self._smooth_gain:
            self._smooth_gain = self.attack * desired_gain + (1 - self.attack) * self._smooth_gain
        else:
            self._smooth_gain = self.release * self._smooth_gain + (1 - self.release) * desired_gain

        return np.clip(frame * self._smooth_gain, -1.0, 1.0).astype(np.float32)
