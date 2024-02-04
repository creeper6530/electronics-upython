from machine import Pin, PWM
from utime import sleep, sleep_ms

led_pin = 2
led = PWM(Pin(led_pin))
led.freq(5000)

buzz_pin = 3
buzz = PWM(Pin(buzz_pin))
buzz.duty_u16(32767)

def percent_to_u16(percent): # Přepočítá procentuální hodnotu na u16
    return int((percent / 100) * 65535)
print(f"TEST: 50 % equals {percent_to_u16(50)}")

x = 250
while True:
    while True:
        x -= 10
        
        print(x)
        led.duty_u16(percent_to_u16(int(x / 5) - 2))    
        buzz.freq(5 * x)
        sleep_ms(100)
        
        if x == 10:
            break
    while True:
        x += 10
        
        print(x)
        led.duty_u16(percent_to_u16(int(x / 5) - 2))    
        buzz.freq(5 * x)
        sleep_ms(100)
        
        if x == 250:
            break
        
    print("Cycle ended!")
