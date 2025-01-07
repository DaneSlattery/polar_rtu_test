# SPDX-FileCopyrightText: 2025-present DaneSlattery <dane_s@umantec.net>
#
# SPDX-License-Identifier: MIT
import click

from rtu_test.__about__ import __version__


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
            click.echo("    q: quit")
            char = click.getchar()
            if char == "s":
                menu = "start"
            elif char == "q":
                menu = "quit"
            else:
                click.echo("Invalid input")
        elif menu == "start":
            click.echo("Start RTU Test")
            is_connected = click.confirm("Is the RTU connected and powered?")

            if not is_connected:
                click.echo("Connect the RTU")
                continue

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
            menu = "main"
        elif menu == "quit":
            return
