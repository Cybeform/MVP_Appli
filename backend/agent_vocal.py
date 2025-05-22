import os
import openai
import sounddevice as sd
import scipy.io.wavfile as wavfile

openai.api_key = os.getenv("OPENAI_API_KEY")

def record_audio(duration: int = 5, fs: int = 44100) -> str:
    wav_path = os.path.join("recordings", "question.wav")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    wavfile.write(wav_path, fs, recording)
    return wav_path

def recognize_audio(wav_file: str) -> str:
    with open(wav_file, "rb") as f:
        resp = openai.audio.transcriptions.create(
            file=f,
            model="whisper-1"
        )
    return resp.text

def ask_openai(prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 150) -> str:
    """
    Ancien : openai.ChatCompletion.create(...)
    Nouveau : openai.chat.completions.create(...)
    """
    resp = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    # la réponse texte est toujours dans choices[0].message.content
    return resp.choices[0].message.content

def speak(text: str) -> None:
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except ImportError:
        print("[agent_vocal] TTS non dispo, skip.")
