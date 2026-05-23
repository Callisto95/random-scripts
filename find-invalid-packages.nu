#!/usr/bin/env nu

def main [] {
	pacman -Qq | lines | enumerate | par-each { |entry|
		let result = yay -Si $entry.item | complete;
		
		if $result.exit_code != 0 {
			print $entry.item;
		}
	}
}
