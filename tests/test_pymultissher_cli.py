import os
from typing import Any

import pytest
from typer.testing import CliRunner

from pymultissher.__main__ import app

runner = CliRunner()


@pytest.fixture
def generate_filenames():
    """Generates two unique file names."""
    base_name = "test_file_config_"
    file_extension = ".yml"
    filenames = []
    for i in range(2):
        filename = f"{base_name}{i}{file_extension}"
        filenames.append(filename)
    yield filenames  # Yield a list containing both filenames


@pytest.fixture(autouse=True)
def remove_files(request: pytest.FixtureRequest, generate_filenames: list):
    """Removes the generated files after the test."""
    yield

    # Get the generated filenames
    filenames = generate_filenames

    # Remove the files
    for filename in filenames:
        if os.path.exists(filename):
            os.remove(filename)


def test_cli_help_commands():
    "Checks is CLI commands presented in help output"

    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    expected_commands = ["init", "run-batch", "run-command", "verify"]
    for cmd in expected_commands:
        assert cmd in result.stdout
    # print(result.stdout)


def test_cli_init_custom(generate_filenames: list):
    "Checks if init generates custom files"

    file_domains, file_commands = generate_filenames
    cli_params = ["init", f"--file-domains", file_domains, "--file-commands", file_commands]
    result = runner.invoke(app, cli_params)
    assert result.exit_code == 0
    assert "Generated config file for domains: test_file_config_0.yml" in result.stdout
    assert "Generated config file for commands: test_file_config_1.yml" in result.stdout


verify_test_data = [
    ("domains", 0, -1),  # First set: param, expected_value, additional_value
    ("commands", 1, -1),
]


@pytest.mark.parametrize("param_target, expected_cli_exit, additional", verify_test_data)
def test_cli_verify_custom(param_target: str, expected_cli_exit: int, additional: int, generate_filenames: list):
    "Checks if verify works with custom files"

    file_domains, file_commands = generate_filenames
    test_cli_init_custom(generate_filenames)
    cli_params = ["verify", f"--filename", file_domains, "--target", param_target]
    print("\n".join(cli_params))
    result = runner.invoke(app, cli_params)
    assert result.exit_code == expected_cli_exit
