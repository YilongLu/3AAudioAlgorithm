#ifndef AUDIO3A_MODULES_H_
#define AUDIO3A_MODULES_H_

#include <array>
#include <cstddef>

#include "audio3a/audio_types.h"

namespace audio3a {

struct ModuleControl {
  bool enabled = true;
};

struct AecParams {
  ModuleControl control;
  std::size_t filter_length = 256;
  float step_size = 0.2F;
  float epsilon = 1.0e-6F;
  bool adaptation_enabled = true;
  float double_talk_ratio = 2.0F;
};

struct AnsParams {
  ModuleControl control;
  std::size_t n_fft = 320;
  std::size_t hop_size = 160;
  float alpha_noise = 0.95F;
  float over_subtraction = 1.2F;
  float floor_gain = 0.1F;
};

struct AgcParams {
  ModuleControl control;
  float target_rms = 0.1F;
  float max_gain_db = 20.0F;
  float noise_floor_rms = 1.0e-3F;
  float limiter_peak = 0.95F;
  float attack = 0.2F;
  float release = 0.95F;
};

struct DrcParams {
  ModuleControl control;
  float threshold_db = -18.0F;
  float ratio = 4.0F;
  float makeup_gain_db = 3.0F;
  float attack = 0.2F;
  float release = 0.98F;
};

struct PipelineParams {
  AecParams aec;
  AnsParams ans;
  AgcParams agc;
  DrcParams drc;
};

struct AecState {
  std::array<float, 256> weights{};
  std::array<float, 256> ref_history{};
  std::size_t head = 0;
};

struct AnsState {
  std::array<float, 161> noise_psd{};
  std::array<float, 320> analysis_state{};
  std::array<float, 160> overlap{};
};

struct AgcState {
  float smooth_gain = 1.0F;
};

struct DrcState {
  float gain_db_smooth = 0.0F;
  float envelope = 0.0F;
};

struct PipelineState {
  AecState aec;
  AnsState ans;
  AgcState agc;
  DrcState drc;
};

}  // namespace audio3a

#endif  // AUDIO3A_MODULES_H_
