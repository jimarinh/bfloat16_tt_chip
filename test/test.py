# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

############################################################
# SPI Utilities
############################################################

async def spi_transfer_16(dut, tx_data):
    """
    SPI MODE 0
    CPOL = 0
    CPHA = 0
    MSB first
    """
    rx_data = 0
    for i in range(15, -1, -1):
        # Data valid before rising edge
        dut.ui_in[0].value = ((tx_data >> i) & 0x1) #MOSI
        # Half cycle
        await ClockCycles(dut.clk, 18)
        # Rising edge SCLK
        dut.ui_in[1].value = 1 
        # Sample MISO
        rx_data = ((rx_data << 1) | int(dut.uo_out[0].value))
        # Half cycle
        await ClockCycles(dut.clk, 18)
        # Falling edge SCLK
        dut.ui_in[1].value = 0 
    return rx_data

############################################################
# Main test
############################################################

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in[0].value = 0  #MOSI
    dut.ui_in[1].value = 0  #SCLK
    dut.ui_in[2].value = 1  #SS
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    
    ########################################################
    # SPI Frame: SUM with ACC=0.0
    ########################################################

    dut._log.info("SPI TEST: SUM ACC=0.0")

    dut.ui_in[2].value = 0
    rx1 = await spi_transfer_16(dut, 0b0000_0000_0000_0000)
    rx2 = await spi_transfer_16(dut, 0x4040)  # 3.0
    rx3 = await spi_transfer_16(dut, 0x4000)  # 2.0
    rx4 = await spi_transfer_16(dut, 0x3DCC)  # 0.1
    rx5 = await spi_transfer_16(dut, 0x0000)  # dummy
    dut.ui_in[2].value = 1

    assert rx1 == 0x0000, (f"ERROR rx0: expected=0x0000 received=0x{rx1:04X}")
    assert rx2 == 0x0000, (f"ERROR rx0: expected=0x0000 received=0x{rx2:04X}")
    assert rx3 == 0x4040, (f"ERROR rx0: expected=0x4040 received=0x{rx3:04X}")
    assert rx4 == 0x40A0, (f"ERROR rx0: expected=0x4000 received=0x{rx4:04X}")
    assert rx5 == 0x40A3, (f"ERROR rx0: expected=0x3DCC received=0x{rx5:04X}")
    
    await ClockCycles(dut.clk, 500)


    ########################################################
    # SPI Frame: SUB with ACC=1.0
    ########################################################

    dut._log.info("SPI TEST: SUB ACC=1.0")

    dut.ui_in[2].value = 0
    rx1 = await spi_transfer_16(dut, 0b1000_0001_0000_0000)
    rx2 = await spi_transfer_16(dut, 0x4040)  # 3.0
    rx3 = await spi_transfer_16(dut, 0x4000)  # 2.0
    rx4 = await spi_transfer_16(dut, 0x3DCC)  # 0.1
    rx5 = await spi_transfer_16(dut, 0x0000)  # dummy
    dut.ui_in[2].value = 1

    assert rx1 == 0x40A3, (f"ERROR rx0: expected=0x0000 received=0x{rx1:04X}")
    assert rx2 == 0x3F80, (f"ERROR rx0: expected=0x3F80 received=0x{rx2:04X}")
    assert rx3 == 0xC000, (f"ERROR rx0: expected=0xC000 received=0x{rx3:04X}")
    assert rx4 == 0xC080, (f"ERROR rx0: expected=0xC080 received=0x{rx4:04X}")
    assert rx5 == 0xC083, (f"ERROR rx0: expected=0xC083 received=0x{rx5:04X}")

    await ClockCycles(dut.clk, 500)
    

    ########################################################
    # SPI Frame: MPY with ACC=0.0
    ########################################################

    dut._log.info("SPI TEST: MPY ACC=0.0")

    dut.ui_in[2].value = 0
    rx1 = await spi_transfer_16(dut, 0b0001_0000_0000_0000)
    rx2 = await spi_transfer_16(dut, 0x4040)  # 3.0
    rx3 = await spi_transfer_16(dut, 0x4000)  # 2.0
    rx4 = await spi_transfer_16(dut, 0x3DCC)  # 0.1
    rx5 = await spi_transfer_16(dut, 0x0000)  # dummy
    dut.ui_in[2].value = 1

    assert rx1 == 0xC083, (f"ERROR rx0: expected=0x0000 received=0x{rx1:04X}")
    assert rx2 == 0x0000, (f"ERROR rx0: expected=0x0000 received=0x{rx2:04X}")
    assert rx3 == 0x0000, (f"ERROR rx0: expected=0x0000 received=0x{rx3:04X}")
    assert rx4 == 0x0000, (f"ERROR rx0: expected=0x0000 received=0x{rx4:04X}")
    assert rx5 == 0x0000, (f"ERROR rx0: expected=0x0000 received=0x{rx5:04X}")

    await ClockCycles(dut.clk, 500)

    ########################################################
    # SPI Frame: MPY with ACC=1.0
    ########################################################

    dut._log.info("SPI TEST: MPY ACC=1.0")

    dut.ui_in[2].value = 0
    rx1 = await spi_transfer_16(dut, 0b0001_0001_0000_0000)
    rx2 = await spi_transfer_16(dut, 0x4040)  # 3.0
    rx3 = await spi_transfer_16(dut, 0x4000)  # 2.0
    rx4 = await spi_transfer_16(dut, 0x3DCC)  # 0.1
    rx5 = await spi_transfer_16(dut, 0x0000)  # dummy
    dut.ui_in[2].value = 1

    await ClockCycles(dut.clk, 500)

    assert rx1 == 0x0000, (f"ERROR rx0: expected=0x0000 received=0x{rx1:04X}")
    assert rx2 == 0x3F80, (f"ERROR rx0: expected=0x3F80 received=0x{rx2:04X}")
    assert rx3 == 0x4040, (f"ERROR rx0: expected=0x4040 received=0x{rx3:04X}")
    assert rx4 == 0x40C0, (f"ERROR rx0: expected=0x40C0 received=0x{rx4:04X}")
    assert rx5 == 0x3F19, (f"ERROR rx0: expected=0x3F19 received=0x{rx5:04X}")
    
    dut._log.info("All SPI tests completed")
