# SPDX-FileCopyrightText: 2025-present DaneSlattery <dane_s@umantec.net>
#
# SPDX-License-Identifier: MIT
import time
import click
import asyncio
from rtu_test.__about__ import __version__
import rtu_test.modbus as modbus
from enum import Enum, auto


@click.command()
@click.argument("comport")
@click.help_option(*("--help", "-h"))
@click.version_option(__version__, "-V", "--version")
def rtu_test(comport):
    click.clear()
    click.echo("RTU Tester Version " +
               click.style(f"[{__version__}]", underline=True))
    click.echo("This tester confirms functionality of the RTU by testing:")
    click.echo("\tDigital Outputs")
    click.echo("\tDigital Inputs")
    click.echo("\tDigital Output Default State (after reboot)")
    click.echo("\tPulse Counters")
    click.echo("\tAnalog Inputs")
    click.echo("")
    click.echo(
        "Before and After the test passes, all registers will be reset to their default state")
    click.echo(
        "If the test fails, the user must debug the RTU and RTU test stand.")

    click.secho("")

    asyncio.run(full_test(comport))


class TestState(Enum):
    START = auto()
    CONNECT = auto()
    PRINT_START = auto()
    SET_OUTPUTS_HIGH = auto()
    SET_INPUTS_HIGH = auto()
    SET_REMEMBERED = auto()
    CHECK_PULSE_COUNT = auto()
    CHECK_ANALOG_1 = auto()
    CHECK_ANALOG_2 = auto()
    CHECK_ANALOG_3 = auto()
    CHECK_ANALOG_4 = auto()
    FINISH = auto()
    UNREACHABLE = auto()

    def next(self):
        if self is TestState.UNREACHABLE:
            return TestState.UNREACHABLE
        return TestState(self.value + 1)


class Transition(Enum):
    PROCEED = auto()
    QUIT = auto()
    RETRY = auto()


async def start():
    is_connected = click.confirm("Is the RTU connected and powered?")
    if not is_connected:
        click.secho("Connect the RTU", fg="magenta")
        return Transition.RETRY

    return Transition.PROCEED


async def connect(comport):

    try:
        client = await modbus.connect(comport)
        return (Transition.PROCEED, client)
    except Exception:
        click.echo("RS485 <-> USB Failed to connect. Plug in the Adapter")
        return (Transition.RETRY, None)


def proceed(message="Choose action", proceed=True):
    click.secho(f"\n {message} ")
    if proceed:
        click.secho(" \t p - proceed", fg="green")
    click.secho(" \t r - retry", fg="yellow")
    click.secho(" \t q - quit", fg="red")
    my_char = click.getchar()
    match my_char:
        case "p":
            if proceed:
                return Transition.PROCEED

        case "r":
            return Transition.RETRY
        case "q":
            return Transition.QUIT

    return Transition.RETRY


async def print(client):
    # Step 1
    #
    #

    click.secho("Print All", fg="green", bold=True)
    await print_all(client)
    return proceed()


async def set_outputs_high(client):
    # Step 2
    #
    #
    click.secho("Set All Outputs High", fg="green", bold=True)
    result = await modbus.set_digi_output(client, modbus.GPIO.ALL, 0xffff)

    if result.isError():
        click.secho(f"FAIL. Cannot set all outputs High, result={
                    result}", fg="red")
        return proceed(proceed=False)

    if not click.confirm("Confirm all outputs are set High."):
        click.secho(f"FAIL. User observed.", fg="red")
        return proceed(proceed=False)

    click.secho(f"PASS. All outputs are High.", fg="green")
    return Transition.PROCEED


async def set_outputs_low(client):
    # Step 2
    #
    #
    click.secho("Set All Outputs Low", fg="green", bold=True)
    result = await modbus.set_digi_output(client, modbus.GPIO.ALL, 0x0000)

    if result.isError():
        click.secho(f"FAIL. Cannot set all outputs Low, result={
                    result}", fg="red")
        return proceed(proceed=False)

    if not click.confirm("Confirm all outputs are set Low."):
        click.secho(f"FAIL. User observed.", fg="red")
        return proceed(proceed=False)

    click.secho(f"PASS. All outputs are Low.", fg="green")
    return Transition.PROCEED


