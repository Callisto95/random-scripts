def main [input: string, subtitles: string, output: string] {
	print $"'($input)' is the base video"
	print $"'($subtitles)' is the subtitles"
	print $"'($output)' is the output"
	
	let answer = ["no" "yes"] | input list "correct?"
	
	if $answer != "yes" {
		return
	}
	
	ffmpeg -i $input -i $subtitles -c copy -c:s mov_text -metadata:s:s:0 language=eng $output
}
