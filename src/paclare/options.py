"""Provides configuration and CLI options to the main script."""

import argparse
import dataclasses
import enum
import importlib.metadata
import logging
import os
import pathlib
import typing

import paclare.logs
from paclare.config import read_config_file
from paclare.packagemanagers import PACKAGE_MANAGERS_DEFAULTS, PackageManager


@dataclasses.dataclass
class OptionsInit:
    """Configuration parameters passed to the CLi for the "list" command."""

    #: Where to export the config file
    output_file: pathlib.Path

    #: The package managers that will be checked on the system
    pkg_mgrs: list[PackageManager]


@dataclasses.dataclass
class OptionsList:
    """Configuration parameters passed to the CLi for the "list" command."""

    #: List the packages for the following package managers
    pkg_mgrs: list[PackageManager]


@dataclasses.dataclass
class OptionsSync:
    """Configuration parameters passed to the CLi for the "sync" command."""

    #: Sync the packages for the following package managers
    pkg_mgrs: list[tuple[PackageManager, list[str]]]

    #: Do not perform any install/uninstall
    dry_run: bool


class _Command(enum.StrEnum):
    """Main command to run in this script call."""

    SYNC = "sync"  #: Sync installed packages with toml config
    LIST = "list"  #: List installed packages
    INIT = "init"  #: Exports a toml config from the current packages


def parse_args(cli_args: list[str]) -> OptionsSync | OptionsList | OptionsInit:
    """Process the CLI arguments."""
    parser = _define_args()
    args = parser.parse_args(cli_args)
    if args.quiet:
        paclare.logs.logger.setLevel(logging.WARNING)
    elif args.verbose:
        paclare.logs.logger.setLevel(logging.DEBUG)

    if args.command == _Command.SYNC:
        pkg_mgrs_packages = [
            (pkg_mgr, pkgs)
            for pkg_mgr, pkgs in read_config_file(pathlib.Path(args.config))
            if (not args.pkg_mgr or pkg_mgr.name == args.pkg_mgr)
        ]
        return OptionsSync(pkg_mgrs_packages, args.dry_run)

    if args.command == _Command.LIST:
        pkg_mgrs = [
            pkg_mgr
            for pkg_mgr, _ in read_config_file(pathlib.Path(args.config))
            if (not args.pkg_mgr or pkg_mgr.name == args.pkg_mgr)
        ]
        return OptionsList(pkg_mgrs)

    return OptionsInit(pathlib.Path(args.output), PACKAGE_MANAGERS_DEFAULTS)


def _version() -> str:
    """Return the version from pyproject.toml."""
    return importlib.metadata.version("paclare")


DESCRIPTION = f"""
paclare v{_version()} syncs your system packages from a config file

It helps keeping your system minimal, you can share your config betwen
devices and back it up.

It supports various packaging formats out of the box, but you can add
additional ones by specifying the commands to run.

See the github for more info : https://github.com/Horrih/paclare
"""

SYNC_HELP = "Install/uninstall packages according to your toml config"
SYNC_DESCRIPTION = f"""{DESCRIPTION}

------------------------------------------------------------------------

sync command : {SYNC_HELP}
"""

LIST_HELP = "List installed packages for each configured package manager"
LIST_DESCRIPTION = f"""{DESCRIPTION}

------------------------------------------------------------------------

list command : {LIST_HELP}
"""

INIT_HELP = "Create a config file from your list of installed packages."
INIT_DESCRIPTION = f"""{DESCRIPTION}

------------------------------------------------------------------------

init command : {INIT_HELP}

WARNING : only supports paclare's built-in package managers.
"""


def _define_args() -> argparse.ArgumentParser:
    """Create the argparse ArgumentParser with this script's options setup."""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _base_args(parser)
    subparsers = parser.add_subparsers(dest="command", title="Available commands")
    _create_init_parser(subparsers)
    _create_sync_parser(subparsers)
    _create_list_parser(subparsers)
    return parser


def _create_sync_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add the 'sync' command arguments."""
    parser = subparsers.add_parser(
        _Command.SYNC,
        description=SYNC_DESCRIPTION,
        help=SYNC_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _config_file_arg(parser)
    parser.add_argument(
        "-n",
        "--dry-run",
        help="If enabled, run a simulation run, your system won't be modified",
        action="store_true",
    )
    _restrict_package_manager_arg(parser)
    _base_args(parser)


def _create_list_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add the 'list' command arguments."""
    parser = subparsers.add_parser(
        _Command.LIST,
        description=LIST_DESCRIPTION,
        help=LIST_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _config_file_arg(parser)
    _restrict_package_manager_arg(parser)
    _base_args(parser)


def _create_init_parser(subparsers: typing.Any) -> None:
    """Add the 'init' command arguments."""
    parser = subparsers.add_parser(
        _Command.INIT,
        description=INIT_DESCRIPTION,
        help=INIT_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("output", help="Path to output file")
    _restrict_package_manager_arg(parser)
    _base_args(parser)


def _base_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments that every command should implement."""
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
    parser.add_argument("--version", action="version", version=f"paclare {_version()}")


def _config_file_arg(parser: argparse.ArgumentParser) -> None:
    """Add an option to specify the toml configuration file location."""
    home = os.getenv("HOME")
    system_config_dir = os.getenv("XDG_CONFIG_HOME") or f"{home}/.config"
    default_config = f"{system_config_dir}/paclare/paclare.toml"
    parser.add_argument(
        "-c",
        "--config",
        help=f"paclare configuration file. Default : {default_config}",
        default=default_config,
    )


def _restrict_package_manager_arg(parser: argparse.ArgumentParser) -> None:
    """Add a filter for package manager for the current command."""
    parser.add_argument(
        "--pkg-mgr",
        help="Restrict the command to only the specified package manager.",
    )
