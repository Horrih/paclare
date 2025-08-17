"""Test paclare's options.py file."""

import logging
import pathlib

import paclare.logs
import paclare.options
from paclare.packagemanagers import UV


def test_options_init() -> None:
    """Test options.parse_args() for the init command."""
    init_options = paclare.options.parse_args(["init", "-q", "output.toml"])
    assert isinstance(init_options, paclare.options.OptionsInit)
    assert init_options.output_file.as_posix() == "output.toml"
    assert paclare.logs.logger.getEffectiveLevel() == logging.WARNING


def test_options_sync(tmp_path: pathlib.Path) -> None:
    """Test options.parse_args() for the sync command."""
    config_txt = """
[uv]
packages = ["pkg1", "pkg2"]
    """
    toml = tmp_path / "config.toml"
    toml.write_text(config_txt)
    sync_options = paclare.options.parse_args(
        ["sync", "-v", "-c", toml.as_posix(), "--dry-run"]
    )

    assert isinstance(sync_options, paclare.options.OptionsSync)
    assert paclare.logs.logger.getEffectiveLevel() == logging.DEBUG
    assert sync_options.pkg_mgrs == [(UV, ["pkg1", "pkg2"])]


def test_options_list(tmp_path: pathlib.Path) -> None:
    """Test options.parse_args() for the list command."""
    config_txt = """
[uv]
packages = []
"""
    toml = tmp_path / "config.toml"
    toml.write_text(config_txt)
    sync_options = paclare.options.parse_args(["list", "-c", toml.as_posix()])
    assert isinstance(sync_options, paclare.options.OptionsList)
    assert paclare.logs.logger.getEffectiveLevel() == logging.DEBUG
    assert sync_options.pkg_mgrs == [UV]
