from machine import Pin, PWM
from utime import sleep, sleep_ms

led_pin = 2
led = PWM(Pin(led_pin))
led.freq(1000)

def percent_to_u16(percent): # Přepočítá procentuální hodnotu na u16
    return int((percent / 100) * 65535)
print(f"TEST: 50 % equals {percent_to_u16(50)}")
led.duty_u16(32767)

x = 100
while True:
    x -= 10
    
    led.duty_u16(percent_to_u16(x))
    sleep_ms(500)
    
    if x == 10:
        x = 100