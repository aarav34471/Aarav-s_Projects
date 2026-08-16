# Raspberry Pi Pico Morse Code Decoder

This embedded C program converts timed button presses into Morse-code letters and displays the decoded character on a seven-segment display.

## How It Works

- A button on GPIO 16 provides the input signal.
- Presses shorter than 250 ms are interpreted as dots; longer valid presses are dashes.
- A pause completes the current Morse sequence.
- The sequence is matched against an A-Z lookup table.
- The corresponding display pattern is written to a common-anode 5161BS seven-segment display.
- Invalid or overlong input produces an error pattern.

## Hardware

- Raspberry Pi Pico or compatible RP2040 board.
- Momentary push button with the configured pull-down input.
- 5161BS seven-segment display with suitable current-limiting resistors.
- GPIO wiring matching `include/seven_segment.h`.

## Building

Set `PICO_SDK_PATH` to a Raspberry Pi Pico SDK checkout, then run:

```bash
mkdir build
cd build
cmake ..
cmake --build .
```

Flash the resulting `pico_morse_decoder.uf2` file to the board. Serial output prints the interpreted dot/dash sequence and decoded letter.

## Limitations

- Timing thresholds are fixed and there is no adaptive calibration or button debouncing.
- A seven-segment display can only approximate some alphabetic characters.
- The decoder handles one letter at a time rather than words and spacing.