async def set_inputs_high(client):
    # Step 2
    #
    #
    click.secho("Test All Inputs High \n", fg="green", bold=True)
    click.pause("Set all inputs High. Press any key to continue")
    result = await modbus.get_digi_input(client, modbus.GPIO.ALL)
    if result != 0b0000_0000_0000_1111:
        click.secho(f"FAIL. Not all inputs are High, value = {
                    result:08b}", fg="red")
        return proceed(proceed=False)
    click.secho(f"PASS. All inputs are High, value = {
        result:08b}", fg="green")
    return Transition.PROCEED


async def set_remembered(client):
    # Step 4
    #
    #
    click.secho("Set All Digital Out Remember", fg="green", bold=True)

    for dig_out in [modbus.GPIO.IO1, modbus.GPIO.IO2, modbus.GPIO.IO3, modbus.GPIO.IO4,]:
        result = await modbus.set_digi_output_config(client, dig_out)
        if result.isError():
            click.echo(f"FAIL. Cannot set digital output config {dig_out}")
            return proceed(proceed=False)
        click.echo(f"Set {dig_out} dig out Remember")

    click.pause("Power down the RTU. Press any key to continue")

    timer = range(30)  # 30 seconds
    click.echo(f"Wait {timer.stop} seconds for capacitor to die")
    with click.progressbar(timer, label="Waiting...", fill_char=click.style("#", fg="green")) as bar:
        for _ in bar:
            time.sleep(1)

    click.echo("If the bus light has stopped flashing")
    click.pause("Power up the RTU. Press any key to continue")

    # Step 5
    #
    #
    click.echo("Check All Digital Out Remembered")
    result: int = await modbus.get_digi_output(client, modbus.GPIO.ALL)
    if (result & 0b0000_0000_0000_1111) != 0b1111:
        click.secho("FAIL. outputs not high", fg="red")
        return proceed(proceed=False)
    click.secho(f"""PASS. All outputs are High, value = {
        result:08b}""", fg="green")
    return Transition.PROCEED


async def test_pulse_count(client):
    # Step 6
    #
    #
    click.secho("Check Pulse Count", fg="green", bold=True)
    click.pause("Pulse each counter 5 times. Press any key to continue")

    pc1 = await modbus.get_pulse_count(client, modbus.PulseCounter.IO1)
    pc2 = await modbus.get_pulse_count(client, modbus.PulseCounter.IO2)
    click.echo(f"Pulse Counter 1 = {pc1}")
    click.echo(f"Pulse Counter 2 = {pc2}")
    if (pc1[1] == 0) or (pc2[1] == 0):
        click.secho("FAIL. Did not detect pulse counts.", fg="red")
        proceed(proceed=False)

    click.secho("PASS. Detected pulse counts.", fg="green")
    return Transition.PROCEED


async def test_analog(client, analog: modbus.AnalogIn):
    # Step 7
    #
    #
    MAX_DEVIATION = 2
    click.secho(f"Check Analog {analog}", fg="green", bold=True)

    click.pause(f"Set Analog {analog} to min. Press any key to continue")

    analog_min = await modbus.get_analog_input(client, analog)

    click.echo(f"Analog = {analog_min}")

    if not ((4-MAX_DEVIATION) <= analog_min <= (4+MAX_DEVIATION)):
        click.secho("FAIL, analog out of range", fg="red")
        return proceed(proceed=False)

    click.pause(f"Set Analog {analog} to 10 then press any key.")

    analog_mid = await modbus.get_analog_input(client, analog)

    click.echo(f"Analog = {analog_mid}")
    if not ((10-MAX_DEVIATION) <= analog_mid <= (10+MAX_DEVIATION)):
        click.secho("FAIL, analog out of range", fg="red")
        return proceed(proceed=False)

    click.pause(f"Set Analog {analog} to max then press any key.")

    analog_max = await modbus.get_analog_input(client, analog)

    click.echo(f"Analog = {analog_max}")
    if not ((20-MAX_DEVIATION) <= analog_max <= (20+MAX_DEVIATION)):
        click.secho("FAIL, analog out of range", fg="red")
        return proceed(proceed=False)

    click.secho(f"PASS. Analog {analog} in range", fg="green")
    return Transition.PROCEED


