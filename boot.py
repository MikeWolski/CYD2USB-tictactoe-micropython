from ili9341 import Display, color565
from xpt2046 import Touch
from machine import idle, Pin, SPI

class TicTacToe:
    CYAN = color565(0, 255, 255)
    PURPLE = color565(255, 0, 255)
    WHITE = color565(255, 255, 255)
    RED = color565(255, 0, 0)
    BLUE = color565(0, 0, 255)
    BLACK = color565(0, 0, 0)
    GRID_COLOR = color565(50, 50, 50)

    def __init__(self, display, spi2):
        self.display = display
        self.touch = Touch(spi2, cs=Pin(33), int_pin=Pin(36), int_handler=self.touchscreen_press)
        self.grid = [[None for _ in range(3)] for _ in range(3)]  # 3x3 board
        self.current_player = "X"  # Start with player "X"
        self.cell_width = self.display.width // 3
        self.cell_height = self.display.height // 3
        self.game_over = False
        self.draw_grid()

    def draw_grid(self):
        for i in range(1, 3):
            # Horizontal lines
            self.display.draw_hline(0, i * self.cell_height, self.display.width, self.GRID_COLOR)
            # Vertical lines
            self.display.draw_vline(i * self.cell_width, 0, self.display.height, self.GRID_COLOR)

    def draw_symbol(self, row, col, player):
        center_x = col * self.cell_width + self.cell_width // 2
        center_y = row * self.cell_height + self.cell_height // 2

        if player == "X":
            self.display.draw_line(center_x - 10, center_y - 10, center_x + 10, center_y + 10, self.RED)
            self.display.draw_line(center_x + 10, center_y - 10, center_x - 10, center_y + 10, self.RED)
        elif player == "O":
            self.display.draw_circle(center_x, center_y, 10, self.BLUE)

    def reset_game(self):
        self.grid = [[None for _ in range(3)] for _ in range(3)]  # Reset the board
        self.current_player = "X"  # Reset to player "X"
        self.game_over = False
        self.display.clear()
        self.draw_grid()  # Redraw the grid

    def touchscreen_press(self, x, y):
        if self.game_over:
            self.reset_game()
            return

        col = x // self.cell_width
        row = y // self.cell_height

        if self.grid[row][col] is None:
            self.grid[row][col] = self.current_player
            self.draw_symbol(row, col, self.current_player)

            if self.check_winner():
                self.draw_game_over_message(f"{self.current_player} WINS!")
                self.game_over = True
            elif self.check_draw():
                self.draw_game_over_message("DRAW!")
                self.game_over = True
            else:
                self.current_player = "O" if self.current_player == "X" else "X"

    def check_winner(self):
        # Check rows, columns, and diagonals for a win
        for i in range(3):
            if self.check_line(self.grid[i][0], self.grid[i][1], self.grid[i][2]):
                return True
            if self.check_line(self.grid[0][i], self.grid[1][i], self.grid[2][i]):
                return True

        # Check diagonals
        if self.check_line(self.grid[0][0], self.grid[1][1], self.grid[2][2]):
            return True
        if self.check_line(self.grid[0][2], self.grid[1][1], self.grid[2][0]):
            return True

        return False

    def check_line(self, cell1, cell2, cell3):
        return cell1 == cell2 == cell3 and cell1 is not None

    def check_draw(self):
        return all(cell is not None for row in self.grid for cell in row)

    def draw_game_over_message(self, message):
        self.display.draw_text8x8(10, self.display.height - 40, message, self.CYAN)
        self.display.draw_text8x8(10, self.display.height - 20, "Press anywhere to restart", self.CYAN)

    def go_to_sleep(self):
        idle()  # Put ESP32 to sleep when idle


def main():
    spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    display = Display(spi1, dc=Pin(2), cs=Pin(15), rst=Pin(0))

    bl_pin = Pin(21, Pin.OUT)
    bl_pin.on()

    spi2 = SPI(2, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))
    game = TicTacToe(display, spi2)

    try:
        while True:
            game.go_to_sleep()  # Put the ESP32 to sleep when idle

    except KeyboardInterrupt:
        print("\nCtrl-C pressed. Cleaning up and exiting...")
    finally:
        display.cleanup()


main()
