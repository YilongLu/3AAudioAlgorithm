from __future__ import annotations

from pathlib import Path

from .io import WavFileSink, WavFileSource
from .pipeline import ThreeAPipeline
from .types import AudioFrame, AudioStreamConfig


def process_wav_files(
    mic_wav_path: str | Path,
    out_wav_path: str | Path,
    stream_config: AudioStreamConfig,
    ref_wav_path: str | Path | None = None,
    pipeline: ThreeAPipeline | None = None,
) -> None:
    """Offline wav-to-wav interface.

    This is the recommended bridge API for C++ migration:
      1) Replace source/sink with hardware ring-buffer I/O.
      2) Keep frame-level `pipeline.process_frame` call unchanged.
    """

    pipeline = pipeline or ThreeAPipeline(stream_config=stream_config)
    mic_source = WavFileSource(mic_wav_path, stream_config)
    ref_source = WavFileSource(ref_wav_path, stream_config) if ref_wav_path else None
    sink = WavFileSink(out_wav_path, stream_config)

    ref_iter = ref_source.read_frames() if ref_source else None

    try:
        for mic_frame in mic_source.read_frames():
            if ref_iter:
                try:
                    ref_frame = next(ref_iter).ensure_mono()
                except StopIteration:
                    ref_frame = None
            else:
                ref_frame = None
            out = pipeline.process_frame(mic_frame.ensure_mono(), ref_frame)
            sink.write_frame(AudioFrame(data=out, timestamp_ms=mic_frame.timestamp_ms))
    finally:
        sink.close()
