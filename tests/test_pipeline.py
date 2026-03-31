import unittest

import numpy as np

from audio3a.pipeline import ThreeAPipeline


class TestThreeA(unittest.TestCase):
    def test_process_frame_shape(self) -> None:
        pipeline = ThreeAPipeline()
        mic = np.random.randn(160).astype(np.float32) * 0.01
        ref = np.random.randn(160).astype(np.float32) * 0.01
        out = pipeline.process_frame(mic, ref)
        self.assertEqual(out.shape, mic.shape)
        self.assertEqual(out.dtype, np.float32)


if __name__ == "__main__":
    unittest.main()
