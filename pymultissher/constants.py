import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))
LOG_FILE_NAME = "log-ssh-scanner.log"

# read global
VERBOSE = os.environ.get("VERBOSE") or "False"
VERBOSE = VERBOSE.upper() == "TRUE"

SUPPORTED_SSH_KEY_TYPES = ["rsa", "ed25519"]
YAML_FILE_DOMAINS = "domains.yml"
YAML_FILE_COMMANDS = "commands.yml"
