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
    _gain_db_smooth: float = 0.0

    def process(self, frame: FloatArray) -> FloatArray:
        if frame.ndim != 1:
            raise ValueError("DRC currently supports mono frames only")

        abs_frame = np.abs(frame) + 1e-8
        level_db = 20.0 * np.log10(abs_frame)

        over_db = np.maximum(level_db - self.threshold_db, 0.0)
        compressed_over_db = over_db / self.ratio
        gain_reduction_db = over_db - compressed_over_db

        target_gain_db = -float(np.mean(gain_reduction_db)) + self.makeup_gain_db
        if target_gain_db < self._gain_db_smooth:
            self._gain_db_smooth = self.attack * target_gain_db + (1 - self.attack) * self._gain_db_smooth
        else:
            self._gain_db_smooth = self.release * self._gain_db_smooth + (1 - self.release) * target_gain_db

        gain_lin = 10.0 ** (self._gain_db_smooth / 20.0)
        out = np.clip(frame * gain_lin, -1.0, 1.0)
        return out.astype(np.float32)
