from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .types import FloatArray


@dataclass(slots=True)
class SpectralNoiseSuppressor:
    """Basic spectral gating noise suppressor with running noise floor estimation."""

    n_fft: int = 320
    hop_size: int = 160
    alpha_noise: float = 0.95
    over_subtraction: float = 1.2
    floor_gain: float = 0.1
    enabled: bool = True
    _noise_psd: FloatArray = field(init=False)
    _analysis_window: FloatArray = field(init=False)
    _synthesis_window: FloatArray = field(init=False)
    _analysis_state: FloatArray = field(init=False)
    _overlap: FloatArray = field(init=False)

    def __post_init__(self) -> None:
        if self.hop_size * 2 != self.n_fft:
            raise ValueError("Reference ANS expects 50% overlap: hop_size * 2 must equal n_fft")
        self._analysis_window = np.hanning(self.n_fft).astype(np.float32)
        self._synthesis_window = self._analysis_window.copy()
        self.reset()

    def reset(self) -> None:
        self._noise_psd = np.ones(self.n_fft // 2 + 1, dtype=np.float32) * 1e-4
        self._analysis_state = np.zeros(self.n_fft, dtype=np.float32)
        self._overlap = np.zeros(self.hop_size, dtype=np.float32)

    def process(self, frame: FloatArray) -> FloatArray:
        if frame.ndim != 1:
            raise ValueError("ANS currently supports mono frames only")
        if frame.shape[0] != self.hop_size:
            raise ValueError(f"ANS expects {self.hop_size}-sample frames")
        if not self.enabled:
            return frame.astype(np.float32, copy=True)

        self._analysis_state[: self.hop_size] = self._analysis_state[self.hop_size :]
        self._analysis_state[self.hop_size :] = frame
        windowed = self._analysis_state * self._analysis_window

        spec = np.fft.rfft(windowed)
        mag = np.abs(spec).astype(np.float32)
        phase = np.angle(spec)
        psd = mag * mag

        self._noise_psd = self.alpha_noise * self._noise_psd + (1 - self.alpha_noise) * psd

        clean_psd = np.maximum(psd - self.over_subtraction * self._noise_psd, self.floor_gain * self._noise_psd)
        gain = np.sqrt(clean_psd / (psd + 1e-10))

        enh_spec = gain * mag * np.exp(1j * phase)
        y = np.fft.irfft(enh_spec, n=self.n_fft).real.astype(np.float32)
        y *= self._synthesis_window

        out = y[: self.hop_size] + self._overlap
        self._overlap = y[self.hop_size :].copy()
        return out.astype(np.float32, copy=False)
