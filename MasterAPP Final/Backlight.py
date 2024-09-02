import time
import board
import neopixel_spi as neopixel
import sys

state = int(sys.argv[1])
brightness = int(sys.argv[2])

NUM_PIXELS = 35
PIXEL_ORDER = neopixel.GRBW
DELAY = 1

spi = board.SPI()

pixels = neopixel.NeoPixel_SPI(
    spi, NUM_PIXELS, pixel_order=(1, 0, 2, 3), auto_write=False
)


if state == 1:
    #turn on  backlight
    print("turning on backlight")
    for i in range(NUM_PIXELS):
        pixels[i] = (brightness,brightness,brightness,brightness)
    pixels.show()
                                                                                                                                                                                                                                                      
else:
    #turn off backlight 
    print("turning off backlight")
    for i in range(NUM_PIXELS):
        pixels[i] = (0,0,0,0)
    pixels.show()

      
