# Example using PIO to create a UART RX interface.
#
# To make it work you'll need a wire connecting GPIO4 and GPIO3.
#
# Demonstrates:
#   - PIO shifting in data on a pin
#   - PIO jmp(pin) instruction
#   - PIO irq handler
#   - using the second core via _thread

# ruff: noqa: F821 - @asm_pio decorator adds names to function scope

import _thread
from machine import Pin, UART
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

UART_BAUD = 57_600 # Maximum viable baudrate
#UART_BAUD = 115200 # Unreliable - testing only

HARD_UART_TX_PIN = Pin(4, Pin.OUT)
PIO_RX_PIN = 3

@asm_pio(
    autopush=True,
    push_thresh=8,
    in_shiftdir=rp2.PIO.SHIFT_RIGHT,
    fifo_join=PIO.JOIN_RX,
)
def uart_rx_mini():
    # fmt: off
    # Wait for start bit
    wait(0, pin, 0)
    # Preload bit counter, delay until eye of first data bit
    set(x, 7)                 [10]
    # Loop 8 times
    label("bitloop")
    # Sample data
    in_(pins, 1)
    # Each iteration is 8 cycles
    jmp(x_dec, "bitloop")     [6]
    # fmt: on

@asm_pio(
    in_shiftdir=rp2.PIO.SHIFT_RIGHT,
)
def uart_rx():
    # fmt: off
    label("start")
    # Stall until start bit is asserted
    wait(0, pin, 0)
    # Preload bit counter, then delay until halfway through
    # the first data bit (12 cycles incl wait, set).
    set(x, 7)                 [10]
    label("bitloop")
    # Shift data bit into ISR
    in_(pins, 1)
    # Loop 8 times, each loop iteration is 8 cycles
    jmp(x_dec, "bitloop")     [6]
    # Check stop bit (should be high)
    jmp(pin, "good_stop")
    # Either a framing error or a break. Set a sticky flag
    # and wait for line to return to idle state.
    irq(block, 4)
    wait(1, pin, 0)
    # Don't push data if we didn't see good framing.
    jmp("start")
    # No delay before returning to start; a little slack is
    # important in case the TX clock is slightly too fast.
    label("good_stop")
    push(block)
    # fmt: on

# The handler for a UART break detected by the PIO.
def handler(sm):
    print("break", time.ticks_ms(), end=" ")


# Function for core1 to execute to write to the given UART.
def core1_task(uart, text):
    uart.write(text)


# Set up the hard UART we're going to use to print characters.
uart = UART(1, UART_BAUD, tx=HARD_UART_TX_PIN)

# Set up the state machine we're going to use to receive the characters.
sm = StateMachine(
    0,
    uart_rx, # Pick either uart_tx or uart_tx_mini
    freq=8 * UART_BAUD,
    in_base=Pin(PIO_RX_PIN, Pin.IN, Pin.PULL_UP),  # For WAIT, IN
    jmp_pin=Pin(PIO_RX_PIN, Pin.IN, Pin.PULL_UP),  # For JMP
)
sm.irq(handler)
sm.active(1)

sleep(2) # For oscilloscope
# When rebooted, the Pico makes around 11 ms negative pulse,
# which makes it waste most of the buffer.
# With this delay, first run the program, quickly start the
# before-stopped oscilloscope and have it measure all needed.
# You have 2 seconds to start the oscilloscope after starting
# this program. Do not start the oscilloscope first.

# Tell core 1 to print some text to UART 1
text = "123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 " # String "UU" in Ascii is 01010101 01010101 in binary, so it makes it easy to see on the oscilloscope
text = text + "\x04" # Ascii EOT (End of transmission) character
_thread.start_new_thread(core1_task, (uart, text))

# Echo characters received from PIO to the console.
while True:
    char = chr(sm.get(None, 24)) # No buffer, shift right by 24 before returning
    if char == "\x04":
        break
    elif char == "\x00":
        char = " "
    print(char, end="")
print()
