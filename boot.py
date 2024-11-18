from ili9341 import Display, color565
from xpt2046 import Touch
from machine import idle, Pin, SPI


class Demo(object):
    CYAN = color565(0, 255, 255)
    PURPLE = color565(255, 0, 255)
    WHITE = color565(255, 255, 255)

    def __init__(self, display, spi2):  #Initialize box. Args: display (ILI9341): display object, spi2 (SPI): SPI bus
        self.display = display
        self.touch = Touch(spi2, cs=Pin(33), int_pin=Pin(36), int_handler=self.touchscreen_press)
        self.display.draw_text8x8(self.display.width // 2 - 32, self.display.height - 9, "TICTACTOE", self.WHITE, background=self.PURPLE) # Display initial message
        self.display.draw_hline(0, self.display.height // 3, self.display.width, 31404)
        self.display.draw_hline(0, self.display.height // 3 * 2, self.display.width, 31404)
        self.display.draw_vline(self.display.width // 3, 0, self.display.height, 31404)
        self.display.draw_vline(self.display.width // 3 * 2, 0, self.display.height, 31404)

    def touchscreen_press(self, x, y):
        # Process touchscreen press events.
        print("Display touched.")
        # Display coordinates
        self.display.draw_text8x8(self.display.width // 2 - 32, self.display.height - 9, "{0:03d}, {1:03d}".format(x, y), self.CYAN)
        # Draw circle
        self.display.draw_circle(x - 5, y - 5, 5, 22222)


def test():
    # Set up the display - ili9341. Baud rate of 40000000 seems about the max
    spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    display = Display(spi1, dc=Pin(2), cs=Pin(15), rst=Pin(0))
    
    bl_pin = Pin(21, Pin.OUT)
    bl_pin.on()
    
    # Set up the touch screen digitizer - xpt2046
    spi2 = SPI(2, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))

    Demo(display, spi2)

    try:
        while True:
            idle()

    except KeyboardInterrupt:
        print("\nCtrl-C pressed.  Cleaning up and exiting...")
    finally:
        display.cleanup()

test()