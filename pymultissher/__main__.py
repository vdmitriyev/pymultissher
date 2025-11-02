import os
import traceback
from sys import platform
from typing import Optional

import typer
from rich import print, print_json
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from pymultissher import __description__
from pymultissher.constants import (
    VIEW_CONSOLE_FORMATS,
    YAML_FILE_COMMANDS,
    YAML_FILE_DOMAINS,
)
from pymultissher.exceptions import (
    MultiSSHerCreateClient,
    MultiSSHerNotSupported,
    YAMLConfigExists,
    YAMLValidationError,
)
from pymultissher.helpers import handle_dict_keys, is_verbose, set_verbose
from pymultissher.logger import get_logger
from pymultissher.pymultissher import MultiSSHer
from pymultissher.version import package_summary, package_version
from pymultissher.yamlhandler import YAMLEmptyConfigHandler, YAMLHandler

app = typer.Typer(help=__description__)
console = Console()


def __set_global_verbose(verbose: bool = False):
    set_verbose(verbose)


def __option_dry_run(dry_run):
    if dry_run:
        console.print(f"Option `--dry-run`: ", end=None)
        console.print(f"enabled", style="yellow")


def __print_domain_name(domain):
    console.print("Try to run commands on domain: ", end=None)
    console.print(domain, style="yellow")


@app.command()
def run_batch(
    file_domains: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="YAML file with domain names of servers"),
    ] = YAML_FILE_DOMAINS,
    file_commands: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="YAML file with command to be run on servers"),
    ] = YAML_FILE_COMMANDS,
    filter: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Filters domains to be used"),
    ] = None,
    view: Annotated[
        Optional[str],
        typer.Option(prompt=False, help=f"View format:{VIEW_CONSOLE_FORMATS}"),
    ] = "json",
    verbose: Annotated[
        Optional[bool],
        typer.Option(prompt=False, help="Verbose output"),
    ] = False,
    dry_run: Annotated[
        Optional[bool],
        typer.Option(prompt=False, help="Only shows prints. Commands will not be run"),
    ] = False,
):
    """
    Runs a batch of commands over SSH
    """

    if not os.path.exists(file_domains):
        raise FileNotFoundError(f"File not found: {file_domains}")

    if file_commands is not None and not os.path.exists(file_commands):
        raise FileNotFoundError(f"File not found: {file_commands}")

    view = view.lower()
    if view not in VIEW_CONSOLE_FORMATS:
        raise MultiSSHerNotSupported(f"Wrong view format for console. Allowed: {VIEW_CONSOLE_FORMATS}")

    __set_global_verbose(verbose)
    __option_dry_run(dry_run)

    logger = get_logger()
    ssher = MultiSSHer(logger=logger)

    ssher.load_defaults(file_domains)
    ssher.load_domains(file_domains)

    commands = []
    if file_commands is not None:
        yml_commands = YAMLHandler(logger=logger, filename=file_commands)
        yml_commands.load_data()
        commands = yml_commands.data
        print(f"Found command: {len(commands['commands'])}")

    filtered_domains = ssher.apply_filter_on_domains(filter=filter)

    for item in filtered_domains:
        try:

            ssh_host = ssher.parse_hostname_item(item["domain"])
            __print_domain_name(ssh_host.domain)
            handle_dict_keys(ssher.data, key=ssh_host.domain)
            ssher.create_client(ssh_host)

            if ssher.client is None:
                raise MultiSSHerCreateClient("SSH client is not ready")

            if ssher.client is not None:
                for cmd_item in commands["commands"]:
                    cmd = cmd_item["item"]
                    logger.debug(f"Run command: {cmd['command']}")
                    ssher.run_command_over_ssh(
                        hostname=ssh_host.domain,
                        cmd=cmd["command"],
                        category_name=cmd["report"]["category"],
                        field_name=cmd["report"]["field"],
                        dry_run=dry_run,
                    )

                ssher.close_client()

        except Exception:
            logger.error(traceback.format_exc())

    ssher.to_console(view)


