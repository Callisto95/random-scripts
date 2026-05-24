#!/usr/bin/env nu

def main [] {
    sudo reflector --verbose --protocol https --country Germany --sort rate --save /etc/pacman.d/mirrorlist;
}
