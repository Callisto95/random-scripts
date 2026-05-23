#!/bin/sh

print "clearing pacman and yay cache"
yay -Sc --noconfirm
# yes | paru -Scd

print "clearing coredumps"
sudo rm -r /var/lib/systemd/coredump/

print "clearing thumbnail cache"

ls ~/.cache/thumbnails/ | get name | each { rm -r $in; mkdir $in }

print "clearing cargo cache"
# requires: cargo install cargo-cache
cargo cache -a

print "done"
