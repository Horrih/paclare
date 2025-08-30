"""Provides utility functions for paclare's toml config file."""

import pathlib
import tomllib
import sys

from paclare.logs import fatal_error, logger, print_section
from paclare.packagemanagers import PACKAGE_MANAGERS_DEFAULTS, PackageManager

PRESETS = {pkg_mgr.name: pkg_mgr for pkg_mgr in PACKAGE_MANAGERS_DEFAULTS}


def read_config_file(
    config_file: pathlib.Path,
) -> list[tuple[PackageManager, list[str]]]:
    """Read the config file."""
    print_section(f"Reading configuration from {config_file.as_posix()}")
    if not config_file.exists():
        fatal_error(f"Config path {config_file.as_posix()} does not exist.")

    package_mgrs = tomllib.loads(config_file.read_text(encoding="utf-8"))
    res = [_read_package_manager(name, fields) for name, fields in package_mgrs.items()]
    logger.info(f"Found {len(res)} configured package managers:")
    logger.debug(
        "\n".join(f"|-- {mgr.name} : {len(pkgs)} packages" for mgr, pkgs in res)
    )
    return res


def _read_package_manager(name: str, fields: dict) -> tuple[PackageManager, list[str]]:
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
    )
    packages = sorted(fields.get("packages"))

    def check_missing_field(field: str) -> None:
        if not getattr(pkg_mgr, field):
            fatal_error(f'Missing "{field}" setting for package manager {name}')

    check_missing_field("list_cmd")
    check_missing_field("install_cmd")
    check_missing_field("uninstall_cmd")
    return pkg_mgr, packages
