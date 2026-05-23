#!/usr/bin/env nu

def load_originals_and_variants []: nothing -> list<record<file: string, list<file: string, folder: string>>> {
    ls "originals" | get name | each { |file|
    
        let raw_name: string = ($file | path parse).stem;
        
        let raw_descendants: list<string> = glob $"**/($raw_name)*";
        let descendants = $raw_descendants | each { |d|
            let parsed = $d | path parse;
            
            let file_name = $parsed.stem;
            let folder = $parsed.parent | path basename;
            
            {
                file: $file_name
                folder: $folder
            }
        }
        
        # let upscaled = $descendants | where {$in.folder == "upscaled"} | get -o 0;
        # let 16x9 = $descendants | where {$in.folder == "16x9"} | get -o 0;
        # let 21x9 = $descendants | where {$in.folder == "21x9"} | get -o 0;
        # let fairphone = $descendants | where {$in.folder == "fairphone"} | get -o 0;
        
        {
            file: ($file | path basename)
            descendants: $descendants
        }
    }
}

def "main orphans" [folder: string] {
    let originals = (load_originals_and_variants | get file | path parse).stem;
    
    let files = ls $folder | get name | path parse | get stem;
    
    $files | where { not ($in in $originals) }
}

def main [] {
    
}
