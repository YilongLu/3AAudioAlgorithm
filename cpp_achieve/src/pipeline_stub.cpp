#include "audio3a/pipeline.h"

#include <algorithm>
#include <cstddef>

namespace audio3a {

ThreeAPipeline::ThreeAPipeline(AudioStreamConfig stream_config)
    : stream_config_(stream_config) {
  Reset();
}

StatusCode ThreeAPipeline::Reset() {
  state_ = {};
  state_.agc.smooth_gain = 1.0F;
  return ValidateConfig();
}

StatusCode ThreeAPipeline::SetParams(const PipelineParams& params) {
  params_ = params;
  return ValidateConfig();
}

const AudioStreamConfig& ThreeAPipeline::GetStreamConfig() const {
  return stream_config_;
}

const PipelineParams& ThreeAPipeline::GetParams() const {
  return params_;
}

const PipelineState& ThreeAPipeline::GetState() const {
  return state_;
}

StatusCode ThreeAPipeline::ProcessFrame(const float* mic,
                                        const float* ref,
                                        float* out,
                                        std::size_t frame_size) {
  const StatusCode config_status = ValidateConfig();
  if (config_status != StatusCode::kOk) {
    return config_status;
  }

  const StatusCode buffer_status = ValidateBuffers(mic, ref, out, frame_size);
  if (buffer_status != StatusCode::kOk) {
    return buffer_status;
  }

  const float* ref_or_silence = ref != nullptr ? ref : mic;
  std::copy_n(mic, frame_size, out);
  (void)ref_or_silence;
  return StatusCode::kOk;
}

StatusCode ThreeAPipeline::ValidateConfig() const {
  return stream_config_.IsReferenceContract() ? StatusCode::kOk
                                              : StatusCode::kUnsupportedConfig;
}

StatusCode ThreeAPipeline::ValidateBuffers(const float* mic,
                                           const float* ref,
                                           float* out,
                                           std::size_t frame_size) const {
  if (mic == nullptr || out == nullptr) {
    return StatusCode::kNullPointer;
  }
  if (frame_size != static_cast<std::size_t>(stream_config_.frame_size)) {
    return StatusCode::kInvalidArgument;
  }
  if (ref == out || mic == out) {
    return StatusCode::kInvalidArgument;
  }
  return StatusCode::kOk;
}

}  // namespace audio3a
