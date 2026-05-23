#!/usr/bin/env nu

pacman -Qqem | save --force ~/Documents/packages/aur-packages.txt;
pacman -Qqen | save --force ~/Documents/packages/packages.txt;
flatpak list --columns=name,application,version,branch | save --force ~/Documents/packages/flatpaks-full.txt;
flatpak list --columns=application | save --force ~/Documents/packages/flatpaks.txt;
