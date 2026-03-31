from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .types import FloatArray


@dataclass(slots=True)
class RMSAutomaticGainControl:
    """Frame-wise AGC targeting RMS level with smooth attack/release."""

    target_rms: float = 0.1
    max_gain_db: float = 20.0
    noise_floor_rms: float = 1e-3
    limiter_peak: float = 0.95
    attack: float = 0.2
    release: float = 0.95
    enabled: bool = True
    _smooth_gain: float = 1.0

    def reset(self) -> None:
        self._smooth_gain = 1.0

    def process(self, frame: FloatArray) -> FloatArray:
        if frame.ndim != 1:
            raise ValueError("AGC currently supports mono frames only")
        if not self.enabled:
            return frame.astype(np.float32, copy=True)

        rms = float(np.sqrt(np.mean(frame * frame) + 1e-10))
        if rms < self.noise_floor_rms:
            desired_gain = 1.0
        else:
            desired_gain = self.target_rms / max(rms, 1e-6)
        max_gain = 10 ** (self.max_gain_db / 20.0)
        peak = float(np.max(np.abs(frame)) + 1e-8)
        peak_limited_gain = self.limiter_peak / peak
        desired_gain = min(desired_gain, max_gain, peak_limited_gain)

        if desired_gain > self._smooth_gain:
            self._smooth_gain = self.attack * desired_gain + (1 - self.attack) * self._smooth_gain
        else:
            self._smooth_gain = self.release * self._smooth_gain + (1 - self.release) * desired_gain

        return np.clip(frame * self._smooth_gain, -1.0, 1.0).astype(np.float32)
