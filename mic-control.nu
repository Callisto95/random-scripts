#!/bin/env nu

def get_sources []: nothing -> list<record<id: string, name: string, controller: string, opmode: string, resolution: string, status: string>> {
	pactl list sources short | split row "\n" | each { $in | str replace --all --regex "[\t ]+" " " | parse "{id} {name} {controller} {opmode} {resolution} {status}" | get 0 } | where { not ($in.name | str contains "easyeffects") }
}

def is_source_muted []: string -> bool {
	(pactl get-source-mute $in | parse "Mute: {state}" | get 0 | get state) == "yes"
}

def set_all_muted [state: bool]: nothing -> nothing {
	get_sources | each { |source| pactl set-source-mute $source.name $state };
	null
}

def main [] {
	print "use a subcommand!";
	exit 1;
}

def "main mute" [] {
	set_all_sources true;
	null
}

def "main unmute" [] {
	set_all_muted false;
	null
}

def "main toggle" [] {
	let sources = get_sources;
	
	let target_state = not (($sources | get 0).name | is_source_muted);
	
	set_all_muted $target_state;
	
	if $target_state {
		notify-send --icon=microphone-sensitivity-muted --app-name=MicMute "Microphones have been muted";
	} else {
		notify-send --icon=microphone-sensitivity-high --app-name=MicMute "Microphones have been unmuted";
	}
	
	null
}

def "main status" [] {
	get_sources | each { |source|
		print $"($source.name): (pactl get-source-mute $source.name)";
	}
}
