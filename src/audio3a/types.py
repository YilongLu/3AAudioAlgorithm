from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float32]
DEFAULT_SAMPLE_RATE_HZ = 16000
DEFAULT_CHANNELS = 1
DEFAULT_FRAME_SIZE = 160


@dataclass(slots=True)
class AudioStreamConfig:
    """Stream-level configuration for frame based processing."""

    sample_rate_hz: int = DEFAULT_SAMPLE_RATE_HZ
    channels: int = DEFAULT_CHANNELS
    frame_size: int = DEFAULT_FRAME_SIZE

    def __post_init__(self) -> None:
        if self.sample_rate_hz != DEFAULT_SAMPLE_RATE_HZ:
            raise ValueError(f"Only {DEFAULT_SAMPLE_RATE_HZ} Hz is supported in the reference pipeline")
        if self.channels != DEFAULT_CHANNELS:
            raise ValueError("Only mono processing is supported in the reference pipeline")
        if self.frame_size != DEFAULT_FRAME_SIZE:
            raise ValueError(f"Only {DEFAULT_FRAME_SIZE}-sample frames are supported in the reference pipeline")


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
            return self.data.astype(np.float32, copy=False)
        return self.data[:, 0].astype(np.float32, copy=False)


def as_float_mono_frame(frame: FloatArray, frame_size: int = DEFAULT_FRAME_SIZE) -> FloatArray:
    array = np.asarray(frame, dtype=np.float32)
    if array.ndim != 1:
        raise ValueError("Audio frames must be mono 1-D float arrays")
    if array.shape[0] != frame_size:
        raise ValueError(f"Audio frames must contain exactly {frame_size} samples")
    return np.ascontiguousarray(array)
