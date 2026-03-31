# C++ / 硬件迁移说明

## 1. API 映射建议

Python:

- `ThreeAPipeline.process_frame(mic_frame, ref_frame)`

C++ 建议：

```cpp
void ProcessFrame(const float* mic, const float* ref, float* out, int frame_size);
```

这样可保证算法边界清晰，IO 与 DSP 解耦。

## 2. 数据约定

- 采样率：建议先固定 `16kHz`
- 帧长：建议 `160`（10ms）
- 数据格式：`float32`（原型）-> `int16` 或 `Q15`（量产）

## 3. 模块迁移优先级

1. AEC（对双讲与回声稳定性影响最大）
2. ANS（降低稳态噪声）
3. AGC（保证响度一致）
<<<<<<< ours
=======
4. DRC（控制峰值与动态范围）
>>>>>>> theirs

## 4. 一致性验证

- 使用同一组 `mic/ref` wav 作为黄金输入
- Python 导出每帧输出作为基准
- C++ 每帧对齐比对：
  - SNR
  - ERLE（针对 AEC）
  - 主观听感（MOS）

## 5. 工程实践建议

- 每个模块独立开关，便于线上回退
- 参数全部配置化，不硬编码
- 在硬件上优先确保无溢出、低延迟，再追求更激进降噪
