import os
import traceback
from sys import platform
from typing import Optional

import typer
from rich import print, print_json
from rich.console import Console
from typing_extensions import Annotated

from pymultissher import __description__
from pymultissher.constants import YAML_FILE_COMMANDS, YAML_FILE_DOMAINS
from pymultissher.exceptions import (
    MultiSSHerCreateClient,
    YAMLConfigExists,
    YAMLValidationError,
)
from pymultissher.helpers import handle_dict_keys
from pymultissher.logger import get_logger
from pymultissher.pymultissher import MultiSSHer, YAMLEmptyConfigHandler, YAMLHandler

app = typer.Typer(help=__description__)


# def info_param_callback(value: str):
#     if value != "info":
#         raise typer.BadParameter("Only allowed: info")
#     return value


@app.command()
def get_info(
    filename: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Path to the YAML file containing domain names"),
    ] = "domains.json",
    filter_domain: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Filters domains to be used"),
    ] = None,
):
    """
    Gathers different information from servers over SSH
    """

    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    logger = get_logger()
    ssher = MultiSSHer(logger=logger)
    ssher.load_domains(filename)

    filtered_domains = ssher.apply_filter_on_domains(filter=filter_domain)

    for item in filtered_domains:
        try:
            ssh_host = ssher.parse_hostname_item(item)
            handle_dict_keys(ssher.data, key=ssh_host.domain)
            ssher.create_client(ssh_host)
            if ssher.client is None:
                raise MultiSSHerCreateClient()

            if ssher.client is not None:
                # SSH version
                ssher.run_command_over_ssh(
                    hostname=ssh_host.domain, cmd="ssh -V", category_name="ssh", field_name="version"
                )
                # fail2ban status
                ssher.run_command_over_ssh(
                    hostname=ssh_host.domain,
                    cmd="systemctl status fail2ban | grep running",
                    category_name="fail2ban",
                    field_name="status",
                )
                # asgard2 status
                ssher.run_command_over_ssh(
                    hostname=ssh_host.domain,
                    cmd="systemctl status asgard2-agent.service | grep running",
                    category_name="asgard2",
                    field_name="status",
                )
                ssher.close_client()

        except Exception:
            logger.error(traceback.format_exc())

    ssher.to_console()


@app.command()
def run_command(
    filename: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Path to the YAML file containing domain names"),
    ] = "domains.json",
    command: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Command to be run on the server"),
    ] = "whoami",
    filter_domain: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Filters domains to be used"),
    ] = None,
):
    """Runs a given command on servers over SSH (default: whoami)"""

    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    logger = get_logger()
    ssher = MultiSSHer(logger=logger)
    ssher.load_domains(filename)

    filtered_domains = ssher.apply_filter_on_domains(filter=filter_domain)

    for item in filtered_domains:
        try:
            ssh_host = ssher.parse_hostname_item(item)
            handle_dict_keys(ssher.data, key=ssh_host.domain)
            ssher.create_client(ssh_host)
            if ssher.client is None:
                raise MultiSSHerCreateClient()

            if ssher.client is not None:
                # run command
                ssher.run_command_over_ssh(
                    hostname=ssh_host.domain,
                    cmd=command,
                    category_name="command",
                    field_name=command.lower().replace(" ", "_"),
                )

        except Exception:
            logger.error(traceback.format_exc())

    ssher.to_console()


@app.command()
def verify(
    filename: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Path to the YAML file containing domain names"),
    ] = YAML_FILE_DOMAINS,
    target: Annotated[
        Optional[str],
        typer.Option(prompt=False, help="Specifies what to verify: domains or commands"),
    ] = "domains",
    verbose: Annotated[
        Optional[bool],
        typer.Option(prompt=False, help="Verbose options for exceptions"),
    ] = False,
):
    """Verify yml file"""

    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

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
            if verbose:
                console.print_exception(show_locals=True)
    if verbose:
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
    """Generates an empty YAML configuration files with defaults, domains and commands"""

    logger = get_logger()
    console = Console()
    yml_handler = YAMLEmptyConfigHandler()

    try:
        yml_handler.generate_empty_configs_domains(filename=file_domains)
        console.print(f"Generated config file for domains: ", end=None)
        console.print(f"{file_domains}", style="green")
    except YAMLConfigExists as ex:
        console.print(f"Config file already exists: ", style="red", end=None)
        console.print(f"{file_domains}", style="yellow")
        if not verbose:
            console.print(f"Exception: ", end=None)
            console.print(f"{ex}", style="red")
        else:
            console.print_exception(show_locals=True)

    try:
        yml_handler.generate_empty_configs_commands(filename=file_commands)
        console.print(f"Generated config file for commands: ", end=None)
        console.print(f"{file_commands}", style="green")
    except YAMLConfigExists as ex:
        console.print(f"Config file already exists: ", style="red", end=None)
        console.print(f"{file_commands}", style="yellow")

        if not verbose:
            console.print(f"Exception: ", end=None)
            console.print(f"{ex}", style="red")
        else:
            console.print_exception(show_locals=True)


if __name__ == "__main__":
    app()
