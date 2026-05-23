#!/usr/bin/env nu

# https://lib.rs/crates/scx_loader

def main [operation: string, scheduler: string = "scx_lavd"] {
	match $operation {
		"stop" => {
			dbus-send --system --print-reply --dest=org.scx.Loader /org/scx/Loader org.scx.Loader.StopScheduler;
		}
		"start" => {
			dbus-send --system --print-reply --dest=org.scx.Loader /org/scx/Loader org.scx.Loader.StartScheduler $"string:($scheduler)" uint32:0;
		}
		"get" => {
			dbus-send --system --print-reply --dest=org.scx.Loader /org/scx/Loader org.freedesktop.DBus.Properties.Get string:org.scx.Loader string:CurrentScheduler;
		}
		"list" => {
			dbus-send --system --print-reply --dest=org.scx.Loader /org/scx/Loader org.freedesktop.DBus.Properties.Get string:org.scx.Loader string:SupportedSchedulers;
		}
		"switch" => {
			dbus-send --system --print-reply --dest=org.scx.Loader /org/scx/Loader org.scx.Loader.SwitchScheduler $"string:($scheduler)" uint32:2;
		}
		_ => {
			print "unknown command"
			exit 1
		}
	}
}
