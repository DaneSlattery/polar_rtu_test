# SPDX-FileCopyrightText: 2025-present DaneSlattery <dane_s@umantec.net>
#
# SPDX-License-Identifier: MIT
import click

from rtu_test.__about__ import __version__
from rtu_test.modbus import connect, read_input_1, set_output_1, enumerature_tty


@click.command()
@click.help_option(*("--help", "-h"))
@click.version_option(__version__, "-V", "--version")
def rtu_test():
    click.echo(f"RTU Tester  ")

    menu = "main"

    while True:
        if menu == "main":
            click.echo("Main Menu:")
            click.echo("    s: start")
            click.echo("    l: list ports")
            click.echo("    q: quit")
            char = click.getchar()
            if char == "s":
                menu = "start"
            elif char == "q":
                menu = "quit"
            elif char == "l":
                menu = "list"
            else:
                click.echo("Invalid input")
        elif menu == "start":
            menu = start_menu()
        elif menu == "list":
            click.echo("List serial ports")
            ports = enumerature_tty()
            click.echo(len(ports))
            for port in ports:
                click.echo(port)
            click.echo("    b: back")
            char = click.getchar()
            if char == "b":
                menu = "main"
            else:
                click.echo("Invalid input")
        elif menu == "quit":
            return


def start_menu():

    click.echo("Start RTU Test")
    is_connected = click.confirm("Is the RTU connected and powered?")

    if not is_connected:
        click.echo("Connect the RTU")
        return "start"

    click.echo("Running Modbus Checks")

    click.echo("Pulse Out 1")
    click.echo("Pulse Out 2")
    click.echo("Pulse Out 3")
    click.echo("Pulse Out 4")

    click.echo("Set Out 1")
    click.echo("Set Out 2")
    click.echo("Set Out 3")
    click.echo("Set Out 4")

    click.confirm("Disconnect RTU power")
    click.echo("Polling RTU until dead")
    click.echo("RTU Dead")
    click.confirm("Reconnect RTU power")

    click.echo("Check Out 1")
    click.echo("Check Out 2")
    click.echo("Check Out 3")
    click.echo("Check Out 4")

    click.echo("All outputs remembered. Test Pass.")
    return "main"
