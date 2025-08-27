"""Provides the entry point for pacsource."""

import argparse
import dataclasses
import importlib.metadata
import logging
import os
import pathlib
import subprocess
import sys
import tomllib

# ruff: noqa: G004

log_format = "%(message)s"
logger = logging.getLogger(__name__)


def main() -> None:
    """Parse arguments and process the relevant command."""
    config = parse_args()
    if config.command == "list":
        list_packages(config)
    elif config.command == "sync":
        sync_packages(config)
    # Argparse de rang 2


@dataclasses.dataclass
class Config:
    """Configuration parameters passed to the CLI."""

    command: str  #: Which action to perform : TODO enum/subparser
    config_file: pathlib.Path  #: Where to find the config file
    dry_run: bool  #: Do not perform any install/uninstall


def version() -> str:
    """Return the version from pyproject.toml."""
    return importlib.metadata.version("paclare")


def define_args() -> argparse.ArgumentParser:
    """Create the argparse ArgumentParser with this script's options setup."""
    description = f"""
paclare v{version()} syncs your system packages from a config file

It helps keeping your system minimal, you can share your config betwen
devices and back it up.

It supports various packaging formats out of the box, but you can add
additional ones by specifying the commands to run.

See the github for more info : https://github.com/Horrih/paclare
"""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", help="Command to run (i.e sync, list, ...)")

    home = os.getenv("HOME")
    system_config_dir = os.getenv("XDG_CONFIG_HOME") or f"{home}/.config"
    default_config = f"{system_config_dir}/paclare/paclare.toml"
    parser.add_argument(
        "-c",
        "--config",
        help=f"paclare configuration file. Default : {default_config}",
        default=default_config,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose logging",
        action="store_true",
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
        logger.error(f"Your config path {config_path.as_posix()} does not exist.")
    return Config(command=args.command, config_file=config_path, dry_run=args.dry_run)


@dataclasses.dataclass
class PackageManager:
    """Represents the main commands to use with a package manager."""

    name: str  #: name
    list_cmd: str
    install_cmd: str
    uninstall_cmd: str
    packages: list[str] = dataclasses.field(default_factory=list)


PACMAN = PackageManager(
    name="pacman",
    list_cmd='pacman -Qeq | grep -v "$(pacman -Qqm)"',
    install_cmd="sudo pacman -S",
    uninstall_cmd="sudo pacman -Rns",
)

PARU = PackageManager(
    name="paru",
    list_cmd="paru -Qeqm",
    install_cmd="paru -S",
    uninstall_cmd="paru -Rns",
)

FLATPAK = PackageManager(
    name="flatpak",
    list_cmd="flatpak list --app --columns=name | tail -n +1",
    install_cmd="flatpak install -y",
    uninstall_cmd="flatpak uninstall -y",
)

PRESETS = {pkg_mgr.name: pkg_mgr for pkg_mgr in [PACMAN, PARU, FLATPAK]}


def read_config(config: Config) -> list[PackageManager]:
    """Read the config file."""
    print_section(f"Reading configuration from {config.config_file.as_posix()}")
    package_mgrs = tomllib.loads(config.config_file.read_text(encoding="utf-8"))
    res = [read_package_manager(name, fields) for name, fields in package_mgrs.items()]
    logger.info(f"Found {len(res)} configured package managers:")
    logger.info("\n".join(f"|-- {p.name} : {len(p.packages)} packages" for p in res))
    return res


def read_package_manager(name: str, fields: dict) -> PackageManager:
    """Read the package manager options and packages from the relevant toml section."""
    preset = PRESETS.get(name)
    default_list_cmd = preset.list_cmd if preset else None
    default_install_cmd = preset.install_cmd if preset else None
    default_uninstall_cmd = preset.uninstall_cmd if preset else None
    pkg_mgr = PackageManager(
        name,
        list_cmd=fields.get("list_cmd", default_list_cmd),
        install_cmd=fields.get("install_cmd", default_install_cmd),
        uninstall_cmd=fields.get("uninstall_cmd", default_uninstall_cmd),
        packages=sorted(fields.get("packages")),
    )
    if not pkg_mgr.list_cmd:
        fatal_error(f'Missing "list_cmd" setting for package manager {name}')
    if not pkg_mgr.install_cmd:
        fatal_error(f'Missing "install_cmd" setting for package manager {name}')
    if not pkg_mgr.uninstall_cmd:
        fatal_error(f'Missing "uninstall_cmd" setting for package manager {name}')
    return pkg_mgr


def list_packages(config: Config) -> None:
    """List the installed packages for all the configured package managers."""
    for package_manager in read_config(config):
        msg = "Here are your pacman explicitely installed packages:"
        print_section(f"{package_manager.name} | {msg}")
        packages = run_helper_command(package_manager.list_cmd)
        logger.info(packages)


def sync_packages(config: Config) -> None:
    """Sync the packages on the config file.

    If a package is in the toml config, it must be installed on the system
    If a package it not in the toml config it must be uninstalled from the system
    """
    for package_manager in read_config(config):
        print_section(f"{package_manager.name} | Checking packages to install/remove")
        installed_str = run_helper_command(
            package_manager.list_cmd,
        )
        installed_packages = set(installed_str.split("\n")[:-1])
        to_install = set(package_manager.packages) - installed_packages
        to_remove = installed_packages - set(package_manager.packages)
        to_install_str = ", ".join(to_install) if to_install else "Nothing to do"
        to_remove_str = ", ".join(to_remove) if to_remove else "Nothing to do"
        logger.info(f"Packages to install : {to_install_str}")
        logger.info(f"Packages to remove  : {to_remove_str}")
        if to_install:
            logger.info("Starting installs...")
            run_user_command(
                f"{package_manager.install_cmd} {' '.join(to_install)}",
                dry_run=config.dry_run,
            )
        if to_remove:
            logger.info("Starting uninstalls...")
            run_user_command(
                f"{package_manager.uninstall_cmd} {' '.join(to_remove)}",
                dry_run=config.dry_run,
            )


def run_user_command(command: str, *, dry_run: bool) -> None:
    """Run any bash command except if dry_run is enabled."""
    logger.info(f"Running command : {command}")
    if not dry_run:
        subprocess.run(["bash", "-c", command])


RESET = "\033[0m"
CYAN = "\033[36m"
GREY = "\033[90m"
RED = "\033[31m"


def run_helper_command(command: str) -> str:
    """Run any bash command except if dry_run is enabled."""
    logger.debug(f"{GREY}{command}{RESET}")
    output = subprocess.run(  # noqa: S603
        ["/bin/bash", "-c", command],
        check=True,
        capture_output=True,
    )
    return output.stdout.decode(encoding="utf-8")


def print_section(text: str) -> None:
    """Print a text in highlighted color with an empty line before."""
    logger.info(f"\n{CYAN}{text}{RESET}")


def fatal_error(text: str) -> None:
    """Print an error message and exit."""
    logger.error(f"{RED}Fatal error{RESET} : {text}.\nFix your configuration file.")
    sys.exit(0)


if __name__ == "__main__":
    main()
