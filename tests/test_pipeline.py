import unittest

import numpy as np

from audio3a.drc import DynamicRangeCompressor
from audio3a.pipeline import ThreeAPipeline


class TestThreeA(unittest.TestCase):
    def test_process_frame_shape(self) -> None:
        pipeline = ThreeAPipeline()
        mic = np.random.randn(160).astype(np.float32) * 0.01
        ref = np.random.randn(160).astype(np.float32) * 0.01
        out = pipeline.process_frame(mic, ref)
        self.assertEqual(out.shape, mic.shape)
        self.assertEqual(out.dtype, np.float32)

    def test_drc_limits_peak(self) -> None:
        drc = DynamicRangeCompressor(threshold_db=-24.0, ratio=6.0)
        frame = (np.ones(160) * 0.9).astype(np.float32)
        out = drc.process(frame)
        self.assertLessEqual(float(np.max(np.abs(out))), 1.0)


if __name__ == "__main__":
    unittest.main()
