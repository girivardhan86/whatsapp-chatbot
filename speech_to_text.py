from faster_whisper import WhisperModel

print("Loading Whisper model...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Whisper Ready")


def speech_to_text(audio_path):

    segments, info = model.transcribe(
        audio_path,
        beam_size=5
    )

    text = ""

    for segment in segments:
        text += segment.text + " "

    return text.strip()