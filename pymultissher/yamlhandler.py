import json
import os

import yaml

from pymultissher.constants import YAML_FILE_COMMANDS, YAML_FILE_DOMAINS
from pymultissher.exceptions import (
    YAMLConfigExists,
    YAMLGenericException,
    YAMLValidationError,
)
from pymultissher.logger import get_logger


class YAMLHandler:

    def __init__(self, filename: str, logger=None):
        """_summary_

        Args:
            filename (str, optional): The filename with YAML configuration to be used
            logger (logging, optional): The logger instable to ber used. Defaults to get_logger.
        """

        if logger is None:
            logger = get_logger()
        self.logger = logger
        self.filename = filename
        self.data = {}

    def load_data(self):
        """
        Loads the YAML data from the specified file path.

        Raises:
            YAMLError: If there's an error loading the YAML file.
        """
        try:
            with open(self.filename, "r") as f:
                self.data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise YAMLGenericException(f"Error loading YAML file: {e}")

    def verify_domains(self):
        """
        Verifies the structure and basic data types of the YAML data.

        Raises:
            ValidationError: If there are any validation errors.
        """
        errors = []

        # Verify 'defaults' section
        if "defaults" not in self.data:
            errors.append("'defaults' section is missing")
        elif self.data["defaults"] is None:
            errors.append("'defaults' section is empty")
        else:
            self.verify_section(self.data["defaults"], expected_keys=["user"])

        # Verify 'domains' section
        if "domains" not in self.data:
            errors.append("'domains' section is missing")

        if not isinstance(self.data["domains"], list):
            errors.append("'domains' section should be a list")
        elif self.data["domains"] is None:
            errors.append("'domains' section is empty")
        else:
            for i, domain_item in enumerate(self.data["domains"]):
                self.verify_section(domain_item, expected_keys=["domain"])
                domain_values = domain_item["domain"]
                self.verify_section(domain_values, expected_keys=["name"])

                # options should be strings
                for key in ["ssh_key_path", "ssh_key_type", "user"]:
                    if key in domain_values and not isinstance(domain_values[key], str):
                        errors.append(f"Domain {i+1}: '{key}' should be a string")

                # options should to int
                for key in ["port"]:
                    if key in domain_values:
                        domain_values[key] = int(domain_values[key])

        if errors:
            raise YAMLValidationError("\n" + "\n".join(errors))

    def verify_section(self, section_data, expected_keys):
        """
        Verifies if a section has the expected keys and their values are not None.

        Args:
            section_data: The data of the section to verify.
            expected_keys: A list of expected keys in the section.

        Raises:
            ValidationError: If there are any missing keys or None values.
        """
        missing_keys = [key for key in expected_keys if key not in section_data]
        if missing_keys:
            raise YAMLValidationError(f"Missing keys: {', '.join(missing_keys)}")

        for key, value in section_data.items():
            if value is None:
                raise YAMLValidationError(f"Value for '{key}' cannot be None")

    def to_console(self):
        """Prints YML config data"""
        print_json(json.dumps(self.data, indent=4))


class YAMLEmptyConfigHandler:

    def generate_empty_configs_domains(self, filename: str = YAML_FILE_DOMAINS):
        """Generates an empty YAML configuration file with defaults and domains.


        Args:
            filename (str, optional): The filename with YAML configuration to be created. Defaults to YAML_FILE_DOMAINS.

        Raises:
            YAMLConfigExists: raised, if config file already exists
        """

        if os.path.exists(filename):
            raise YAMLConfigExists(f"Found existing config for domains: {filename}")

        domains_config = {
            "defaults": {
                "port": "22",
                "user": "root",
                "ssh_key_path": "~/.ssh/id_rsa",
                "ssh_key_password": None,
                "ssh_key_type": "rsa",
            },
            "domains": [
                {
                    "domain": {
                        "name": "localhost",
                        "port": 22,
                        "user": "root",
                        "ssh_key_path": "~/.ssh/id_rsa",
                        "ssh_key_type": "rsa",
                    }
                }
            ],
        }

        with open(filename, "w") as outfile:
            yaml.dump(domains_config, outfile, default_flow_style=False)

    def generate_empty_configs_commands(self, filename: str = YAML_FILE_COMMANDS):
        """Generates an empty YAML configuration file with commands."""

        if os.path.exists(filename):
            raise YAMLConfigExists(f"Found existing config for commands: {filename}")

        config = {
            "commands": [
                {"item": {"command": "whoami", "tag": "all", "report": {"category": "whoami", "field": "value"}}},
                {"item": {"command": "hostname", "tag": "all", "report": {"category": "hostname", "field": "value"}}},
                {"item": {"command": "ssh -V", "tag": "all", "report": {"category": "ssh", "field": "version"}}},
                {
                    "item": {
                        "command": "systemctl status fail2ban | grep running",
                        "tag": "all",
                        "report": {"category": "fail2ban", "field": "status"},
                    }
                },
            ],
        }

        with open(filename, "w") as outfile:
            yaml.dump(config, outfile, default_flow_style=False)
