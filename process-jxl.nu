#!/usr/bin/env nu

def main [...files: string] {
    $files | par-each { |file|
        let target = $file | str replace ".jxl" ".png";
        djxl $file $target;
        /home/callisto/.cargo/bin/oxipng --opt=2 --preserve --filters "0-9" --fix $target;
    }
    notify-send --icon=image-invert --app-name="Decode JXL" $"Decoding of ($files | length) files done!"
}
