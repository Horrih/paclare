# paclare - A minimalist declarative package manager

[![codecov](https://codecov.io/github/Horrih/paclare/graph/badge.svg?token=8H0KZLUUBZ)](https://codecov.io/github/Horrih/paclare)

* [Why paclare](#why-paclare-)
  * [Intro](#intro)
  * [A config file to rule them all](#a-config-file-to-rule-them-all)
  * [Why not nix ?](#why-not-nix-)
* [Getting started](#getting-started)
  * [Installation](#installation)
  * [Setting up your config : paclare init](#setting-up-your-config--paclare-init)
  * [Check what you have installed : paclare list](#check-what-you-have-installed--paclare-list)
  * [Installing new packages : paclare sync](#installing-new-packages--paclare-sync)
* [Adding a new package manager](#adding-a-new-package-manager)
* [Contributing](#contributing)

## Why paclare ?

### Intro
Many package managers end up cluttering your environment. Stuff you don't
need anymore is installed and you can't remember why you installed it.

Conversely, when setting up a new machine, you may not remember all you
need to install to have a similar setup as on the previous one.

You may also suffer from fragmented configuration : apt, flatpak, pip, it's
difficult to have a one size fits all solution.

Paclare, contraction of Package deClare, aims to solve these issues.

### A config file to rule them all

For each package manager you use, you put the packages you need in a config.toml file.

```toml
[apt]
packages = [
    "emacs",   # You can add a comment if you want
    "vim",     # Please don't install this one
    "flatpak", # Package manager for portable gui apps
]

[flatpak]
packages = [
    "org.mozilla.firefox",
]
```

Here is what paclare will do :
- If a package is not installed yet, paclare will install it
- If a package is installed but not on the list, paclare will uninstall it
- Paclare supports some of the most popular package managers out of the box
- If paclare's does not support your package manager natively, you can add it
yourself in the toml file (read-on for a detailed explanation).

### Why not nix ?
Other declarative package managers exist, like nix or guix, they are
far more powerful but also far more complex.

## Getting started

### Installation

Paclare is a python package, it requires python3.12 or later.

Currently, paclare has been packaged on the pypi index, so you can install
it through pip, pipx, or uv.

I recommend uv, as it is becoming the defacto modern python package manager.

```bash
pip install paclare
pipx install paclare
uv tool install paclare
```

### Setting up your config : paclare init

Let's assume that you use package managers already supported by paclare.

```bash
mkdir ~/.config/paclare  # Or symlink to your dotfiles repo
paclare init ~/.config/paclare/paclare.toml
```

This file will only contain your **explicitely** installed packages.
Dependencies should not appear there.

### Check what you have installed : paclare list

```bash
paclare list
```

This command will read your config file, detect the package managers you
have enabled there, and for each one of them list the explicitely installed
packages.

### Installing new packages : paclare sync

```bash
paclare sync
```

This command will read your config file, detect the package managers and
the associated packages.

It will then compare these lists to what is actually installed on your machine.
The missing packages will be installed, the leftovers uninstalled.

## Adding a new package manager

Paclare won't support every package manager out of the box, but you can
add your own.

You must provide three variables in your toml config :

```toml
[mypackagemgr]
list_cmd = "mypackagemgr --list-user-installed-packages"
install_cmd = "mypackagemgr install"
uninstall_cmd = "mypackagemgr uninstall"
packages = [
    "pkg1",
    "pkg2"
]
```
The commands specified here will be interpreted by your machine's
default shell, /bin/sh.

This means you can use your pipes, cut, sed, and pals to help you here.

You can check out the commands used for the built-in package managers
[here](https://github.com/Horrih/paclare/blob/main/src/paclare/packagemanagers.py)

You can also override paclare's commands for built-in package managers by
defining these variables.

## Contributing

Contributions are of course welcome, especially to add new package managers
to the supported list.

New features and PRs will be considered, but I intend to keep paclare as minimal
as possible.
