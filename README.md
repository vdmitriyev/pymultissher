## About

pymultissher is a simple CLI tool that runs commands on multiple servers over SSH.

## Why "yet another" SSH tool?

There is already endless number of tools and utilities, which are able to run commands on a cluster of servers over SSH (e.g., [ansible](https://github.com/ansible/ansible), [fabric](https://github.com/fabric/fabric), [paramiko](https://github.com/paramiko/paramiko), `you-name-it`). However, from time to time you just need a simple and straightforward CLI tool, which take a list of domains and runs a list of command on them over SSH and aggregates output. This is exactly what [pymultissher](https://github.com/vdmitriyev/pymultissher) is trying to accomplish.

P.S. SSH heavy-lifting is done by [Paramiko](https://www.paramiko.org/)

## How it works?

The utility relies on two YAML configuration files to control its operations:

* `domains.yml`: This file defines default SSH values and domain names. Each domain can have its own set of SSH parameters.
* `commands.yml`: This file specifies the commands to be executed over SSH connections.

You can generate these initial configuration files using the `init` argument.
The utility also allows using custom YAML configuration files to store domain information and commands.

## Getting Started

* Install (TestPyPI)
    ```
    pip install --index-url https://test.pypi.org/simple/ --upgrade pymultissher
    ```
* Generate initial configuration files
    ```
    pymultissher init
    ```
* Edit YAML configuration files according to needs
* List available CLI parameters
    ```
    pymultissher --help
    ```
* Utility could also be started as a Python module:
    ```
    python -m pymultissher --help
    ```

## Usage: CLI

Output of the CLI command:
```
pymultissher --help
```

![](https://raw.githubusercontent.com/vdmitriyev/pymultissher/main/docs/images/cli-image.png)

N.B. CLI could be also run as a Python module: ```python -m pymultissher --help```

## Documentation

[Documentation](https://vdmitriyev.github.io/pymultissher/)

## Contributing

Please, check [CONTRIBUTING.rst](https://github.com/vdmitriyev/pymultissher/blob/main/CONTRIBUTING.rst)

## License

[MIT](https://github.com/vdmitriyev/pymultissher/blob/main/LICENSE)
