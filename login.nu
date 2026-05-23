#!/usr/bin/env nu

def main [] {
    ls ~/.ssh | get name | where { $in | str ends-with ".pub" } | str replace ".pub" "" | each { ssh-add $in };
    
    pactl set-source-volume virtual-microphone 200%;
}
