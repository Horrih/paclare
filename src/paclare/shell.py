"""Wrapper functions for bash commands."""

import subprocess

from paclare.logs import GREY, RESET, logger


def run_user_command(command: str, *, dry_run: bool) -> None:
    """Run any bash command except if dry_run is enabled."""
    logger.info("Running command : %s", command)
    if not dry_run:
        subprocess.run(["/bin/sh", "-c", command], check=True)  # noqa: S603


def run_helper_command(command: str) -> str:
    """Run any bash command except if dry_run is enabled."""
    logger.debug("%s%s%s", GREY, command, RESET)
    output = subprocess.run(  # noqa: S603
        ["/bin/sh", "-c", command],
        check=True,
        capture_output=True,
    )
    return output.stdout.decode(encoding="utf-8")
