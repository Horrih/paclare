"""Implementation of the main logic of paclare : its commands."""

import shutil

from paclare.logs import logger, print_section
from paclare.options import OptionsInit, OptionsList, OptionsSync
from paclare.packagemanagers import PackageManager
from paclare.shell import run_helper_command, run_user_command


def init_config(options: OptionsInit) -> None:
    """Initialize a config file from the installed packages."""
    print_section("Auto detecting installed package managers...")
    logger.info("Only the paclare's preconfigured package managers will be checked")
    mgr_to_pkgs = []
    for pkg_mgr in options.pkg_mgrs:
        print("YEAH")
        is_present = shutil.which(pkg_mgr.name)
        if is_present:
            print("PRESENT")
            logger.info(
                "Package manager %s is installed : checking installed packages",
                pkg_mgr.name,
            )
            packages = sorted(run_helper_command(pkg_mgr.list_cmd)[:-1].split("\n"))
            logger.info(" |-- Found %s packages", len(packages))
            mgr_to_pkgs.append((pkg_mgr, packages))
        else:
            logger.info("Package manager %s is not installed : skipping", pkg_mgr.name)

    def config_section(pkg_mgr: PackageManager, packages: list[str]) -> str:
        return f"""[{pkg_mgr.name}]
packages = [
    {",\n    ".join('"' + pkg + '"' for pkg in packages)}
]
"""

    with options.output_file.open("w") as f:
        sections = [config_section(mgr, pkgs) for mgr, pkgs in mgr_to_pkgs]
        f.write("\n".join(sections))

    logger.info(
        "Your config has been initialized : see %s",
        options.output_file.as_posix(),
    )


def list_packages(options: OptionsList) -> None:
    """List the installed packages for all the configured package managers."""
    for package_manager in options.pkg_mgrs:
        msg = "Here are your pacman explicitely installed packages:"
        print_section(f"{package_manager.name} | {msg}")
        packages = run_helper_command(package_manager.list_cmd)
        logger.info("\n".join(sorted(packages[:-1].split("\n"))))


def sync_packages(options: OptionsSync) -> None:
    """Sync the packages on the config file.

    If a package is in the toml config, it will be installed.
    If a package it not in the toml config it will be uninstalled.
    """
    for package_manager, packages in options.pkg_mgrs:
        print_section(f"{package_manager.name} | Checking packages to install/remove")
        installed_str = run_helper_command(
            package_manager.list_cmd,
        )
        installed_packages = set(installed_str.split("\n")[:-1])
        to_install = set(packages) - installed_packages
        to_remove = installed_packages - set(packages)
        to_install_str = ", ".join(to_install) if to_install else "Nothing to do"
        to_remove_str = ", ".join(to_remove) if to_remove else "Nothing to do"
        logger.info("Packages to install : %s", to_install_str)
        logger.info("Packages to remove  : %s", to_remove_str)
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
