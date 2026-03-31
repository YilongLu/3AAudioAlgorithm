#ifndef AUDIO3A_PIPELINE_H_
#define AUDIO3A_PIPELINE_H_

#include "audio3a/audio_types.h"
#include "audio3a/modules.h"

namespace audio3a {

class ThreeAPipeline {
 public:
  explicit ThreeAPipeline(AudioStreamConfig stream_config = {});

  [[nodiscard]] StatusCode Reset();
  [[nodiscard]] StatusCode SetParams(const PipelineParams& params);
  [[nodiscard]] const AudioStreamConfig& GetStreamConfig() const;
  [[nodiscard]] const PipelineParams& GetParams() const;
  [[nodiscard]] const PipelineState& GetState() const;

  [[nodiscard]] StatusCode ProcessFrame(const float* mic,
                                        const float* ref,
                                        float* out,
                                        std::size_t frame_size);

 private:
  [[nodiscard]] StatusCode ValidateConfig() const;
  [[nodiscard]] StatusCode ValidateBuffers(const float* mic,
                                           const float* ref,
                                           float* out,
                                           std::size_t frame_size) const;

  AudioStreamConfig stream_config_;
  PipelineParams params_{};
  PipelineState state_{};
};

}  // namespace audio3a

#endif  // AUDIO3A_PIPELINE_H_
