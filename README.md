# 3AAudioAlgorithm

Python reference implementation for **3A + DRC audio processing**:

- **AEC**: Acoustic Echo Cancellation (`NLMSAcousticEchoCanceller`)
- **ANS**: Automatic Noise Suppression (`SpectralNoiseSuppressor`)
- **AGC**: Automatic Gain Control (`RMSAutomaticGainControl`)
- **DRC**: Dynamic Range Compression (`DynamicRangeCompressor`)

> 目标：先做 Python 参考原型，再平滑迁移到 C++，最终面向 MCU / DSP 硬件实现。

## 1. Directory Layout

```text
3AAudioAlgorithm/
├── pyproject.toml
├── README.md
├── docs/
│   └── cplusplus_migration.md
├── cpp_achieve/
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── include/
│   └── src/
├── examples/
│   ├── export_golden_vectors.py
│   └── run_pipeline.py
├── src/
│   └── audio3a/
│       ├── __init__.py
│       ├── interfaces.py
│       ├── types.py
│       ├── io.py
│       ├── aec.py
│       ├── ans.py
│       ├── agc.py
│       ├── drc.py
│       ├── pipeline.py
│       └── runner.py
├── tests/
│   ├── test_docs.py
│   ├── test_golden_vectors.py
│   └── test_pipeline.py
└── sitecustomize.py
```

## 2. Install

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

## 3. Frame Contract

`ThreeAPipeline` 提供唯一 DSP 主入口：

```python
out_frame = pipeline.process_frame(mic_frame, ref_frame)
```

- `mic_frame`: 单通道 `float32`，长度固定 `160`，范围 `[-1, 1]`
- `ref_frame`: 单通道 `float32`，长度固定 `160`，可为 `None`
- 返回值：处理后的单通道 `float32`
- 内部处理顺序：`AEC -> ANS -> AGC -> DRC`
- 每个模块都支持：
  - `enabled`：旁路调试
  - `reset()`：清空运行状态

## 4. Offline WAV Processing

`audio3a.runner.process_wav_files(...)`

```python
from audio3a.runner import process_wav_files
from audio3a.types import AudioStreamConfig

cfg = AudioStreamConfig(sample_rate_hz=16000, channels=1, frame_size=160)
process_wav_files(
    mic_wav_path="data/mic_in.wav",
    ref_wav_path="data/ref_in.wav",
    out_wav_path="data/out.wav",
    stream_config=cfg,
)
```

## 5. Golden Vector Export

用于后续 C++ / DSP / 硬件逐帧对齐：

```bash
python examples/export_golden_vectors.py --output-dir artifacts/golden_vectors
```

输出文件：

- `artifacts/golden_vectors/pipeline_reference.npz`
- 包含 `mic`、`ref`、`out`、`sample_rate_hz`、`frame_size`

## 6. Migration Guidance

- 保持 `process_frame(mic, ref)` 作为唯一 DSP 入口
- 将 `AudioSource/AudioSink` 替换为 DMA / RingBuffer / 硬件驱动层
- 先完成浮点 C++ 逐帧对齐，再进入定点化
- 模块迁移顺序建议：`AGC -> DRC -> ANS -> AEC`
- 第一版 C++ 头文件/API 骨架位于 `cpp_achieve/`

详见 `docs/cplusplus_migration.md`。

## 7. Tests

```bash
python -m unittest discover -s tests
```
