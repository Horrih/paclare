"""Provides the entry point for pacsource."""

import sys

from paclare.commands import init_config, list_packages, sync_packages
from paclare.options import OptionsInit, OptionsList, OptionsSync, parse_args


def main() -> None:
    """Parse arguments and process the relevant command."""
    options = parse_args(sys.argv[1:])
    if isinstance(options, OptionsSync):
        sync_packages(options)
    elif isinstance(options, OptionsList):
        list_packages(options)
    elif isinstance(options, OptionsInit):
        init_config(options)


if __name__ == "__main__":
    main()
