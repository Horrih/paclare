"""Contains the defaut package managers."""

import dataclasses


@dataclasses.dataclass(eq=False)
class PackageManager:
    """Represents the main commands to use with a package manager."""

    name: str  #: name of the package manager
    list_cmd: str  #: bash command to list installed packages
    install_cmd: str  #: bash command to install a list of packages
    uninstall_cmd: str  #: bash command to uninstall a list of packages


PACKAGE_MANAGERS_DEFAULTS = [
    PackageManager(
        name="pacman",
        list_cmd='pacman -Qeq | grep -v "$(pacman -Qqm)"',
        install_cmd="sudo pacman -S",
        uninstall_cmd="sudo pacman -Rns",
    ),
    PackageManager(
        name="paru",
        list_cmd="paru -Qeqm",
        install_cmd="paru -S",
        uninstall_cmd="paru -Rns",
    ),
    PackageManager(
        name="flatpak",
        list_cmd="flatpak list --app --columns=application | tail -n +1",
        install_cmd="flatpak install",
        uninstall_cmd="flatpak uninstall",
    ),
]
