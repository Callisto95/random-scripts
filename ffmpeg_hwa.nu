#!/usr/bin/env nu

def main [input: string, output: string] {
	if not ($output | str ends-with ".mp4") {
		print "codec may be unsupported!"
		print "use MP4 for working results!"
	}
	
	# '-qp' control quality, 25 by default
	ffmpeg -i $input -vaapi_device /dev/dri/renderD128 -vcodec "hevc_vaapi" -vf format='nv12|vaapi,hwupload' $output
	# -vaapi_device /dev/dri/renderD128
	# =
	# -init_hw_device vaapi=vaapi0:/dev/dri/renderD128 -filter_hw_device vaapi0
}
