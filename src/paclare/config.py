"""Provides utility functions for paclare's toml config file."""

import pathlib
import tomllib
import typing

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
    logger.info("Found %s configured package managers:", len(res))
    logger.debug(
        "\n".join(f"|-- {mgr.name} : {len(pkgs)} packages" for mgr, pkgs in res)
    )
    return res


def _read_package_manager(name: str, fields: dict) -> tuple[PackageManager, list[str]]:
    """Read the package manager options and packages from the relevant toml section."""
    preset = PRESETS.get(name)

    def get_field(field_name: str) -> str:
        field_value = fields.get(field_name)
        if not field_value and preset:
            field_value = getattr(preset, field_name)
        if not field_value:
            fatal_error(f'{name} : Missing "{field_name}" setting')
        if not isinstance(field_value, str):
            fatal_error(f'{name} : "{field_name}" should be a string')
        return typing.cast(str, field_value)

    pkg_mgr = PackageManager(
        name,
        list_cmd=get_field("list_cmd"),
        install_cmd=get_field("install_cmd"),
        uninstall_cmd=get_field("uninstall_cmd"),
    )
    packages = fields.get("packages")
    if not isinstance(packages, list) or not all(
        isinstance(pkg, str) for pkg in packages
    ):
        fatal_error(f'{name} : "packages" missing, should be a list of package names')
    return pkg_mgr, sorted(typing.cast(list[str], packages))
