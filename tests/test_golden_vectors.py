import shutil
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np


class TestGoldenVectorExport(unittest.TestCase):
    def test_export_script_writes_reference_arrays(self) -> None:
        if shutil.which(sys.executable) is None:
            self.skipTest("Python executable is unavailable")

        repo_root = Path(__file__).resolve().parents[1]
        out_dir = repo_root / "artifacts" / "test_vectors"
        if out_dir.exists():
            shutil.rmtree(out_dir)

        command = [
            sys.executable,
            "examples/export_golden_vectors.py",
            "--output-dir",
            str(out_dir),
            "--num-frames",
            "3",
            "--seed",
            "7",
        ]
        subprocess.run(command, check=True, cwd=repo_root)

        with np.load(out_dir / "pipeline_reference.npz") as archive:
            self.assertEqual(archive["mic"].shape, (3, 160))
            self.assertEqual(archive["ref"].shape, (3, 160))
            self.assertEqual(archive["out"].shape, (3, 160))
            self.assertEqual(int(archive["sample_rate_hz"]), 16000)
            self.assertEqual(int(archive["frame_size"]), 160)

        shutil.rmtree(out_dir)
