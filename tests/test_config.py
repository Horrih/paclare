"""Tests the configuration import functions."""

import pathlib

import pytest

import paclare.config
import paclare.logs
import paclare.packagemanagers


def _error_to_exception(text: str):
    """Raise a runtime error with the input text."""
    raise RuntimeError(text)


def test_missing_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Check that read_config_file raises a fatal error when file missing."""
    monkeypatch.setattr("paclare.config.fatal_error", _error_to_exception)
    with pytest.raises(RuntimeError):
        paclare.config.read_config_file(pathlib.Path("dummy.toml"))


def test_builtin_pkg_mgr(tmp_path: pathlib.Path) -> None:
    """Check config parsing for one of paclare's built-in package managers."""
    toml = tmp_path / "config.toml"
    text = """
# A predefined package manager, we only list the packages
[uv]
packages = [
    "uv1",
    "uv2"
]
"""
    toml.write_text(text)
    pkg_mgrs = paclare.config.read_config_file(toml)
    uv, uv_pkgs = pkg_mgrs[0]
    assert uv.name == paclare.packagemanagers.UV.name
    assert uv.install_cmd == paclare.packagemanagers.UV.install_cmd
    assert uv_pkgs == ["uv1", "uv2"]


def test_override_builtin(tmp_path: pathlib.Path) -> None:
    """Override commands for one of paclare's built-in package managers."""
    toml = tmp_path / "config.toml"
    install_cmd = "install"
    list_cmd = "list"
    uninstall_cmd = "uninstall"
    text = f"""
[uv]
list_cmd = "{list_cmd}"
install_cmd = "{install_cmd}"
uninstall_cmd = "{uninstall_cmd}"
packages = [
    "uv1",
    "uv2"
]
"""
    toml.write_text(text)
    pkg_mgrs = paclare.config.read_config_file(toml)
    uv, uv_pkgs = pkg_mgrs[0]
    assert uv.name == paclare.packagemanagers.UV.name
    assert uv.install_cmd == install_cmd
    assert uv.uninstall_cmd == uninstall_cmd
    assert uv.list_cmd == list_cmd
    assert uv_pkgs == ["uv1", "uv2"]


def test_custom_pkg_mgr(tmp_path: pathlib.Path) -> None:
    """Define a new package manager."""
    toml = tmp_path / "config.toml"
    tool_name = "toolname"
    install_cmd = "install"
    list_cmd = "list"
    uninstall_cmd = "uninstall"
    text = f"""
[{tool_name}]
list_cmd = "{list_cmd}"
install_cmd = "{install_cmd}"
uninstall_cmd = "{uninstall_cmd}"
packages = [
    "pkg1",
    "pkg2"
]
"""
    toml.write_text(text)
    pkg_mgrs = paclare.config.read_config_file(toml)
    tool, tool_pkgs = pkg_mgrs[0]
    assert tool.name == tool_name
    assert tool.install_cmd == install_cmd
    assert tool.uninstall_cmd == uninstall_cmd
    assert tool.list_cmd == list_cmd
    assert tool_pkgs == ["pkg1", "pkg2"]


def test_missing_custom_commands(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Define a new package manager but you forgot to define some commands."""
    toml = tmp_path / "config.toml"
    text = """
[some_tool]
list_cmd = "list"
packages = ["pkg1"]
"""
    toml.write_text(text)

    monkeypatch.setattr("paclare.config.fatal_error", _error_to_exception)
    with pytest.raises(RuntimeError):
        paclare.config.read_config_file(toml)
