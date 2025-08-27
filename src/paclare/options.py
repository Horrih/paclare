"""Provides configuration and CLI options to the main script."""

import argparse
import dataclasses
import enum
import importlib.metadata
import logging
import os
import pathlib
import sys

from paclare.logs import init_logs, logger


@dataclasses.dataclass
class OptionsSync:
    """Configuration parameters passed to the CLi for the "sync" command."""

    config_file: pathlib.Path  #: Where to find the config file
    dry_run: bool  #: Do not perform any install/uninstall


@dataclasses.dataclass
class OptionsList:
    """Configuration parameters passed to the CLi for the "list" command."""

    config_file: pathlib.Path  #: Where to find the config file


@dataclasses.dataclass
class OptionsInit:
    """Configuration parameters passed to the CLi for the "list" command."""

    output_file: pathlib.Path  #: Where to export the config file


class _Command(enum.StrEnum):
    """Main command to run in this script call."""

    SYNC = "sync"  #: Sync installed packages with toml config
    LIST = "list"  #: List installed packages
    INIT = "init"  #: Exports a toml config from the current packages


def parse_args() -> OptionsSync | OptionsList | OptionsInit:
    """Process the CLI arguments."""
    parser = _define_args()
    args = parser.parse_args()
    if args.quiet:
        init_logs(logging.WARNING)
    elif args.verbose:
        init_logs(logging.DEBUG)
    else:
        init_logs(logging.INFO)

    if args.command == _Command.SYNC:
        return OptionsSync(_check_config_path(args.config), args.dry_run)
    if args.command == _Command.LIST:
        return OptionsList(_check_config_path(args.config))
    return OptionsInit(args.output)


def _check_config_path(path: str) -> pathlib.Path:
    """Check that the configuration file path exists, exits otherwise."""
    config_path = pathlib.Path(path)
    if not config_path.exists():
        logger.error(f"Config path {config_path.as_posix()} does not exist.")
        sys.exit(1)
    return config_path


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


def _create_sync_parser(subparsers: argparse.ArgumentParser) -> None:
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


def _create_list_parser(subparsers: argparse.ArgumentParser) -> None:
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


def _create_init_parser(subparsers: argparse.ArgumentParser) -> None:
    """Add the 'init' command arguments."""
    parser = subparsers.add_parser(
        _Command.INIT,
        description=INIT_DESCRIPTION,
        help=INIT_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    init_help = """Output toml file containing an initialized config.
Warning : only paclare's preconfigured package managers will be detected."""
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
