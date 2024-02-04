from machine import Pin, PWM, ADC
from utime import sleep, sleep_ms

input_pin = 28
input = ADC(input_pin)

on = False
while True:
    data = input.read_u16()
    print(f"{data}     ", end="\r")
    
    if data < 60000:
        if on == False:
            on = True
            print("BOOM ")
            sleep_ms(50)
            continue
    on = False
    sleep_ms(5)

# input = Pin(input_pin, mode=Pin.IN, pull=Pin.PULL_UP)
# 
# def rise(pin):
#     print("RISE")
#     
# def fall(pin):
#     print("FALL")
# 
# input.irq(trigger=Pin.IRQ_FALLING, handler=fall)
# input.irq(trigger=Pin.IRQ_RISING, handler=rise)
# 
# while True:
#     sleep(1)