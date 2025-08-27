"""Provides utility functions for paclare's toml config file."""

import pathlib
import tomllib

from paclare.logs import fatal_error, logger, print_section
from paclare.packagemanagers import PACKAGE_MANAGERS_DEFAULTS, PackageManager

PRESETS = {pkg_mgr.name: pkg_mgr for pkg_mgr in PACKAGE_MANAGERS_DEFAULTS}


def read_config_file(config_file: pathlib.Path) -> dict[PackageManager, list[str]]:
    """Read the config file."""
    print_section(f"Reading configuration from {config_file.as_posix()}")
    package_mgrs = tomllib.loads(config_file.read_text(encoding="utf-8"))
    res = [_read_package_manager(name, fields) for name, fields in package_mgrs.items()]
    logger.info(f"Found {len(res)} configured package managers:")
    logger.debug(
        "\n".join(f"|-- {mgr.name} : {len(pkgs)} packages" for mgr, pkgs in res)
    )
    return {pkg_mgr: packages for pkg_mgr, packages in res}


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
    if not pkg_mgr.list_cmd:
        fatal_error(f'Missing "list_cmd" setting for package manager {name}')
    if not pkg_mgr.install_cmd:
        fatal_error(f'Missing "install_cmd" setting for package manager {name}')
    if not pkg_mgr.uninstall_cmd:
        fatal_error(f'Missing "uninstall_cmd" setting for package manager {name}')
    return pkg_mgr, packages
