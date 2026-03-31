from __future__ import annotations

from dataclasses import dataclass, field

from .aec import NLMSAcousticEchoCanceller
from .agc import RMSAutomaticGainControl
from .ans import SpectralNoiseSuppressor
from .types import FloatArray


@dataclass(slots=True)
class ThreeAPipeline:
    """3A pipeline: AEC -> ANS -> AGC."""

    aec: NLMSAcousticEchoCanceller = field(default_factory=NLMSAcousticEchoCanceller)
    ans: SpectralNoiseSuppressor = field(default_factory=SpectralNoiseSuppressor)
    agc: RMSAutomaticGainControl = field(default_factory=RMSAutomaticGainControl)

    def process_frame(self, mic_frame: FloatArray, ref_frame: FloatArray | None = None) -> FloatArray:
        if ref_frame is None:
            ref_frame = mic_frame * 0.0

        aec_out = self.aec.process(mic_frame, ref_frame)
        ans_out = self.ans.process(aec_out)
        agc_out = self.agc.process(ans_out)
        return agc_out
