## About

pymultissher is a simple CLI tool that runs commands on multiple servers over SSH.

## Why "yet another" SSH tool?

There is already endless number of tools and utilities, which are able to run commands on a cluster of servers over SSH (e.g., ansible, fabric, paramiko, `you-name-it`). However, from time to time you just need a pure CLI tool, which take a collection domains and runs a given command on them using SSH and provide back a gathered output. This is exactly what [pymultissher]() is for. SSH heavy-lifting is done by [Paramiko](https://www.paramiko.org/)

## Getting Started

* Install (TestPyPI)
    ```
    pip install --index-url https://test.pypi.org/simple/ --upgrade pymultissher
    ```
* Generate initial configuration files
    ```
    python -m pymultissher --help
    ```

## Usage: CLI

Should be run as Python module (e.g. ```python -m pymultissher --help```)

## Documentation

[Documentation](https://vdmitriyev.github.com/pymultissher/)

## Contributing

Please, check [CONTRIBUTING.rst](CONTRIBUTING.rst)

## License

[MIT](LICENSE)
