# src/audio/tts.py
from gtts import gTTS
import tempfile
import os
import subprocess
import threading

def speak(text, lang="ko"):
    def _play():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts = gTTS(text=text, lang=lang)
            tts.save(fp.name)

        # mpg123이 가장 안정적
        subprocess.run(
            ["mpg123", "-q", fp.name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        os.remove(fp.name)

    # 🔑 중요: UI 멈추지 않게 스레드로 실행
    threading.Thread(target=_play, daemon=True).start()
