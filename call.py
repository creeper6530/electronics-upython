from machine import Pin, PWM
from utime import sleep, sleep_ms

buzz_pin = 1
buzz = PWM(Pin(buzz_pin))
buzz.duty_u16(0)
buzz.freq(425)

for _ in range(3):
    buzz.duty_u16(32767)
    sleep(1)
    buzz.duty_u16(0)
    sleep(4)
    
for _ in range(7):
    buzz.duty_u16(32767)
    sleep_ms(330)
    buzz.duty_u16(0)
    sleep_ms(330)