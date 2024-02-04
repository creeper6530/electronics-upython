# Borked when ran by Thonny. Run only by connecting to the Pico via PuTTY,
# running "from pio_uart_32bit import *" and then simply using "function(args)".

# It is recommended to clean up after testing by running "import machine; machine.reset()" instead of Ctrl-D

import _thread
from machine import Pin, reset
from rp2 import PIO, StateMachine, asm_pio
from time import sleep
from collections import deque
from time import sleep_ms

_UART_BAUD = const(57_600)
_TX_PIN = const(2)
_RX_PIN = const(3)


print(f"Baudrate: {_UART_BAUD}; Tx pin: {_TX_PIN}; Rx pin: {_RX_PIN}")

# Selftest only runs when loopback is detected
temp_tx = Pin(_TX_PIN, Pin.OUT, value=1)
temp_rx = Pin(_RX_PIN, Pin.IN, Pin.PULL_DOWN)
sleep_ms(2)
if temp_rx.value() == 1:
    SELFTEST = True
else: SELFTEST = False
del temp_tx
del temp_rx
sleep_ms(2)


@asm_pio(sideset_init=PIO.OUT_HIGH, out_init=PIO.OUT_HIGH, out_shiftdir=PIO.SHIFT_RIGHT, fifo_join=PIO.JOIN_TX, )
def uart_tx():
    # fmt: off
    # Block with TX deasserted until data available
    pull()
    # Initialise bit counter, assert start bit for 32 cycles
    set(x, 31)  .side(0)       [7]
    # Shift out 8 data bits, 8 execution cycles per bit
    label("bitloop")
    out(pins, 1)              [6]
    jmp(x_dec, "bitloop")
    # Assert stop bit for 8 cycles total (incl 1 for pull())
    nop()      .side(1)       [6]
    # fmt: on

@asm_pio(in_shiftdir=PIO.SHIFT_RIGHT, fifo_join=PIO.JOIN_RX, )
def uart_rx():
    # fmt: off
    label("start")
    # Stall until start bit is asserted
    wait(0, pin, 0)
    # Preload bit counter, then delay until halfway through
    # the first data bit (12 cycles incl wait, set).
    set(x, 31)                 [10]
    label("bitloop")
    # Shift data bit into ISR
    in_(pins, 1)
    # Loop 32 times, each loop iteration is 8 cycles
    jmp(x_dec, "bitloop")     [6]
    # Check stop bit (should be high)
    jmp(pin, "good_stop")
    # Either a framing error or a break.
    # Wait for line to return to idle state.
    wait(1, pin, 0)
    # Don't push data if we didn't see good framing.
    jmp("start")
    # No delay before returning to start; a little slack is
    # important in case the TX clock is slightly too fast.
    label("good_stop")
    push(block)
    # fmt: on


# Set up the state machine we're going to use to receive the characters.
sm_rx = StateMachine(
    0,
    uart_rx,
    freq=8 * _UART_BAUD,
    in_base=Pin(_RX_PIN, Pin.IN, Pin.PULL_UP),  # For WAIT, IN
    jmp_pin=Pin(_RX_PIN, Pin.IN, Pin.PULL_UP),  # For JMP
)

sm_tx = StateMachine(
    1,
    uart_tx,
    freq=8 * _UART_BAUD,
    sideset_base=Pin(_TX_PIN),
    out_base=Pin(_TX_PIN),
)
sm_tx.active(1)


# Each FIFO is 64 words long (totaling to 64*32 = 2 KiB of max size)
fifo_tx = deque((), 64)
fifo_rx = deque((), 64)

def core1_task(sm_tx, sm_rx, fifo_tx, fifo_rx): # Push and pull between PIO's and in-memory FIFOs to allow larger buffers
    sm_rx.active(1)
    while True:
        if sm_rx.rx_fifo() != 0: # Prevent trying to pull from empty FIFO to avoid blocking
            fifo_rx.append(sm_rx.get())
        
        if len(fifo_tx) > 0: # Prevent trying to pull from empty in-memory FIFO to avoid exception
            if sm_tx.tx_fifo() < 8: # Prevent trying to push into full FIFO to avoid blocking
                # Pop a character out of in-memory FIFO and push it into PIO's FIFO
                sm_tx.put(fifo_tx.popleft())
                
        sleep_ms(30)
        
_thread.start_new_thread(core1_task, (sm_tx, sm_rx, fifo_tx, fifo_rx))

def receive(len): # Input number of 32-bit words to fetch, returns an array of ints, each 1 byte big
    global fifo_rx
    words = []
    for _ in range(len):
        try: words.append(fifo_rx.popleft())
        except IndexError: break # Exit prematurely when FIFO is empty; blocking could be potentially used
        
    out =  []
    for i in words:
        for _ in range(4):
            out.append(i & 0xFF) # Get the last byte
            i = i >> 8
        
    return out

def transmit(array): # Input array of ints, each only 1 byte big (0 <= x < 256)
    global fifo_tx
    
    if type(array) is not list: raise ValueError("Input must be an array")
    for i in array:
        if type(i) is not int: raise ValueError("Array may only contain ints")
        if not (0 <= i < 256): raise ValueError("All ints must be 0 <= x < 256")
    
    # Pad the array to make its lenght a multiple of 4
    needed = 4 - (len(array) % 4)
    if needed == 4: needed = 0
    array.extend([0] * needed)
    
    # Iterate through 4 items at a time
    for i in range(0, len(array), 4):
        bytelist = array[i:i + 4]
        
        # Serialize list of bytes to an int, first item as least significant
        data = 0
        for j in range(4):
            data += bytelist[j] << 8*j
        
        fifo_tx.append(data)
        
print("DONE")
Pin(25, Pin.OUT).on() # Turn onboard LED on

if SELFTEST:
    transmit([0x55, 0x55, 0xAA, 0xAA, 12, 34, 56])
    sleep_ms(500)
    print(receive(3))

# DEBUG, allows for easier shutdown at the cost of no usage of module after "import" completes
# _thread.exit()

def clear(): print(ESC+"[2J"+ESC+"[H")