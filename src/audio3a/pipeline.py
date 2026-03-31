from __future__ import annotations

from dataclasses import dataclass, field

from .aec import NLMSAcousticEchoCanceller
from .agc import RMSAutomaticGainControl
from .ans import SpectralNoiseSuppressor
from .drc import DynamicRangeCompressor
from .types import AudioStreamConfig, DEFAULT_FRAME_SIZE, FloatArray, as_float_mono_frame


@dataclass(slots=True)
class ThreeAPipeline:
    """3A+DRC pipeline: AEC -> ANS -> AGC -> DRC."""

    stream_config: AudioStreamConfig = field(default_factory=AudioStreamConfig)
    aec: NLMSAcousticEchoCanceller = field(default_factory=NLMSAcousticEchoCanceller)
    ans: SpectralNoiseSuppressor = field(default_factory=SpectralNoiseSuppressor)
    agc: RMSAutomaticGainControl = field(default_factory=RMSAutomaticGainControl)
    drc: DynamicRangeCompressor = field(default_factory=DynamicRangeCompressor)

    def __post_init__(self) -> None:
        if self.stream_config.frame_size != DEFAULT_FRAME_SIZE:
            raise ValueError("ThreeAPipeline expects the reference 160-sample frame contract")
        if self.ans.hop_size != self.stream_config.frame_size:
            raise ValueError("ANS hop_size must match stream_config.frame_size")

    def reset(self) -> None:
        self.aec.reset()
        self.ans.reset()
        self.agc.reset()
        self.drc.reset()

    def process_frame(self, mic_frame: FloatArray, ref_frame: FloatArray | None = None) -> FloatArray:
        mic = as_float_mono_frame(mic_frame, self.stream_config.frame_size)
        if ref_frame is None:
            ref = mic * 0.0
        else:
            ref = as_float_mono_frame(ref_frame, self.stream_config.frame_size)

        aec_out = self.aec.process(mic, ref)
        ans_out = self.ans.process(aec_out)
        agc_out = self.agc.process(ans_out)
        drc_out = self.drc.process(agc_out)
        return drc_out