@app.command()
def run_command(
    command: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Command to be run on the server"),
    ] = "whoami",
    file_domains: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Path to the YAML file containing domain names"),
    ] = YAML_FILE_DOMAINS,
    filter_domain: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Filters domains to be used"),
    ] = None,
    view: Annotated[
        Optional[str],
        typer.Option(prompt=False, help=f"View format:{VIEW_CONSOLE_FORMATS}"),
    ] = "json",
    verbose: Annotated[
        Optional[bool],
        typer.Option(prompt=False, help="Verbose output"),
    ] = False,
    dry_run: Annotated[
        Optional[bool],
        typer.Option(prompt=False, help="Only shows prints. Commands will not be run"),
    ] = False,
):
    """Runs a single command over SSH (default: whoami)"""

    if not os.path.exists(file_domains):
        raise FileNotFoundError(f"File not found: {file_domains}")

    view = view.lower()
    if view not in VIEW_CONSOLE_FORMATS:
        raise MultiSSHerNotSupported(f"Wrong view format for console. Allowed: {VIEW_CONSOLE_FORMATS}")

    __set_global_verbose(verbose)
    __option_dry_run(dry_run)

    logger = get_logger()
    ssher = MultiSSHer(logger=logger)

    ssher.load_defaults(file_domains)
    ssher.load_domains(file_domains)

    filtered_domains = ssher.apply_filter_on_domains(filter=filter_domain)

    for item in filtered_domains:
        try:
            ssh_host = ssher.parse_hostname_item(item["domain"])
            __print_domain_name(ssh_host.domain)
            handle_dict_keys(ssher.data, key=ssh_host.domain)
            ssher.create_client(ssh_host)

            if ssher.client is None:
                raise MultiSSHerCreateClient("SSH client is not ready")

            if ssher.client is not None:
                ssher.run_command_over_ssh(
                    hostname=ssh_host.domain,
                    cmd=command,
                    category_name="command",
                    field_name=command.lower().replace(" ", "_"),
                    dry_run=dry_run,
                )

        except Exception:
            logger.error(traceback.format_exc())

    ssher.to_console(view)


@app.command()
def verify(
    filename: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Path to the YAML file containing domain names"),
    ] = YAML_FILE_DOMAINS,
    target: Annotated[
        Optional[str], typer.Option(prompt=False, help="Specifies what to verify: domains or commands")
    ] = "domains",
    verbose: Annotated[
        Optional[bool],
        typer.Option(prompt=False, help="Verbose options for exceptions"),
    ] = False,
):
    """Verify a given YAML file"""

    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    __set_global_verbose(verbose)

    logger = get_logger()
    console = Console()
    yml_handler = YAMLHandler(logger=logger, filename=filename)
    yml_handler.load_data()

    console.print(f"Verify target: ", end=None)
    console.print(f"{target}", style="green")

    if target.lower() == "domains":
        try:
            yml_handler.verify_domains()
        except YAMLValidationError as ex:
            console.print(f"Invalid YAML file: ", end=None)
            console.print(f"{filename}", style="yellow")
            console.print(f"YAML errors: ", end=None)
            console.print(f"{ex}", style="red")
            if is_verbose():
                console.print_exception(show_locals=True)
    else:
        raise MultiSSHerNotSupported(f"Proved target is not supported: {target}")

    if is_verbose():
        yml_handler.to_console()


@app.command()
def init(
    file_domains: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Path to the YAML file containing domain names"),
    ] = YAML_FILE_DOMAINS,
    file_commands: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Path to the YAML file containing commands"),
    ] = YAML_FILE_COMMANDS,
    verbose: Annotated[
        Optional[bool],
        typer.Option(prompt=False, help="Verbose options for exceptions"),
    ] = False,
):
    """Generates initial YAML configuration files with SSH defaults, domains and commands"""

    _console = Console()
    yml_handler = YAMLEmptyConfigHandler()

    try:
        yml_handler.generate_empty_configs_domains(filename=file_domains)
        _console.print("Generated config file for domains: ", style="blue", end=None)
        _console.print(f"{file_domains}", style="green")
    except YAMLConfigExists as ex:
        _console.print("Config file already exists: ", style="red", end=None)
        _console.print(f"{file_domains}", style="blue")

        if verbose:
            _console.print_exception(show_locals=True)
        else:
            _console.print("Exception: ", style="red", end=None)
            _console.print(f"{ex}\n", style="white")

    try:
        yml_handler.generate_empty_configs_commands(filename=file_commands)
        _console.print("Generated config file for commands: ", style="blue", end=None)
        _console.print(f"{file_commands}", style="green")
    except YAMLConfigExists as ex:
        _console.print("Config file already exists: ", style="red", end=None)
        _console.print(f"{file_commands}", style="blue")

        if verbose:
            _console.print_exception(show_locals=True)
        else:
            _console.print("Exception: ", style="red", end=None)
            _console.print(f"{ex}\n", style="white")


@app.command()
def version(
    verbose: Annotated[
        Optional[bool],
        typer.Option(prompt=False, help="Verbose options for exceptions"),
    ] = False,
):
    """Shows package version"""

    if not verbose:
        console.print("Version: ", style="white", end=None)
        console.print(f"{package_version()}", style="yellow")
    else:
        table = Table()
        table.add_column("Field", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", justify="left", style="yellow", no_wrap=True)
        summary = package_summary()
        for item in summary:
            table.add_row(item["field"], item["value"])
        console.print(table)


if __name__ == "__main__":
    app()
