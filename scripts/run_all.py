import os
import sys
import subprocess
import re
from src.audio.tts import speak
from src.door_check.state import disable_door_tts
import threading
from src.door_check.server import run_server


ROOT = os.path.expanduser("~/kiosk_barrierfree")



def run_step1():
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT

    p = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.step1_eye_then_gesture_yolo"
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True
    )
    return (p.stdout or "") + "\n" + (p.stderr or "")

def detect_mode(log: str):
    if re.search(r"\bNORMAL MODE\b", log, re.IGNORECASE):
        return "NORMAL"
    if re.search(r"\bACCESSIBLE MODE\b", log, re.IGNORECASE):
        return "ACCESSIBLE"
    if "일반모드" in log or "(fist)" in log:
        return "NORMAL"
    if "시각장애인" in log or "(palm)" in log:
        return "ACCESSIBLE"
    return None

def pick_port():
    candidates = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0", "/dev/ttyUSB1"]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "/dev/ttyACM0"

def run_menu(port, skip_first_tts=False):
    env = os.environ.copy()
    env["JOY_PORT"] = port
    env["PYTHONPATH"] = ROOT + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
   
    if skip_first_tts:
        env["SKIP_FIRST_MENU_TTS"] ="1"
        
    return subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "main_menu_run.py")],
        cwd=ROOT,
        env=env
    ).returncode



def main():
    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    port = os.environ.get("JOY_PORT", pick_port())
    log = run_step1()
    mode = detect_mode(log)

    disable_door_tts()   # 문 열릴 때 음성나오는거 중지.

    print("\n=== STEP1 LOG (tail) ===")
    lines = [l for l in log.splitlines() if l.strip()]
    print("\n".join(lines[-30:]))

    if mode is None:
        print("\n[ERROR] Step1 mode not detected.")
        sys.exit(1)
        
    if mode == "ACCESSIBLE":
       
        speak(
            "시각장애인 모드입니다. "
            "정면에 설치된 조이스틱을 이용하여 메뉴를 고르실 수 있습니다. "
            "조이스틱을 누르시면 메뉴가 선택됩니다."
        )

    
    print(f"\n[OK] MODE = {mode}")
    print(f"[INFO] Starting MENU with JOY_PORT={port} ...\n")
    sys.exit(run_menu(port, skip_first_tts=(mode == "ACCESSIBLE")))
    
if __name__ == "__main__":
    main()
