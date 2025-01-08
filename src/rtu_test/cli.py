# SPDX-FileCopyrightText: 2025-present DaneSlattery <dane_s@umantec.net>
#
# SPDX-License-Identifier: MIT
import click
import asyncio
from rtu_test.__about__ import __version__
# from rtu_test.modbus import connect, read_input_1, set_output, enumerature_tty
import rtu_test.modbus as modbus

@click.command()
@click.help_option(*("--help", "-h"))
@click.version_option(__version__, "-V", "--version")
def rtu_test():
    click.echo(f"RTU Tester  ")
    asyncio.run(start_menu())
    # menu = "main"

    # while True:
    #     if menu == "main":
    #         click.echo("Main Menu:")
    #         click.echo("    s: start")
    #         click.echo("    l: list ports")
    #         click.echo("    q: quit")
    #         char = click.getchar()
    #         if char == "s":
    #             menu = "start"
    #         elif char == "q":
    #             menu = "quit"
    #         elif char == "l":
    #             menu = "list"
    #         else:
    #             click.echo("Invalid input")
    #     elif menu == "start":
    #         menu = start_menu()
    #     elif menu == "list":
    #         click.echo("List serial ports")
    #         ports = enumerature_tty()
    #         click.echo(len(ports))
    #         for port in ports:
    #             click.echo(port)
    #         click.echo("    b: back")
    #         char = click.getchar()
    #         if char == "b":
    #             menu = "main"
    #         else:
    #             click.echo("Invalid input")
    #     elif menu == "quit":
    #         return


async def start_menu():

    click.echo("Start RTU Test")

    is_connected = click.confirm("Is the RTU connected and powered?")

    if not is_connected:
        click.echo("Connect the RTU")
        exit(1)

    try:
        client =await modbus.connect("/dev/ttyUSB0")
    except Exception:
        click.echo("RS485 USB Failed to connect.")
        exit(1)


    click.echo("1. Print All")
    await print_all(client)

    if not click.confirm("Proceed?"):
        exit(1)
    
    click.echo("2. Set All Outputs High")
    result =await modbus.set_digi_output(client,modbus.GPIO.ALL,0xffff)
    if result.isError():
        click.echo(f"Failed to set all high, result={result}")
        exit(1)

    if not click.confirm("All outputs high?"):
        click.echo("Fail, output not high")

        exit(1)
    
    click.echo("3. Set All Inputs High")
    click.pause("Hit any key when all inputs are set high.")
    result = await modbus.get_digi_input(client,modbus.GPIO.ALL)
    if result != 0b0000_0000_0000_1111:
        click.echo("Fail, input not high")
        exit(1)

    # set_output(client, 1)
    # click.echo("Pulse Out 2")
    # click.echo("Pulse Out 3")
    # click.echo("Pulse Out 4")
    # click.confirm("Did all outputs pulse?")

    # click.echo("Set Out 1")
    # click.echo("Set Out 2")
    # click.echo("Set Out 3")
    # click.echo("Set Out 4")

    # click.confirm("Did all outputs get set?")

    # click.confirm("Switch all inputs to 1")

    # click.echo("Check In 1")
    # click.echo("Check In 2")
    # click.echo("Check In 3")
    # click.echo("Check In 4")

    # click.confirm("Pulse Each PC ")

    # click.echo("Check PC 1")
    # click.echo("Check PC 2")

    # click.confirm("Disconnect RTU power")
    # click.echo("Polling RTU until dead")
    # click.echo("RTU Dead")
    # click.confirm("Reconnect RTU power")

    # click.echo("Check Out 1")
    # click.echo("Check Out 2")
    # click.echo("Check Out 3")
    # click.echo("Check Out 4")

    # click.echo("All outputs remembered. Test Pass.")
    exit(0)


async def print_all(client:modbus.AsyncModbusSerialClient):
    digi_out =await  modbus.get_digi_output(client,modbus.GPIO.ALL)
    click.echo(f"Out = \t{digi_out:010b}")
    
    out_settings = []

    for dig_out in [modbus.GPIO.IO1,modbus.GPIO.IO2,modbus.GPIO.IO3,modbus.GPIO.IO4,]:
        setting = await modbus.get_digi_output_config(client,dig_out)
        click.echo(f"Out Conf {dig_out} = \t{setting}")
        out_settings.append(setting)

    digi_in =await modbus.get_digi_input(client,modbus.GPIO.ALL)
    click.echo(f"In = \t{digi_in:010b}")

    analogs = []
    for a in modbus.AnalogIn:
        analog = await modbus.get_analog_input(client,a)
        click.echo(f"Analog {a} = \t{analog}")
        analogs.append(analog)


    pcs = []
    for pc in modbus.PulseCounter:
        count =await modbus.get_pulse_count(client,pc)
        click.echo(f"PC {pc} = \t{count}")
        pcs.append(count)

    
