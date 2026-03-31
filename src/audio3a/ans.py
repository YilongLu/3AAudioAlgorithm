from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .types import FloatArray


@dataclass(slots=True)
class SpectralNoiseSuppressor:
    """Basic spectral gating noise suppressor with running noise floor estimation."""

    n_fft: int = 320
    alpha_noise: float = 0.95
    over_subtraction: float = 1.2
    floor_gain: float = 0.1
    _noise_psd: FloatArray = field(init=False)

    def __post_init__(self) -> None:
        self._noise_psd = np.ones(self.n_fft // 2 + 1, dtype=np.float32) * 1e-4

    def process(self, frame: FloatArray) -> FloatArray:
        if frame.ndim != 1:
            raise ValueError("ANS currently supports mono frames only")

        if frame.shape[0] < self.n_fft:
            padded = np.zeros(self.n_fft, dtype=np.float32)
            padded[: frame.shape[0]] = frame
            x = padded
            valid = frame.shape[0]
        else:
            x = frame[: self.n_fft]
            valid = self.n_fft

        spec = np.fft.rfft(x)
        mag = np.abs(spec).astype(np.float32)
        phase = np.angle(spec)
        psd = mag * mag

        self._noise_psd = self.alpha_noise * self._noise_psd + (1 - self.alpha_noise) * psd

        clean_psd = np.maximum(psd - self.over_subtraction * self._noise_psd, self.floor_gain * self._noise_psd)
        gain = np.sqrt(clean_psd / (psd + 1e-10))

        enh_spec = gain * mag * np.exp(1j * phase)
        y = np.fft.irfft(enh_spec, n=self.n_fft).real.astype(np.float32)
        return y[:valid]
