import socket
from src.audio.tts import speak
from src.door_check.state import is_door_tts_enabled

HOST = "0.0.0.0"
PORT = 5000

WELCOME_TEXT = (
    "어서오세요. 키오스크를 통해 주문해주세요. "
    "키오스크는 출입문의 좌측, 음성이 나오는 곳에 위치해 있습니다."
)

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)

    print("[DOOR] 서버 대기 중...")

    conn, addr = server.accept()
    print("[DOOR] ESP32 연결됨:", addr)

    while True:
        data = conn.recv(1024)
        if not data:
            break

        msg = data.decode().strip()
        if msg == "WELCOME":
            if is_door_tts_enabled():
                print("[DOOR] 환영 음성 출력")
                speak(WELCOME_TEXT)
            else:
                print("[DOOR] 환영 음성 차단됨 (사람 인식 상태)")
