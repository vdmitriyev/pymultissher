"""Provides module specific constants."""

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))
LOG_FILE_NAME = "log-ssh-scanner.log"
SUPPORTED_SSH_KEY_TYPES = ["rsa", "ed25519"]
YAML_FILE_DOMAINS = "domains.yml"
YAML_FILE_COMMANDS = "commands.yml"

VIEW_CONSOLE_FORMATS = ["json", "table"]
