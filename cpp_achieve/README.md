# C++ API Skeleton

This directory hosts the first C++ API skeleton for the `3AAudioAlgorithm` pipeline.

## Goals

- Mirror the Python frame contract: `16 kHz`, mono, `160` samples per frame
- Keep DSP processing decoupled from file / hardware I/O
- Separate parameters from mutable runtime state
- Provide both C++ class APIs and a stable C ABI wrapper for embedded integration

## Layout

- `include/audio3a/audio_types.h`: shared constants and config types
- `include/audio3a/modules.h`: module parameter/state declarations
- `include/audio3a/pipeline.h`: C++ pipeline class API
- `include/audio3a/pipeline_c.h`: C ABI wrapper
- `src/pipeline_stub.cpp`: placeholder implementation with contract checks

## Next Steps

- Implement `AecModule`, `AnsModule`, `AgcModule`, and `DrcModule`
- Load Python golden vectors and verify frame-by-frame alignment
- Add fixed-point simulation helpers before MCU / DSP bring-up
