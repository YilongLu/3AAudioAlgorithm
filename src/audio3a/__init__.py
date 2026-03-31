"""audio3a - 3A audio processing reference package.

3A = AEC (echo cancellation), ANS (noise suppression), AGC (automatic gain control).
"""

from .aec import NLMSAcousticEchoCanceller
from .agc import RMSAutomaticGainControl
from .ans import SpectralNoiseSuppressor
from .drc import DynamicRangeCompressor
from .pipeline import ThreeAPipeline
from .types import AudioFrame, AudioStreamConfig

__all__ = [
    "AudioFrame",
    "AudioStreamConfig",
    "NLMSAcousticEchoCanceller",
    "SpectralNoiseSuppressor",
    "RMSAutomaticGainControl",
    "DynamicRangeCompressor",
    "ThreeAPipeline",
]
