import unittest
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from audio3a.aec import NLMSAcousticEchoCanceller
from audio3a.agc import RMSAutomaticGainControl
from audio3a.ans import SpectralNoiseSuppressor
from audio3a.drc import DynamicRangeCompressor
from audio3a.pipeline import ThreeAPipeline
from audio3a.types import AudioStreamConfig


class TestThreeA(unittest.TestCase):
    def setUp(self) -> None:
        self.config = AudioStreamConfig()

    def test_process_frame_shape(self) -> None:
        pipeline = ThreeAPipeline(stream_config=self.config)
        mic = np.random.randn(160).astype(np.float32) * 0.01
        ref = np.random.randn(160).astype(np.float32) * 0.01
        out = pipeline.process_frame(mic, ref)
        self.assertEqual(out.shape, mic.shape)
        self.assertEqual(out.dtype, np.float32)

    def test_process_frame_requires_mono_contract(self) -> None:
        pipeline = ThreeAPipeline(stream_config=self.config)
        mic = np.random.randn(160).astype(np.float32) * 0.01
        with self.assertRaises(ValueError):
            pipeline.process_frame(mic.reshape(80, 2))

    def test_drc_limits_peak(self) -> None:
        drc = DynamicRangeCompressor(threshold_db=-24.0, ratio=6.0)
        frame = (np.ones(160) * 0.9).astype(np.float32)
        out = drc.process(frame)
        self.assertLessEqual(float(np.max(np.abs(out))), 1.0)

    def test_module_bypass_returns_input(self) -> None:
        frame = np.linspace(-0.25, 0.25, 160, dtype=np.float32)
        ref = np.linspace(0.1, -0.1, 160, dtype=np.float32)

        aec = NLMSAcousticEchoCanceller(enabled=False)
        ans = SpectralNoiseSuppressor(enabled=False)
        agc = RMSAutomaticGainControl(enabled=False)
        drc = DynamicRangeCompressor(enabled=False)

        np.testing.assert_allclose(aec.process(frame, ref), frame)
        np.testing.assert_allclose(ans.process(frame), frame)
        np.testing.assert_allclose(agc.process(frame), frame)
        np.testing.assert_allclose(drc.process(frame), frame)

    def test_pipeline_reset_restores_stateful_modules(self) -> None:
        pipeline = ThreeAPipeline(stream_config=self.config)
        mic = np.sin(np.linspace(0.0, 2.0 * np.pi, 160, dtype=np.float32)) * 0.05
        ref = np.roll(mic, 1)

        first = pipeline.process_frame(mic, ref)
        second = pipeline.process_frame(mic, ref)
        pipeline.reset()
        third = pipeline.process_frame(mic, ref)

        self.assertFalse(np.allclose(first, second))
        np.testing.assert_allclose(first, third, atol=1e-5)

    def test_agc_noise_floor_prevents_silence_boost(self) -> None:
        agc = RMSAutomaticGainControl(noise_floor_rms=1e-2, max_gain_db=30.0)
        silent = np.zeros(160, dtype=np.float32)
        out = agc.process(silent)
        np.testing.assert_allclose(out, silent)


if __name__ == "__main__":
    unittest.main()
