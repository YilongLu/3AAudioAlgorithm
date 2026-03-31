from audio3a.runner import process_wav_files
from audio3a.types import AudioStreamConfig

if __name__ == "__main__":
    cfg = AudioStreamConfig(sample_rate_hz=16000, channels=1, frame_size=160)
    process_wav_files(
        mic_wav_path="data/mic_in.wav",
        ref_wav_path="data/ref_in.wav",  # can be None if no far-end reference
        out_wav_path="data/out.wav",
        stream_config=cfg,
    )
