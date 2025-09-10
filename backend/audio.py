"""
diarize_whisper.py
Minimal MVP: Transcribe + Diarize (Who Spoke What)
Requirements:
  pip install git+https://github.com/openai/whisper.git
  pip install pyannote.audio torch
"""

import whisper
from pyannote.audio import Pipeline

# ---- CONFIG ----
AUDIO_FILE = "audio.mp3"          # your input file
MODEL_SIZE = "base"               # whisper model: tiny, base, small, medium, large
HF_TOKEN = "YOUR_HF_TOKEN"        # replace with your HuggingFace token
# ----------------


def transcribe_with_whisper(audio_file, model_size="base"):
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_file)
    return result["segments"]  # [{start, end, text, ...}, ...]


def diarize_with_pyannote(audio_file, hf_token):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token=hf_token
    )
    diarization = pipeline(audio_file)
    return list(diarization.itertracks(yield_label=True))


def merge_transcript_and_diarization(segments, diarization):
    final_output = []
    for seg in segments:
        speaker_found = "Unknown"
        for turn, _, speaker in diarization:
            # check overlap between transcription and diarization segments
            if seg["start"] >= turn.start and seg["end"] <= turn.end:
                speaker_found = speaker
                break
        final_output.append({
            "speaker": speaker_found,
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"]
        })
    return final_output


def main():
    print("🔹 Transcribing with Whisper...")
    segments = transcribe_with_whisper(AUDIO_FILE, MODEL_SIZE)

    print("🔹 Performing diarization with Pyannote...")
    diarization = diarize_with_pyannote(AUDIO_FILE, HF_TOKEN)

    print("🔹 Merging results...")
    final_output = merge_transcript_and_diarization(segments, diarization)

    print("\n===== Diarized Transcript =====")
    for entry in final_output:
        print(f"[{entry['start']:.2f}s – {entry['end']:.2f}s] {entry['speaker']}: {entry['text']}")


if __name__ == "__main__":
    main()
