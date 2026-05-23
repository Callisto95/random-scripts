#!/usr/bin/env nu

def main [version: string] {
	let directory = $"/usr/lib/python($version)";
	
	if not ($directory | path exists) {
		print "Python version does not exist"
		print "available versions are:"
		ls -ls /usr/lib/python* | get name | each {
			print ($in | str replace "python" "");
		}
		return
	}
	
	print "these packages are out-of-date:"
	pacman -Qoq $directory
	
	print "";
	
	yay -S ...(pacman -Qoq $directory | lines);
}
