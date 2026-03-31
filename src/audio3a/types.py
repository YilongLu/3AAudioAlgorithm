from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float32]


@dataclass(slots=True)
class AudioStreamConfig:
    """Stream-level configuration for frame based processing."""

    sample_rate_hz: int
    channels: int = 1
    frame_size: int = 160


@dataclass(slots=True)
class AudioFrame:
    """One frame of audio samples.

    All samples are normalized float32 in range [-1.0, 1.0].
    Shape is (num_samples,) for mono or (num_samples, channels).
    """

    data: FloatArray
    timestamp_ms: float

    def ensure_mono(self) -> FloatArray:
        if self.data.ndim == 1:
            return self.data
        return self.data[:, 0]
