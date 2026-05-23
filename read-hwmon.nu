#!/usr/bin/env nu

def "main pwm" [hwmon: int, pwm: int] {
	let path = $"/sys/class/hwmon/hwmon($hwmon)/pwm($pwm)";
	
	if not ($path | path exists) {
		print "Path does not exist"
		exit 1;
	}

	^watch --interval 1 -- cat $path;
}

def "main temp" [hwmon: int, temp: int] {
	let label = $"/sys/class/hwmon/hwmon($hwmon)/temp($temp)_label";
	let input = $"/sys/class/hwmon/hwmon($hwmon)/temp($temp)_input";
	
	if not ($label | path exists) {
		print "Path does not exist"
		exit 1;
	}

	^watch --interval 1 -- $"cat ($label); cat ($input);"
}

def main [] {}
