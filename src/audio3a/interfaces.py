from __future__ import annotations

from typing import Protocol

from .types import FloatArray


class ResettableProcessor(Protocol):
    enabled: bool

    def reset(self) -> None:
        ...


class MonoFrameProcessor(ResettableProcessor, Protocol):
    def process(self, frame: FloatArray) -> FloatArray:
        ...


class MonoReferenceProcessor(ResettableProcessor, Protocol):
    def process(self, mic_frame: FloatArray, ref_frame: FloatArray) -> FloatArray:
        ...
