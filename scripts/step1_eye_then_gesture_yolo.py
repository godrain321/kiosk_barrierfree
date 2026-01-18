import time
import cv2
from pathlib import Path
from picamera2 import Picamera2
from ultralytics import YOLO

EYE_HOLD_SEC = 3.0
GESTURE_STABLE_SEC = 3.0
CONF_THRES = 0.45
IMGSZ = 640

def find_haar_dir():
    candidates = [
        Path("/usr/share/opencv4/haarcascades"),
        Path("/usr/share/opencv/haarcascades"),
    ]
    for d in candidates:
        if (d / "haarcascade_frontalface_default.xml").exists() and (d / "haarcascade_eye.xml").exists():
            return d
    raise FileNotFoundError("Haar cascade not found. Install: sudo apt install -y opencv-data")

HAAR_DIR = find_haar_dir()
FACE_XML = HAAR_DIR / "haarcascade_frontalface_default.xml"
EYE_XML = HAAR_DIR / "haarcascade_eye.xml"

face_cascade = cv2.CascadeClassifier(str(FACE_XML))
eye_cascade = cv2.CascadeClassifier(str(EYE_XML))

def eyes_detected(frame_bgr) -> bool:
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)
    if len(faces) == 0:
        return False
    x, y, w, h = faces[0]
    roi = gray[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(roi, 1.2, 10)
    return len(eyes) >= 2

class StableLabel:
    def __init__(self, stable_sec: float):
        self.stable_sec = stable_sec
        self.label = None
        self.start_t = None

    def update(self, new_label):
        now = time.time()
        if new_label is None:
            self.label = None
            self.start_t = None
            return None, 0.0
        if self.label != new_label:
            self.label = new_label
            self.start_t = now
            return None, 0.0
        held = now - (self.start_t or now)
        if held >= self.stable_sec:
            return self.label, held
        return None, held

def decide_gesture_from_yolo(model: YOLO, frame_bgr):
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    res = model.predict(rgb, imgsz=IMGSZ, conf=CONF_THRES, verbose=False)[0]
    if res.boxes is None or len(res.boxes) == 0:
        return None, 0.0

    best_conf = 0.0
    best_cls = None
    for b in res.boxes:
        conf = float(b.conf[0])
        cls = int(b.cls[0])
        if conf > best_conf:
            best_conf = conf
            best_cls = cls

    if best_cls is None:
        return None, 0.0

    name = str(model.names.get(best_cls, best_cls)).lower()
    if "fist" in name:
        return "fist", best_conf
    if "palm" in name or "bojaegi" in name:
        return "palm", best_conf
    return None, best_conf

def main():
    model_path = Path.home() / "kiosk_barrierfree" / "models" / "palm_fist_y11n_best.pt"
    model = YOLO(str(model_path))

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    time.sleep(0.3)

    cv2.namedWindow("kiosk_step1", cv2.WINDOW_NORMAL)

    state = "EYE_HOLD"
    eye_hold_start = None
    stable = StableLabel(GESTURE_STABLE_SEC)

    while True:
        rgb = picam2.capture_array()
        frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        if state == "EYE_HOLD":
            ok = eyes_detected(frame)
            if ok:
                if eye_hold_start is None:
                    eye_hold_start = time.time()
                held = time.time() - eye_hold_start
                cv2.putText(frame, f"Hold still: {held:.1f}/{EYE_HOLD_SEC:.1f}s",
                            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                if held >= EYE_HOLD_SEC:
                    state = "GESTURE"
            else:
                eye_hold_start = None
                cv2.putText(frame, "Please stand still for 3 seconds",
                            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

        else:
            gesture, conf = decide_gesture_from_yolo(model, frame)
            decided, held = stable.update(gesture)
            cv2.putText(frame, f"Gesture={gesture} conf={conf:.2f} stable={held:.1f}/{GESTURE_STABLE_SEC:.1f}s",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            if decided == "fist":
                print("NORMAL MODE")
                break
            if decided == "palm":
                print("ACCESSIBLE MODE")
                break

        cv2.imshow("kiosk_step1", frame)
        if (cv2.waitKey(10) & 0xFF) == 27:
            break

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()