from __future__ import annotations

import wave
from pathlib import Path
from typing import Iterator, Protocol

import numpy as np

from .types import AudioFrame, AudioStreamConfig, FloatArray


class AudioSource(Protocol):
    """Generic pull-style audio source interface (easy to map to C++ abstract class)."""

    def read_frames(self) -> Iterator[AudioFrame]:
        ...


class AudioSink(Protocol):
    """Generic push-style audio sink interface."""

    def write_frame(self, frame: AudioFrame) -> None:
        ...

    def close(self) -> None:
        ...


def pcm16_to_float32(raw: bytes, channels: int) -> FloatArray:
    arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        arr = arr.reshape(-1, channels)
    return arr


def float32_to_pcm16(samples: FloatArray) -> bytes:
    clipped = np.clip(samples, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)
    return pcm.tobytes()


class WavFileSource:
    def __init__(self, wav_path: str | Path, config: AudioStreamConfig):
        self._path = Path(wav_path)
        self._config = config

    def read_frames(self) -> Iterator[AudioFrame]:
        with wave.open(str(self._path), "rb") as wf:
            if wf.getframerate() != self._config.sample_rate_hz:
                raise ValueError("Sample rate mismatch between wav file and config")
            if wf.getnchannels() != self._config.channels:
                raise ValueError("Channel count mismatch between wav file and config")

            frame_index = 0
            while True:
                raw = wf.readframes(self._config.frame_size)
                if not raw:
                    break
                data = pcm16_to_float32(raw, self._config.channels)
                timestamp_ms = frame_index * self._config.frame_size / self._config.sample_rate_hz * 1000.0
                frame_index += 1
                yield AudioFrame(data=data, timestamp_ms=timestamp_ms)


class WavFileSink:
    def __init__(self, wav_path: str | Path, config: AudioStreamConfig):
        self._path = Path(wav_path)
        self._config = config
        self._wf = wave.open(str(self._path), "wb")
        self._wf.setnchannels(config.channels)
        self._wf.setsampwidth(2)
        self._wf.setframerate(config.sample_rate_hz)

    def write_frame(self, frame: AudioFrame) -> None:
        self._wf.writeframes(float32_to_pcm16(frame.data))

    def close(self) -> None:
        self._wf.close()
