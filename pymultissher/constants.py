import os

from dotenv import load_dotenv

load_dotenv()

BASEDIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASEDIR, "output")
LOG_FILE_NAME = "log-ssh-scanner.log"
SUPPORTED_SSH_KEY_TYPES = ["rsa", "ed25519"]

# read global
VERBOSE = os.environ.get("VERBOSE") or "False"
VERBOSE = VERBOSE.upper() == "TRUE"

YAML_FILE_DOMAINS = "domains.yml"
YAML_FILE_COMMANDS = "commands.yml"
