#!/usr/bin/env nu

let WEBHOOK = "WEBHOOK_URL";

let today = date now | format date "%F";

let mensen = [
    {
        id: 102,
        name: "Mensa 1",
        colour: "#00FFFF",
    },
    {
        id: 111,
        name: "360 Grad",
        colour: "#880088",
    },
]

let menus = $mensen | each {
    |mensa|
    
    let menu  = http get $"https://sls.api.stw-on.de/v1/locations/($mensa.id)/menu/($today)?time=all";
    
    if ($menu.meals | is-empty) {
        return null;
    }
    
    if (not ($menu.announcements | is-empty)) {
        http post $WEBHOOK {content: "ANNOUNCEMENT!!!"};
    }
    
    let meals = $menu.meals | each {
        |entry|
        
        {
            name: $entry.name,
            price: $entry.price.student,
            lane: $entry.lane.name,
        };
    }
    
    {
        mensa: $mensa,
        meals: $meals,
    }
}

if ($menus | is-empty) {
    return;
}

let embeds = $menus | each {
    |menu|
    
    # $menu.meals | group-by --to-table lane | each {
    #     |lane_meals|
        
        
        
    #     {
    #         title: $"($menu.mensa.name) - ($lane_meals.lane)",
    #         footer: {
    #             text: $today,
    #         },
    #         fields: 
            
    #     }
    # }
    
    let fields = $menu.meals | each {
        |meal|
        
        {
            name: $meal.name,
            value: $"($meal.price)€",
            inline: true,
        }
    }
    
    {
        title: $menu.mensa.name,
        description: $today,
        fields: $fields,
        color: ($menu.mensa.colour | str substring 1.. | into int --radix 16),
    }
}

http post --content-type application/json $WEBHOOK {embeds: $embeds}
