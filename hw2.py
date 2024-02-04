from machine import Pin, PWM
from utime import sleep, sleep_ms

from utime import ticks_ms, ticks_diff

buzz_pin = 2
buzz = PWM(Pin(buzz_pin))
buzz.duty_u16(0)
buzz.freq(1000)

btn_pin = 3
button = Pin(btn_pin, mode=Pin.IN, pull=Pin.PULL_UP)

def button_press(pin):
    t2 = ticks_ms()
    
    global waiting
    if waiting:
        
        waiting = False
        print(f"Reaction time: {ticks_diff(t2, t1)} ms")
        
button.irq(trigger=Pin.IRQ_FALLING, handler=button_press)
waiting = False
sleep(5)
waiting = True

t1 = ticks_ms()
buzz.duty_u16(32768)
sleep_ms(100)
buzz.duty_u16(0)

while waiting:
    sleep_ms(100)