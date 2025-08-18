"""Provides the entry point for pacsource."""

import argparse
import dataclasses
import importlib.metadata
import logging
import os
import pathlib
import subprocess

log_format = "%(message)s"
logger = logging.getLogger(__file__)


def main():
    """Parse arguments and process the relevant command."""
    config = parse_args()
    if config.command == "list":
        list_packages(config)
    # TODO
    # enabled_package_managers
    # sync
    # list avec delta
    # lecture des packages dans fichier
    # Argparse de rang 2


@dataclasses.dataclass
class Config:
    """Configuration parameters passed to the CLI."""

    command: str  #: Which action to perform : TODO enum/subparser
    config_dir: pathlib.Path  #: Where to find the config files
    dry_run: bool  #: Do not perform any install/uninstall


def version() -> str:
    """Return the version from pyproject.toml."""
    return importlib.metadata.version("pacsource")


def define_args() -> argparse.ArgumentParser:
    """Create the argparse ArgumentParser with this script's options setup."""
    description = f"""
pacsource v{version()} syncs your system packages from config files.

It helps keeping your system minimal, you can share your config betwen
devices and back it up.

It supports various packaging formats out of the box, but you can add
additional ones by specifying the commands to run.

See the github for more info : https://github.com/Horrih/pacsource
"""
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("command", help="Command to run (i.e sync, list, ...)")

    home = os.getenv("HOME")
    system_config_dir = os.getenv("XDG_CONFIG_HOME") or f"{home}/.config"
    default_config = f"{system_config_dir}/pacsource"
    parser.add_argument(
        "-c",
        "--config",
        help=f"Pacsource configuration directory. Default : {default_config}",
        default=default_config,
    )
    parser.add_argument(
        "-v", "--verbose", help="Enable verbose logging", action="store_true"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Disable logging except for warnings/errors",
        action="store_true",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        help="If enabled, run a simulation run, your system won't be modified",
        action="store_true",
    )
    return parser


def parse_args() -> Config:
    """Process the CLI arguments."""
    parser = define_args()
    args = parser.parse_args()
    level = logging.INFO
    if args.quiet:
        level = logging.WARNING
    elif args.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level, format=log_format)

    config_path = pathlib.Path(args.config)
    if not config_path.exists():
        logging.error(f"Your config path {config_path.as_posix()} does not exist.")
    return Config(command=args.command, config_dir=config_path, dry_run=args.dry_run)


@dataclasses.dataclass
class PackageManager:
    """Represents the main commands to use with a package manager."""

    name: str
    list_cmd: str
    install_cmd: str
    uninstall_cmd: str


PACMAN = PackageManager(
    name="pacman",
    list_cmd='pacman -Qeq | grep -v "$(pacman -Qqm)"',
    install_cmd="",
    uninstall_cmd="",
)

PARU = PackageManager(
    name="paru",
    list_cmd="paru -Qeqm",
    install_cmd="",
    uninstall_cmd="",
)

FLATPAK = PackageManager(
    name="flatpak",
    list_cmd="flatpak list --app --columns=name | tail -n +1",
    install_cmd="flatpak install -y",
    uninstall_cmd="flatpak uninstall -y",
)


def read_config_managers(config: Config) -> list[PackageManager]:
    return [PACMAN, PARU, FLATPAK]


def list_packages(config: Config):
    """List the installed packages for all the configured package managers."""
    for package_manager in read_config_managers(config):
        msg = "Here are your pacman explicitely installed packages:"
        print_section(f"{package_manager.name} | {msg}")
        run_command(config, package_manager.list_cmd)


def run_command(config: Config, command: str):
    print_command(command)
    if not config.dry_run:
        subprocess.run(["/bin/bash", "-c", command])


RESET = "\033[0m"
CYAN = "\033[36m"
GREY = "\033[90m"


def print_section(text: str):
    """Print a text in highlighted color with an empty line before."""
    logging.info(f"\n{CYAN}{text}{RESET}")


def print_command(text: str):
    """Print a text in a descrete color to print the debug command."""
    logging.info(f"{GREY}{text}{RESET}")


if __name__ == "__main__":
    main()
