import json
import logging
import os
import traceback
from dataclasses import dataclass
from datetime import datetime

import click
import paramiko
from colorama import Fore, Style
from dotenv import load_dotenv
from rich import print_json
from rich.console import Console

from pymultissher.constants import OUTPUT_DIR, SUPPORTED_SSH_KEY_TYPES, VERBOSE
from pymultissher.exceptions import MultiSSHerException
from pymultissher.logger import get_logger


@dataclass
class SSHCredentials:
    domain: str
    port: int = 22
    username: str = "root"
    ssh_key_path: str = ""
    ssh_key_password: str = ""
    ssh_key_type: str = "rsa"


class MultiSSHer:

    def __init__(self, logger=None):
        if logger is None:
            logger = get_logger()

        self.logger = logger
        self.logger.debug('class "MultiSSHer" was created')
        self.init_directory()
        self.data = {}

        self.console = Console()

    def init_directory(self):
        pass
        # if not os.path.exists(OUTPUT_DIR):
        #     os.mkdir(OUTPUT_DIR)

    def verbose_print(self, msg: str) -> None:
        if VERBOSE:
            self.console.print(msg, style="yellow")

    def banner(self):
        """Prints banner"""
        self.console.print("Print verbose information:", style="white")
        self.console.print(VERBOSE, style="red")

    def get_default_ssh_values(self):
        self.default_ssh_username = os.getenv("SSH_USERNAME_DEFAULT", "root")
        self.default_ssh_key_file_path = os.getenv("SSH_KEY_PATH_DEFAULT", "~/.ssh/id_rsa")
        self.default_ssh_key_password = os.getenv("SSH_KEY_PASSWORD_DEFAULT", None)
        self.get_default_ssh_key_type()

    def get_default_ssh_key_type(self):
        self.default_ssh_key_type = os.getenv("SSH_KEY_TYPE_DEFAULT", "rsa")
        self.default_ssh_key_type = self.default_ssh_key_type.lower()

        if self.default_ssh_key_type not in SUPPORTED_SSH_KEY_TYPES:
            raise MultiSSHerException(f"Only following keys supported: {SUPPORTED_SSH_KEY_TYPES}")

    def create_client(self, ssh_host: SSHCredentials) -> None:
        """Creates a client to connect to server over SSH using a custom private key

        Args:
            ssh_host(SSHCredentials): data class that contains all necessary parameters for SSH connection
        """

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load private key with password
        try:
            if ssh_host.ssh_key_type == "rsa":
                key = paramiko.RSAKey.from_private_key_file(ssh_host.ssh_key_path, password=ssh_host.ssh_key_password)

            if ssh_host.ssh_key_type == "ed25519":
                key = paramiko.Ed25519Key.from_private_key_file(
                    ssh_host.ssh_key_path, password=ssh_host.ssh_key_password
                )

        except (paramiko.SSHException, FileNotFoundError) as e:
            print(f"Error loading private key: {e}")
            self.logger.error(traceback.format_exc())
            return None

        try:
            self.client.connect(
                hostname=ssh_host.domain,
                port=ssh_host.port,
                username=ssh_host.username,
                pkey=key,
                disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
            )
        except paramiko.AuthenticationException:
            print(f"Authentication failed for server: {ssh_host.domain}")
            logging.error(traceback.format_exc())
            self.close_client()
        except paramiko.SSHException as e:
            print(f"SSH connection error: {e}")
            logging.error(traceback.format_exc())
            self.close_client()

    def close_client(self) -> None:
        """Closes a SSH client"""

        if self.client is not None:
            self.client.close()

    def run_command_over_ssh(self, hostname: str, cmd: str, category_name: str, field_name: str = "value"):
        """Runs command on the server.

        Args:
            username (str): The username for SSH login.
        """

        self.logger.debug(f"Run CMD on the server: {cmd}")
        output = self.execute_cmd_and_read_response(cmd)
        if output:
            self.verbose_print(f"Server: '{hostname}'")
            self.verbose_print(f"Output:\n{output}")
            self.data[hostname][category_name] = {field_name: output}
        else:
            self.logger.error(f"Error getting output: '{hostname}'")

    def execute_cmd_and_read_response(self, cmd: str) -> str:
        """Based on https://stackoverflow.com/questions/31834743/get-output-from-a-paramiko-ssh-exec-command-continuously

        Args:
            cmd (str): command to be run

        Returns:
            str: Output of the command
        """

        output = ""
        # is_active can be a false positive, so further test
        transport = self.client.get_transport()
        if transport.is_active():
            try:
                transport.send_ignore()
            except Exception as _e:
                logging.error(traceback.format_exc())
        else:
            logging.error(f"Something wrong with transport")
            return None

        channel = transport.open_session()
        channel.set_combine_stderr(1)  # not handling stdout & stderr separately
        channel.exec_command(cmd)
        channel.shutdown_write()  # command was sent, no longer need stdin

        def __response_read(channel):
            # Small outputs (i.e. 'whoami') can end up running too quickly
            # so we yield channel.recv in both scenarios
            while True:
                if channel.recv_ready():
                    yield channel.recv(4096).decode("utf-8")

                if channel.exit_status_ready():
                    yield channel.recv(4096).decode("utf-8")
                    break

        # read response
        for response in __response_read(channel):
            output += response

        return output.strip()

    def parse_hostname_item(self, item: dict) -> SSHCredentials:
        """Converts an JSON item in to data class with all necessary parameters for SSH connection.

        Args:
            item (dict): JSON item with server parameters

        Returns:
            SSHCredentials: Data class that contains all necessary parameters for SSH connection
        """

        ssh_obj = SSHCredentials
        self.get_default_ssh_values()

        if "domain" in item:
            ssh_obj.domain = item["domain"]
            self.verbose_print(f"{datetime.now()} domain: {ssh_obj.domain}")
            logging.debug(f"domain: {ssh_obj.domain}")

        if "port" in item:
            ssh_obj.port = int(item["port"])
            logging.debug(f"port: {ssh_obj.port}")

        ssh_obj.username = self.default_ssh_username
        if "user" in item:
            ssh_obj.username = item["user"]
            self.verbose_print(f"{datetime.now()} user: {ssh_obj.username}")

        ssh_obj.ssh_key_path = self.default_ssh_key_file_path
        if "ssh_key_path" in item:
            ssh_obj.ssh_key_path = item["ssh_key_path"]
            self.verbose_print(f"{datetime.now()} ssh_key_path: {ssh_obj.ssh_key_path}")

        ssh_obj.ssh_key_password = self.default_ssh_key_password
        if "ssh_key_password" in item:
            ssh_obj.ssh_key_password = item["ssh_key_password"]
            self.verbose_print(f"{datetime.now()} ssh_key_password: **HIDDEN**")

        ssh_obj.ssh_key_type = self.default_ssh_key_type
        if "ssh_key_type" in item:
            ssh_obj.ssh_key_type = item["ssh_key_type"]
            self.verbose_print(f"{datetime.now()} ssh_key_type: {ssh_obj.ssh_key_type}")

        return ssh_obj

    def load_domains(self, filename: str):
        """Loads domains from JSON

        Args:
            filename (str): Name of the file
        """
        self.domains = {}
        self.logger.debug(f"file with domain names: {filename}")
        with open(filename) as json_file:
            self.domains = json.load(json_file)

    def apply_filter_on_domains(self, filter: str):
        """Apply filter on domains

        Args:
            domains (dict): List of items with domains
            filter (str): Filter to be applied
        """

        if filter is None:
            return self.domains

        filter = filter.lower()
        self.logger.info(f"Filter domains based on: {filter}")
        filtered_domains = []
        for item in self.domains:
            try:
                ssh_host = self.parse_hostname_item(item)
                if filter in ssh_host.domain.lower():
                    filtered_domains.append(item)
            except Exception:
                self.logger.error(traceback.format_exc())

        return filtered_domains

    def to_console(self):
        """Prints gathered data"""
        print_json(json.dumps(self.data, indent=4))
