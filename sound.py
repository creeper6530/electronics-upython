from machine import Pin, PWM
from utime import sleep, sleep_ms

buzz_pin = 2
buzz = PWM(Pin(buzz_pin))
buzz.duty_u16(32767)

x = 100
while True:
    x -= 10
    
    buzz.freq(5 * x)
    sleep_ms(100)
    
    if x == 10:
        x = 100