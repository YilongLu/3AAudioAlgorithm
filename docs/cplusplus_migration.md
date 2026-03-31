# C++ / MCU-DSP Migration Notes

## 1. Reference API

当前第一版 C++ 头文件/API 骨架已放在 `cpp_achieve/`。

Python 主入口：

- `ThreeAPipeline.process_frame(mic_frame, ref_frame=None)`

建议的 C++ 参考接口：

```cpp
struct AudioStreamConfig {
    int sample_rate_hz = 16000;
    int channels = 1;
    int frame_size = 160;
};

class ThreeAPipeline {
public:
    void Reset();
    void ProcessFrame(const float* mic, const float* ref, float* out, int frame_size);
};
```

建议保持 I/O 与 DSP 核心解耦，便于后续替换成 DMA、RingBuffer 或平台驱动。

## 2. Fixed Contract

- 采样率：`16 kHz`
- 通道数：`1`
- 帧长：`160 samples`（10 ms）
- 参考信号：可为空；为空时按全零参考处理
- 参考格式：原型阶段使用 `float32`，量产阶段再过渡到 `int16` / `Q15` / `Q31`

## 3. Migration-Friendly Changes In Python

- `ThreeAPipeline` 是唯一链路入口，适合直接映射成 `ProcessFrame`
- 所有模块都支持 `enabled` 旁路和 `reset()` 状态清零
- `AEC` 已改为环形历史缓冲，避免逐采样搬移整段历史
- `ANS` 使用固定 `320 FFT / 160 hop` 的状态化重叠处理
- `AGC` 和 `DRC` 的控制路径都已显式状态化，方便 C++ 逐帧复现

## 4. Suggested Migration Order

1. `AGC`
2. `DRC`
3. `ANS`
4. `AEC`

原因：前两者无参考支路、状态较简单，更适合先搭建 C++ 单元测试和数值对齐框架；`AEC` 最后迁移，能降低联调复杂度。

## 5. Alignment Validation

- 使用 `examples/export_golden_vectors.py` 导出 Python 黄金向量
- C++ 逐帧读取 `mic/ref`，输出 `out`
- 对比指标建议至少包含：
  - 最大绝对误差
  - 帧均方误差
  - 峰值/RMS 误差
  - `AEC` 的 ERLE

## 6. Next Steps For MCU / DSP

- 固定所有内部状态数组尺寸，避免运行时动态分配
- 统计各模块的内部数值范围，为定点化选择位宽
- 将参数和运行状态分离，便于做参数热更新和状态复位
- 板级联调阶段优先保留模块旁路开关，便于快速定位失真来源
