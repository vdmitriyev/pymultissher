import os
import traceback
from sys import platform
from typing import Optional

import typer
from typing_extensions import Annotated

from pymultissher.exceptions import MultiSSHerCreateClient
from pymultissher.helpers import handle_dict_keys
from pymultissher.logger import get_logger
from pymultissher.pymultissher import MultiSSHer

app = typer.Typer()


def info_param_callback(value: str):
    if value != "info":
        raise typer.BadParameter("Only allowed: info")
    return value


@app.command()
def ssh_info(
    info: Annotated[
        str, typer.Argument(help="Gathers different information from servers over SSH", callback=info_param_callback)
    ] = None,
    filename: str = typer.Option(
        prompt=False, help="Path to the JSON file containing domain names", default="domains.json"
    ),
    filter_domain: str = typer.Option(None, prompt=False, help="Filters domains to be used"),
):

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


if __name__ == "__main__":
    app()
