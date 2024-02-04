from machine import Pin, ADC, PWM
from utime import sleep, sleep_ms

adc_pin = 26
trimmer = ADC(adc_pin)

led_pin = 15
led = PWM(Pin(led_pin))
led.freq(5000)

while True:
    data = 0
    no_of_msmnts = 100 # Počet měření
    
    for _ in range(0, no_of_msmnts):
        data += trimmer.read_u16()
    data /= no_of_msmnts # Zprůměruje "no_of_msmnts" měření 
    
    print(data)
    led.duty_u16(int(data))