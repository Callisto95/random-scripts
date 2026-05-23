#!/usr/bin/env nu

clear;

def main [start: int = 0] {
	let lines = open packages.txt | lines;
	$lines | enumerate | each { |entry|
		if $entry.index < $start {
			return;
		}
		
		print $"($entry.index + 1)/($lines | length) -- ($entry.item)";
		
		pacman -Qi $entry.item;
		
		if (input) == "q" {
			exit;
		}
		
		clear;
	}
	
	null
}
