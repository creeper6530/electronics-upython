# Example using PIO to create a UART TX interface

# ruff: noqa: F821 - @asm_pio decorator adds names to function scope

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio

UART_BAUD = 57_600
PIN = 3


@asm_pio(sideset_init=PIO.OUT_HIGH, out_init=PIO.OUT_HIGH, out_shiftdir=PIO.SHIFT_RIGHT)
def uart_tx():
    # fmt: off
    # Block with TX deasserted until data available
    pull()
    # Initialise bit counter, assert start bit for 8 cycles
    set(x, 7)  .side(0)       [7]
    # Shift out 8 data bits, 8 execution cycles per bit
    label("bitloop")
    out(pins, 1)              [6]
    jmp(x_dec, "bitloop")
    # Assert stop bit for 8 cycles total (incl 1 for pull())
    nop()      .side(1)       [6]
    # fmt: on



sm = StateMachine(
    0,
    uart_tx,
    freq=8 * UART_BAUD,
    sideset_base=Pin(PIN),
    out_base=Pin(PIN)
)
sm.active(1)


# We can print characters from each UART by pushing them to the TX FIFO
def pio_uart_print(sm, s):
    for c in s:
        sm.put(ord(c))


pio_uart_print(sm, "U\x00") # Character U in Ascii is 01010101 in binary, so it makes it easy to see on the oscilloscope
