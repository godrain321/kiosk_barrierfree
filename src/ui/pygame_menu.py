import pygame

class PygameMenu:
    def __init__(self, items, title="Kiosk Menu", width=800, height=480):
        self.items = items
        self.title = title
        self.w = width
        self.h = height
        self.idx = 0
        self.cart = []

    def run(self, event_source=None):
        pygame.init()
        screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption(self.title)
        clock = pygame.time.Clock()

        font = pygame.font.SysFont(None, 48)
        small = pygame.font.SysFont(None, 32)

        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_UP:
                        self.idx = (self.idx - 1) % len(self.items)
                    elif ev.key == pygame.K_DOWN:
                        self.idx = (self.idx + 1) % len(self.items)
                    elif ev.key == pygame.K_RETURN:
                        self.cart.append(self.items[self.idx])
                    elif ev.key == pygame.K_ESCAPE:
                        running = False

            if event_source is not None:
                e = event_source()
                if e == "UP":
                    self.idx = (self.idx - 1) % len(self.items)
                elif e == "DOWN":
                    self.idx = (self.idx + 1) % len(self.items)
                elif e == "ENTER":
                    self.cart.append(self.items[self.idx])
                elif e == "BACK":
                    running = False

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
