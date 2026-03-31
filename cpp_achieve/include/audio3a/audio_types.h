#ifndef AUDIO3A_AUDIO_TYPES_H_
#define AUDIO3A_AUDIO_TYPES_H_

#include <cstddef>
#include <cstdint>

namespace audio3a {

inline constexpr std::int32_t kDefaultSampleRateHz = 16000;
inline constexpr std::int32_t kDefaultChannels = 1;
inline constexpr std::int32_t kDefaultFrameSize = 160;

struct AudioStreamConfig {
  std::int32_t sample_rate_hz = kDefaultSampleRateHz;
  std::int32_t channels = kDefaultChannels;
  std::int32_t frame_size = kDefaultFrameSize;

  [[nodiscard]] constexpr bool IsReferenceContract() const {
    return sample_rate_hz == kDefaultSampleRateHz &&
           channels == kDefaultChannels &&
           frame_size == kDefaultFrameSize;
  }
};

enum class StatusCode : std::int32_t {
  kOk = 0,
  kInvalidArgument = 1,
  kUnsupportedConfig = 2,
  kNullPointer = 3,
};

}  // namespace audio3a

#endif  // AUDIO3A_AUDIO_TYPES_H_
