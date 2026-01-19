import pygame
from src.audio.tts import speak
import os

skip_first = os.environ.get("SKIP_FIRST_MENU_TTS") == "1"

class PygameMenu:
    def __init__(self, items, title="Kiosk Menu", width=800, height=480):
        self.items = items
        self.title = title
        self.w = width
        self.h = height

        self.idx = 0
        self.cart = []

        # TTS 중복 방지
        self.last_spoken_idx = None

        # 상태 머신
        self.state = "BROWSE"      # BROWSE | CONFIRM
        self.pending_item = None  # 확인 중인 메뉴
        
        self.skip_next_focus_tts = skip_first

        

    def run(self, event_source=None):
        pygame.init()
        screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption(self.title)
        clock = pygame.time.Clock()

        font = pygame.font.SysFont(None, 48)
        small = pygame.font.SysFont(None, 32)

        running = True
        while running:

            # =========================
            # 1️⃣ 키보드 이벤트
            # =========================
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False

                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_UP:
                        self._handle_direction("UP")
                    elif ev.key == pygame.K_DOWN:
                        self._handle_direction("DOWN")
                    elif ev.key == pygame.K_RETURN:
                        self._handle_enter()
                    elif ev.key == pygame.K_ESCAPE:
                        running = False

            # =========================
            # 2️⃣ 조이스틱 이벤트
            # =========================
            if event_source is not None:
                e = event_source()
                if e in ("UP", "DOWN", "LEFT", "RIGHT"):
                    self._handle_direction(e)
                elif e == "ENTER":
                    self._handle_enter()
                elif e == "BACK":
                    running = False

            # =========================
            # 3️⃣ 메뉴 포커스 TTS (BROWSE 상태에서만)
            # =========================
            if self.state == "BROWSE":
                if self.skip_next_focus_tts:
                    self.skip_next_focus_tts = False
                    self.last_spoken_idx = self.idx
                elif self.idx != self.last_spoken_idx:
                    item = self.items[self.idx]
                    speak(f"{item['name']} {item['price']}원")
                    self.last_spoken_idx = self.idx

            # =========================
            # 4️⃣ 화면 렌더링
            # =========================
            screen.fill((15, 15, 18))

            title_surf = font.render(self.title, True, (240, 240, 240))
            screen.blit(title_surf, (30, 20))

            y0 = 100
            for i, item in enumerate(self.items):
                name = item["name"]
                price = item.get("price", "")
                text = f"{name}  {price}"
                color = (80, 200, 120) if i == self.idx else (220, 220, 220)
                surf = font.render(text, True, color)
                screen.blit(surf, (60, y0 + i * 60))

            cart_text = f"Selected: {len(self.cart)}"
            cart_surf = small.render(cart_text, True, (200, 200, 200))
            screen.blit(cart_surf, (30, self.h - 50))

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        return self.cart

    # =========================
    # 🔽 방향 입력 처리
    # =========================
    def _handle_direction(self, direction):
        if self.state == "CONFIRM":
            # ❌ 주문 취소
            speak("원하시는 메뉴를 선택해 주세요.")
            self.state = "BROWSE"
            self.pending_item = None
            
            # 🔴 메뉴 복귀 시 포커스 TTS 1회 스킵
            self.skip_next_focus_tts = True
            return

        # 메뉴 이동
        if direction == "UP":
            self.idx = (self.idx - 1) % len(self.items)
        elif direction == "DOWN":
            self.idx = (self.idx + 1) % len(self.items)

    # =========================
    # 🔘 ENTER 처리
    # =========================
    def _handle_enter(self):
        if self.state == "BROWSE":
            # 1️⃣ 메뉴 선택 → 확인 단계
            self.pending_item = self.items[self.idx]
            speak(
                f"{self.pending_item['name']}을 선택하였습니다. "
                "이 메뉴로 주문하시겠습니까? "
                "맞으면 조이스틱을 한번 더 누르고 "
                "아니면 조이스틱을 아래로 움직여 주세요."
            )
            self.state = "CONFIRM"

        elif self.state == "CONFIRM":
            # 2️⃣ 주문 확정
            self.cart.append(self.pending_item)
            speak(f"{self.pending_item['name']} 주문이 완료되었습니다.")
            self.pending_item = None
            self.state = "BROWSE"
                # 🔴 다음 포커스 TTS 한 번 스킵
            self.skip_next_focus_tts = True
