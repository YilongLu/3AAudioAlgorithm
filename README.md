# 3AAudioAlgorithm

Python reference implementation for **3A audio processing**:

- **AEC**: Acoustic Echo Cancellation (`NLMSAcousticEchoCanceller`)
- **ANS**: Automatic Noise Suppression (`SpectralNoiseSuppressor`)
- **AGC**: Automatic Gain Control (`RMSAutomaticGainControl`)

> 目标：先做 Python 原型，后续可平滑迁移到 C++ 并部署到硬件。

## 1. 目录规范

```text
3AAudioAlgorithm/
├── pyproject.toml
├── README.md
├── docs/
│   └── cplusplus_migration.md
├── src/
│   └── audio3a/
│       ├── __init__.py
│       ├── types.py          # 基础数据结构
│       ├── io.py             # 输入输出抽象 + WAV 适配
│       ├── aec.py            # AEC 算法
│       ├── ans.py            # ANS 算法
│       ├── agc.py            # AGC 算法
│       ├── pipeline.py       # 3A 主流水线
│       └── runner.py         # 文件级调用入口
├── examples/
│   └── run_pipeline.py
└── tests/
    └── test_pipeline.py
```

## 2. 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 3. 音频输入输出接口

### 3.1 帧级接口（推荐后续硬件/实时接入）

`ThreeAPipeline` 提供核心接口：

```python
out_frame = pipeline.process_frame(mic_frame, ref_frame)
```

- `mic_frame`: 近端麦克风单通道 `float32`，范围 `[-1, 1]`
- `ref_frame`: 远端参考（扬声器回采）单通道 `float32`，可为 `None`
- 返回：处理后的单通道 `float32`

### 3.2 文件级接口（离线验证）

`audio3a.runner.process_wav_files(...)`

```python
from audio3a.runner import process_wav_files
from audio3a.types import AudioStreamConfig

cfg = AudioStreamConfig(sample_rate_hz=16000, channels=1, frame_size=160)
process_wav_files(
    mic_wav_path="data/mic_in.wav",
    ref_wav_path="data/ref_in.wav",  # 可选
    out_wav_path="data/out.wav",
    stream_config=cfg,
)
```

## 4. 迁移到 C++ 的建议

- 保持 `process_frame(mic, ref)` 为唯一 DSP 入口（Python/C++ 同签名）
- `AudioSource/AudioSink` 抽象替换为硬件 DMA/RingBuffer
- 统一定点化策略：先在 Python 中固定增益与限幅范围，再在 C++ 定点实现
- 分模块迁移：AEC -> ANS -> AGC，逐个对齐测试向量

详见 `docs/cplusplus_migration.md`。

## 5. 测试

```bash
python -m unittest discover -s tests
```
