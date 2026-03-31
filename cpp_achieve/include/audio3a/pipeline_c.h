#ifndef AUDIO3A_PIPELINE_C_H_
#define AUDIO3A_PIPELINE_C_H_

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum audio3a_status_code {
  AUDIO3A_STATUS_OK = 0,
  AUDIO3A_STATUS_INVALID_ARGUMENT = 1,
  AUDIO3A_STATUS_UNSUPPORTED_CONFIG = 2,
  AUDIO3A_STATUS_NULL_POINTER = 3,
};

typedef struct audio3a_stream_config {
  int32_t sample_rate_hz;
  int32_t channels;
  int32_t frame_size;
} audio3a_stream_config_t;

typedef struct audio3a_pipeline_params {
  float aec_step_size;
  float ans_alpha_noise;
  float agc_target_rms;
  float drc_threshold_db;
  uint8_t aec_enabled;
  uint8_t ans_enabled;
  uint8_t agc_enabled;
  uint8_t drc_enabled;
} audio3a_pipeline_params_t;

typedef struct audio3a_pipeline_handle audio3a_pipeline_handle_t;

audio3a_pipeline_handle_t* audio3a_pipeline_init(const audio3a_stream_config_t* config);
void audio3a_pipeline_destroy(audio3a_pipeline_handle_t* handle);
int32_t audio3a_pipeline_reset(audio3a_pipeline_handle_t* handle);
int32_t audio3a_pipeline_set_params(audio3a_pipeline_handle_t* handle,
                                    const audio3a_pipeline_params_t* params);
int32_t audio3a_pipeline_process(audio3a_pipeline_handle_t* handle,
                                 const float* mic,
                                 const float* ref,
                                 float* out,
                                 size_t frame_size);

#ifdef __cplusplus
}
#endif

#endif  // AUDIO3A_PIPELINE_C_H_
