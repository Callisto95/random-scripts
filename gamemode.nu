#!/usr/bin/env nu

def main [mode: string] {
	match $mode {
		"start" => {
			notify-send --app-name "GameMode" "GameMode started";
			# ./scx.nu "start"
		}
		"end" => {
			notify-send --app-name "GameMode" "GameMode ended";
			# ./scx.nu "stop"
		}
		_ => {
			print "unknown mode"
			exit 1
		}
	}
}
