import time
import serial
import re

class SerialJoystick:
    def __init__(self, port: str, baud: int = 115200, timeout: float = 0.02):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser = None
        self.buf = bytearray()

    def open(self):
        self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)
        time.sleep(0.3)
        try:
            self.ser.reset_input_buffer()
        except Exception:
            pass

    def close(self):
        if self.ser:
            self.ser.close()
            self.ser = None

    def _extract_lines(self):
        lines = []
        while True:
            idx_n = self.buf.find(b"\n")
            idx_r = self.buf.find(b"\r")

            if idx_n == -1 and idx_r == -1:
                break

            if idx_n != -1 and idx_r != -1:
                cut = min(idx_n, idx_r)
            else:
                cut = idx_n if idx_n != -1 else idx_r

            line = bytes(self.buf[:cut])
            del self.buf[:cut+1]

            line = line.strip()
            if line:
                lines.append(line)
        return lines

    def read_event(self):
        if not self.ser:
            return None

        try:
            data = self.ser.read(128)
        except Exception:
            return None

        if data:
            self.buf.extend(data)

        lines = self._extract_lines()
        if not lines:
            return None

        for raw in lines:
            text = raw.decode("utf-8", errors="ignore").strip().upper()
            m = re.search(r"\b(UP|DOWN|LEFT|RIGHT|ENTER|BACK)\b", text)
            if m:
                return m.group(1)
        return None
