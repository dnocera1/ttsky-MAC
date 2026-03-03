## How it works

A 4-bit input Multiply Accumulate function that outputs 16 bits. On each clock cycle when enabled, it multiplies the top 4 bits of `ui_in` (Pin A) by the bottom for bits of `ui_in` (Pin B). This product is then added and accumulated with all previous products. and output as 16 bits Top 8 bits from `uio_out` and Bot 8 bits from `uo_out`. The accumulator wraps around at decimal value `16'd65535`. Setting `rst_n` low will clear the accumulator to zero. 

## How to test

 1. Set `rst_n` low for at least one clock cycle to reset the accumulator to 0, then
    release it high.
2. Set A on `ui_in[7:4]` and B on `ui_in[3:0]`.
3. Set `ena` high for one clock cycle to accumulate `A × B` into the accumulator.
4. Read the result: `uo_out[7:0]` holds the lower byte, `uio_out[7:0]` holds the upper byte.
5. Keep `ena` low between operations to hold the accumulator value, or apply `rst_n`
    to clear and start over.

Running the CocoTb test using make -B runs: 
    -Simple Single Multiplications Test
    -Accumulating Multiplications Test
    -Multiply by Zero Test
    -8+ bits Accumulation
    -Random Accumulation with Overflow Detection

## External hardware
None. 

