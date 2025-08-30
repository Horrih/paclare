"""Tests for commands.py."""

import logging
import pathlib

import pytest

import paclare.commands
import paclare.packagemanagers


def test_list(caplog: pytest.LogCaptureFixture) -> None:
    """Test the 'list' main command output."""
    caplog.set_level(logging.INFO)
    pkg_mgr = paclare.packagemanagers.PackageManager(
        name="my_pkg_mgr",
        list_cmd="echo pkg1",
        install_cmd="",
        uninstall_cmd="",
    )
    options = paclare.commands.OptionsList([pkg_mgr])
    paclare.commands.list_packages(options)
    output = "\n".join(rec.message for rec in caplog.records)
    assert pkg_mgr.name in output
    assert "pkg1" in output


def test_init(tmp_path: pathlib.Path) -> None:
    """Test the 'init' main command output."""
    toml = tmp_path / "config.toml"
    pkg_mgr = paclare.packagemanagers.PackageManager(
        name="my_pkg_mgr",
        list_cmd="echo pkg1; echo pkg2",
        install_cmd="",
        uninstall_cmd="",
    )
    options = paclare.commands.OptionsInit(toml, [pkg_mgr])
    paclare.commands.init_config(options)

    # Case 1 : the package_mgr is not on the PATH : no output
    assert toml.read_text(encoding="utf-8") == ""

    # Case 2 : the package_mgr is not on the path : this should work as expected
    pkg_mgr.name = "bash"
    paclare.commands.init_config(options)
    output = toml.read_text(encoding="utf-8")
    expected = f"""[{pkg_mgr.name}]
packages = [
    "pkg1",
    "pkg2"
]
"""
    assert output == expected


def test_sync(tmp_path: pathlib.Path) -> None:
    """Test the 'sync' main command.

    For this test we define a mock package manager that will dump the packages
    to install/remove in a file that our test will check
    """
    define_dump_args = "dump_args() { f=$1; shift; echo $@ > $f; }"
    installed = tmp_path / "installed"
    removed = tmp_path / "removed"
    pkg_mgr = paclare.packagemanagers.PackageManager(
        name="my_pkg_mgr",
        list_cmd="echo pkg1; echo pkg2",
        install_cmd=f"{define_dump_args}; dump_args {installed}",
        uninstall_cmd=f"{define_dump_args}; dump_args {removed}",
    )
    pkgs = ["pkg2", "pkg3"]
    # pkg1 should be removed, pkg2 kept, pkg3 installed
    options = paclare.commands.OptionsSync([(pkg_mgr, pkgs)], dry_run=False)
    paclare.commands.sync_packages(options)
    assert installed.read_text(encoding="utf-8") == "pkg3\n"
    assert removed.read_text(encoding="utf-8") == "pkg1\n"
