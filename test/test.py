# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.triggers import RisingEdge
import random

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    async def reset_acc():
        dut.rst_n.value = 0
        await RisingEdge(dut.clk)
        dut.rst_n.value = 1

    async def mac_op(a, b):
     dut.ui_in.value = (a << 4) | b
     dut.ena.value = 1                 # enable for ONE cycle
     await RisingEdge(dut.clk)        # C1: accumulation scheduled as NBA
     dut.ena.value = 0                 # disable before next posedge
     await RisingEdge(dut.clk)        # C2: C1 NBA is now visible; no new accum
     return int(dut.uo_out.value)

    dut._log.info("Simple Single Multiplications Test")

    result = await mac_op(1, 1)   # 1 x 1 = 1
    assert result == 1;   
    await reset_acc()

    result = await mac_op(3, 4)   # 3 x 4 = 12
    assert result == 12; 
    await reset_acc()

    result = await mac_op(15, 15) # 15 x 15 = 225
    assert result == 225; 
    await reset_acc()

    dut._log.info("Test Accumulating Multiplications")

    result = await mac_op(2, 8) # 2 x 8 = 16
    assert result == 16; 

    result = await mac_op(1, 15) # 16 + (1 x 15)
    assert result == 31; 

    result = await mac_op(4, 4) # 31 + (4 x 4)
    assert result == 47; 

    await reset_acc()
        
    dut._log.info("Multiply by Zero Tests")

    result = await mac_op(1, 0) # 1 x 0 = 0 
    assert result == 0; 

    await reset_acc() 

    result = await mac_op(0, 5) # 5 x 0 = 0
    assert result == 0; 

    result = await mac_op(0, 0) # 0 x 0 = 0
    assert result == 0; 

    await reset_acc()

    dut._log.info("8+ bits Accumulation")

    result = await mac_op(15, 15) # 15 x 15 = 225 
    assert result == 225; 

    result = await mac_op(15, 15) # (15 x 15) + 225 = 450 (0x01C2)
    assert dut.uo_out.value == 194; 
    assert dut.uio_out.value == 1; 

    await reset_acc()

    dut._log.info("Random Accumulation with Overflow Detection")
    ref_acc = 0
    step = 0
    await reset_acc()

    while True:
        a = random.randint(0, 15)
        b = random.randint(0, 15)
        product = a * b
        step += 1

        if ref_acc + product > 0xFFFF:
            dut._log.info(
                f"OVERFLOW at step {step}: {a} x {b} = {product}, "
                f"acc {ref_acc} + {product} = {ref_acc + product} > 65535"
            )
            await mac_op(a, b)
            expected = (ref_acc + product) & 0xFFFF
            assert int(dut.uo_out.value) == (expected & 0xFF); 
            assert int(dut.uio_out.value) == (expected >> 8); 
            dut._log.info(f"Wrapped accumulator = {expected} (0x{expected:04X})")
            break

        ref_acc += product
        await mac_op(a, b)
        assert int(dut.uo_out.value) == (ref_acc & 0xFF); 
        assert int(dut.uio_out.value) == (ref_acc >> 8); 

    await reset_acc()
    dut._log.info("All tests passed!")
