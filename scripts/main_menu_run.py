import os
from src.io.serial_joystick import SerialJoystick
from src.ui.pygame_menu import PygameMenu

def main():
    items = [
        {"name": "Americano", "price": "3000"},
        {"name": "Latte", "price": "3500"},
        {"name": "Tea", "price": "3200"},
        {"name": "Sandwich", "price": "4500"},
    ]

    port = os.environ.get("JOY_PORT", "/dev/ttyACM0")
    js = SerialJoystick(port=port, baud=115200)
    js.open()

    menu = PygameMenu(items, title="Barrier-Free Kiosk Menu")
    cart = menu.run(event_source=js.read_event)

    js.close()
    print("CART:", cart)

if __name__ == "__main__":
    main()
