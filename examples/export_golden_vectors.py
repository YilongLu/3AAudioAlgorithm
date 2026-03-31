from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from audio3a.pipeline import ThreeAPipeline
from audio3a.types import AudioStreamConfig


def build_reference_vectors(num_frames: int, seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    config = AudioStreamConfig()
    pipeline = ThreeAPipeline(stream_config=config)

    mic_frames = []
    ref_frames = []
    out_frames = []

    for _ in range(num_frames):
        ref = rng.normal(0.0, 0.03, config.frame_size).astype(np.float32)
        near = rng.normal(0.0, 0.01, config.frame_size).astype(np.float32)
        echo = np.roll(ref, 8) * 0.35
        mic = np.clip(near + echo, -1.0, 1.0).astype(np.float32)

        out = pipeline.process_frame(mic, ref)
        mic_frames.append(mic)
        ref_frames.append(ref)
        out_frames.append(out)

    return {
        "mic": np.stack(mic_frames).astype(np.float32),
        "ref": np.stack(ref_frames).astype(np.float32),
        "out": np.stack(out_frames).astype(np.float32),
        "sample_rate_hz": np.array(config.sample_rate_hz, dtype=np.int32),
        "frame_size": np.array(config.frame_size, dtype=np.int32),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export golden reference vectors for C++/DSP alignment.")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/golden_vectors"))
    parser.add_argument("--num-frames", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    vectors = build_reference_vectors(args.num_frames, args.seed)
    np.savez(args.output_dir / "pipeline_reference.npz", **vectors)


if __name__ == "__main__":
    main()
