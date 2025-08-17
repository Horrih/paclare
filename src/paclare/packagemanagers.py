"""Contains the defaut package managers."""

import dataclasses


@dataclasses.dataclass
class PackageManager:
    """Represents the main commands to use with a package manager."""

    name: str  #: name of the package manager
    list_cmd: str  #: bash command to list installed packages
    install_cmd: str  #: bash command to install a list of packages
    uninstall_cmd: str  #: bash command to uninstall a list of packages


FLATPAK = PackageManager(
    name="flatpak",
    list_cmd="flatpak list --app --columns=application | tail -n +1",
    install_cmd="flatpak install",
    uninstall_cmd="flatpak uninstall",
)

APT = PackageManager(
    name="apt",
    list_cmd="apt-mark showmanual",
    install_cmd="sudo apt install",
    uninstall_cmd="sudo apt remove",
)

DNF = PackageManager(
    name="dnf",
    list_cmd="dnf repoquery --userinstalled",
    install_cmd="sudo dnf install",
    uninstall_cmd="sudo dnf remove",
)

UV = PackageManager(
    name="uv",
    list_cmd="uv tool list | grep -v '\\- ' | cut -f 1 -d ' '",
    install_cmd="uv tool install",
    uninstall_cmd="uv tool uninstall",
)

PACMAN = PackageManager(
    name="pacman",
    list_cmd='pacman -Qeq | grep -v "$(pacman -Qqm)"',
    install_cmd="sudo pacman -S",
    uninstall_cmd="sudo pacman -Rns",
)

PARU = PackageManager(
    name="paru",
    list_cmd="paru -Qeqm",
    install_cmd="paru -S",
    uninstall_cmd="paru -Rns",
)

YAY = PackageManager(
    name="yay",
    list_cmd="yay -Qeqm",
    install_cmd="yay -S",
    uninstall_cmd="yay -Rns",
)


PACKAGE_MANAGERS_DEFAULTS = [FLATPAK, APT, DNF, UV, PACMAN, PARU, YAY]