async def reset_all(client):
    click.secho("Reset All", fg="green", bold=True)
    result = await modbus.reset_pulse_count(client)
    if result.isError():
        click.echo("Failed to reset pulse count")
        proceed(proceed=False)
    click.echo("Reset Pulse Count")

    for dig_out in [modbus.GPIO.IO1, modbus.GPIO.IO2, modbus.GPIO.IO3, modbus.GPIO.IO4,]:
        result = await modbus.set_digi_output_config(client, dig_out, modbus.DigOutDefaultState.OFF)
        if result.isError():
            click.echo(f"Failed to set out conf {dig_out}")
            exit(1)
        click.echo(f"Set {dig_out} dig out off")

    result = await modbus.set_digi_output(client, modbus.GPIO.ALL, 0x0000)
    if result.isError():
        click.echo(f"Failed to reset outputs {dig_out}")
        exit(1)


async def full_test(comport):

    click.echo("Start RTU Test")

    state = TestState.START
    transition = Transition.PROCEED

    while True:
        match state:
            case TestState.START:
                transition = await start()
            case TestState.CONNECT:
                (transition, client) = await connect(comport)
            # case TestState.PRINT_START:
            #     transition = await print(client)
            case TestState.SET_OUTPUTS_HIGH:
                transition = await set_outputs_high(client)
            # case TestState.SET_INPUTS_HIGH:
            #     transition = await set_inputs_high(client)
            # case TestState.SET_REMEMBERED:
            #     transition = await set_remembered(client)
            # case TestState.CHECK_PULSE_COUNT:
            #     transition = await test_pulse_count(client)
            # case TestState.CHECK_ANALOG_1:
            #     transition = await test_analog(client, modbus.AnalogIn.IO1)
            # case TestState.CHECK_ANALOG_2:
            #     transition = await test_analog(client, modbus.AnalogIn.IO2)
            # case TestState.CHECK_ANALOG_3:
            #     transition = await test_analog(client, modbus.AnalogIn.IO3)
            # case TestState.CHECK_ANALOG_4:
            #     transition = await test_analog(client, modbus.AnalogIn.IO4)
            case TestState.FINISH:
                transition = await reset_all(client)
                transition = await print(client)
                transition = Transition.QUIT
            case TestState.UNREACHABLE:
                transition = Transition.QUIT

        # click.echo(f"Transition: {transition}")
        match transition:
            case Transition.PROCEED:
                state = state.next()
                # click.echo(f"Move to stage {state}")
            case Transition.QUIT:
                click.echo("Quit")
                exit(1)
            case Transition.RETRY:
                # click.echo(f"Retry stage {state}")
                pass
            case _:
                exit(1)

    # click.echo("Success! ")
    # exit(0)


async def print_all(client: modbus.AsyncModbusSerialClient):
    digi_out = await modbus.get_digi_output(client, modbus.GPIO.ALL)
    click.echo(f"Out = \t{digi_out:010b}")

    out_settings = []

    for dig_out in [modbus.GPIO.IO1, modbus.GPIO.IO2, modbus.GPIO.IO3, modbus.GPIO.IO4,]:
        setting = await modbus.get_digi_output_config(client, dig_out)
        click.echo(f"Out Conf {dig_out} = \t{setting}")
        out_settings.append(setting)

    digi_in = await modbus.get_digi_input(client, modbus.GPIO.ALL)
    click.echo(f"In = \t{digi_in:010b}")

    analogs = []
    for a in modbus.AnalogIn:
        analog = await modbus.get_analog_input(client, a)
        click.echo(f"Analog {a} = \t{analog}")
        analogs.append(analog)

    pcs = []
    for pc in modbus.PulseCounter:
        count = await modbus.get_pulse_count(client, pc)
        click.echo(f"PC {pc} = \t{count}")
        pcs.append(count)
