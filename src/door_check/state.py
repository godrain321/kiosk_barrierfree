import threading

door_tts_enabled = True
lock = threading.Lock()

def disable_door_tts():
    global door_tts_enabled
    with lock:
        door_tts_enabled = False

def enable_door_tts():
    global door_tts_enabled
    with lock:
        door_tts_enabled = True

def is_door_tts_enabled():
    with lock:
        return door_tts_enabled