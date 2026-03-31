from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .types import FloatArray


@dataclass(slots=True)
class DynamicRangeCompressor:
    """Simple feed-forward dynamic range compressor.

    Args:
        threshold_db: Compression threshold in dBFS.
        ratio: Compression ratio above threshold.
        makeup_gain_db: Fixed make-up gain after compression.
        attack: Envelope attack coefficient (0~1, larger=faster).
        release: Envelope release coefficient (0~1, larger=slower).
    """

    threshold_db: float = -18.0
    ratio: float = 4.0
    makeup_gain_db: float = 3.0
    attack: float = 0.2
    release: float = 0.98
    enabled: bool = True
    _gain_db_smooth: float = 0.0
    _envelope: float = 0.0

    def reset(self) -> None:
        self._gain_db_smooth = 0.0
        self._envelope = 0.0

    def process(self, frame: FloatArray) -> FloatArray:
        if frame.ndim != 1:
            raise ValueError("DRC currently supports mono frames only")
        if not self.enabled:
            return frame.astype(np.float32, copy=True)

        out = np.zeros_like(frame)
        for index, sample in enumerate(frame):
            level = abs(float(sample))
            coeff = self.attack if level > self._envelope else self.release
            self._envelope = coeff * level + (1.0 - coeff) * self._envelope

            level_db = 20.0 * np.log10(self._envelope + 1e-8)
            over_db = max(level_db - self.threshold_db, 0.0)
            compressed_over_db = over_db / self.ratio
            gain_reduction_db = over_db - compressed_over_db
            target_gain_db = self.makeup_gain_db - gain_reduction_db

            gain_coeff = self.attack if target_gain_db < self._gain_db_smooth else self.release
            self._gain_db_smooth = gain_coeff * target_gain_db + (1.0 - gain_coeff) * self._gain_db_smooth

            gain_lin = 10.0 ** (self._gain_db_smooth / 20.0)
            out[index] = float(np.clip(sample * gain_lin, -1.0, 1.0))
        return out.astype(np.float32, copy=False)
