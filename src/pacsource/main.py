"""Provides the entry point for pacsource."""

import argparse
import dataclasses
import importlib.metadata
import logging
import pathlib

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def main():
    config = parse_args()


@dataclasses.dataclass
class Config:
    command: str  #: Which action to perform : TODO enum/subparser
    config_dir: pathlib.Path  #: Where to find the config files
    dry_run: bool  #: Do not perform any install/uninstall


def version() -> str:
    return importlib.metadata.version("pacsource")


def parse_args() -> Config:
    description = f"""
pacsource v{version()} applies to your system the packages listed in your config files.

It helps keeping your system minimal, and you can share your config and back it up.

It supports various packaging formats out of the box, but you can add additional ones
by specifying the commands to run.
"""
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("command", help="Command to run (i.e sync, list, ...)")
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
    args = parser.parse_args()
    if args.quiet:
        logging.basicConfig(level=logging.WARNING)
    elif args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    return Config(command=args.command, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
