import subprocess
import tempfile
import os
import threading
from gtts import gTTS

# 🔴 현재 재생 중인 프로세스 (전역)
_current_proc = None
_lock = threading.Lock()


def speak(text: str):
    """
    항상 '가장 최신 음성만' 재생하는 TTS
    이전 음성은 즉시 중단됨
    """
    global _current_proc

    if not text:
        return

    with _lock:
        # 1️⃣ 이전 음성 중단
        if _current_proc is not None:
            try:
                _current_proc.kill()
            except Exception:
                pass
            _current_proc = None

        # 2️⃣ 새 음성 파일 생성
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        tts = gTTS(text=text, lang="ko")
        tts.save(path)

        # 3️⃣ 새 음성 재생
        _current_proc = subprocess.Popen(
            ["mpg123", "-q", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # 4️⃣ 재생 끝나면 파일 정리 (백그라운드)
        threading.Thread(
            target=_cleanup_when_done,
            args=(_current_proc, path),
            daemon=True
        ).start()


def _cleanup_when_done(proc, path):
    try:
        proc.wait()
    finally:
        try:
            os.remove(path)
        except Exception:
            pass
