from machine import Pin, Timer

led_pin = 15
led = Pin(led_pin, Pin.OUT)

timer = Timer()
def toggler(timer):
    led.toggle()

led.value(1)
timer.init(freq=0.5, mode=Timer.PERIODIC, callback=toggler)