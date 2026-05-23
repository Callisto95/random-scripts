#!/usr/bin/env nu

def main [] {
    let birth_install = stat -c %W / | into datetime --format "%s";
    let current = date now;
    
    let difference = $current - $birth_install;
    
    print ([(($difference / 1day) | into int) "days"] | str join " ");
}
