#!/usr/bin/env nu

def main [] {
    let orphans = pacman -Qtdq | lines;
    
    if ($orphans | is-empty) {
        print "nothing to remove"
        return
    }
    
    sudo pacman -Rns ...$orphans;
}
