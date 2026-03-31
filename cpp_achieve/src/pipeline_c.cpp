#include "audio3a/pipeline.h"
#include "audio3a/pipeline_c.h"

#include <new>

namespace {

using audio3a::AudioStreamConfig;
using audio3a::PipelineParams;
using audio3a::StatusCode;
using audio3a::ThreeAPipeline;

struct audio3a_pipeline_handle {
  explicit audio3a_pipeline_handle(const AudioStreamConfig& config) : pipeline(config) {}
  ThreeAPipeline pipeline;
};

int32_t ToCStatus(StatusCode code) {
  return static_cast<int32_t>(code);
}

PipelineParams ToCppParams(const audio3a_pipeline_params_t& params) {
  PipelineParams cpp_params;
  cpp_params.aec.control.enabled = params.aec_enabled != 0;
  cpp_params.aec.step_size = params.aec_step_size;
  cpp_params.ans.control.enabled = params.ans_enabled != 0;
  cpp_params.ans.alpha_noise = params.ans_alpha_noise;
  cpp_params.agc.control.enabled = params.agc_enabled != 0;
  cpp_params.agc.target_rms = params.agc_target_rms;
  cpp_params.drc.control.enabled = params.drc_enabled != 0;
  cpp_params.drc.threshold_db = params.drc_threshold_db;
  return cpp_params;
}

}  // namespace

audio3a_pipeline_handle_t* audio3a_pipeline_init(const audio3a_stream_config_t* config) {
  if (config == nullptr) {
    return nullptr;
  }

  AudioStreamConfig cpp_config;
  cpp_config.sample_rate_hz = config->sample_rate_hz;
  cpp_config.channels = config->channels;
  cpp_config.frame_size = config->frame_size;

  return new (std::nothrow) audio3a_pipeline_handle(cpp_config);
}

void audio3a_pipeline_destroy(audio3a_pipeline_handle_t* handle) {
  delete handle;
}

int32_t audio3a_pipeline_reset(audio3a_pipeline_handle_t* handle) {
  if (handle == nullptr) {
    return AUDIO3A_STATUS_NULL_POINTER;
  }
  return ToCStatus(handle->pipeline.Reset());
}

int32_t audio3a_pipeline_set_params(audio3a_pipeline_handle_t* handle,
                                    const audio3a_pipeline_params_t* params) {
  if (handle == nullptr || params == nullptr) {
    return AUDIO3A_STATUS_NULL_POINTER;
  }
  return ToCStatus(handle->pipeline.SetParams(ToCppParams(*params)));
}

int32_t audio3a_pipeline_process(audio3a_pipeline_handle_t* handle,
                                 const float* mic,
                                 const float* ref,
                                 float* out,
                                 size_t frame_size) {
  if (handle == nullptr) {
    return AUDIO3A_STATUS_NULL_POINTER;
  }
  return ToCStatus(handle->pipeline.ProcessFrame(mic, ref, out, frame_size));
}
