"""Implementation of the main logic of paclare : its commands."""

from paclare.bash import run_helper_command, run_user_command
from paclare.config import read_config_file
from paclare.logs import logger, print_section
from paclare.options import OptionsInit, OptionsList, OptionsSync


def init_config(options: OptionsInit) -> None:
    """Initialize a config file from the installed packages."""
    logger.error("Notimplemented" + options.output_file.as_posix())


def list_packages(options: OptionsList) -> None:
    """List the installed packages for all the configured package managers."""
    for package_manager in read_config_file(options.config_file):
        msg = "Here are your pacman explicitely installed packages:"
        print_section(f"{package_manager.name} | {msg}")
        packages = run_helper_command(package_manager.list_cmd)
        logger.info("\n".join(sorted(packages[:-1].split("\n"))))


def sync_packages(options: OptionsSync) -> None:
    """Sync the packages on the config file.

    If a package is in the toml config, it will be installed.
    If a package it not in the toml config it will be uninstalled.
    """
    for package_manager, packages in read_config_file(options.config_file).items():
        print_section(f"{package_manager.name} | Checking packages to install/remove")
        installed_str = run_helper_command(
            package_manager.list_cmd,
        )
        installed_packages = set(installed_str.split("\n")[:-1])
        to_install = set(packages) - installed_packages
        to_remove = installed_packages - set(packages)
        to_install_str = ", ".join(to_install) if to_install else "Nothing to do"
        to_remove_str = ", ".join(to_remove) if to_remove else "Nothing to do"
        logger.info(f"Packages to install : {to_install_str}")
        logger.info(f"Packages to remove  : {to_remove_str}")
        if to_install:
            logger.info("Starting installs...")
            run_user_command(
                f"{package_manager.install_cmd} {' '.join(to_install)}",
                dry_run=options.dry_run,
            )
        if to_remove:
            logger.info("Starting uninstalls...")
            uninstall_str = f"'{"' '".join(to_remove)}'"
            run_user_command(
                f"{package_manager.uninstall_cmd} {uninstall_str}",
                dry_run=options.dry_run,
            )
