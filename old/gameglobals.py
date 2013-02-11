'''
Created on 26.3.2012

@author: Tarmo
'''
import gameutil
import os, sys, random

WEAPON_PUNCH = gameutil.Weapon("punch", 10, "Your powerful fist.", 5, 5, "punch")
WEAPON_KICK = gameutil.Weapon("kick", 10, "Your powerful leg.", 7, 3, "kick")
WEAPON_BITE = gameutil.Weapon("bite", 10, "Your powerful mouth.", 15, 10, "bite")
    
PATH_AREASCHEMA = str(os.path.dirname(sys.argv[0])) + "areaschema.xsd"
PATH_HOME_BEDROOM = str(os.path.dirname(sys.argv[0])) + "base/area_home_bedroom.xml"

AREA_NAME_BEDROOM = "Apartment building - Stairs - Home - Bedroom"

INITCONTENT_SKILLS = [gameutil.Skill("Spastic Twitching", 5), \
                      gameutil.Skill("Rolling with the punches", 3, gameutil.DamageModifier("resist", "impact", 10, 3, True), \
                      gameutil.Skill("Eating", 30)), \
                      gameutil.Skill("Being awful at everything", 10), \
                      gameutil.Skill("Being awful at everything", 3)]

INITCONTENT_STATS = [gameutil.Stat("Strength", 3), \
                     gameutil.Stat("Fastness", 5), \
                     gameutil.Stat("Height", 180), \
                     gameutil.Stat("Width", 50), \
                     gameutil.Stat("Mouth power", 15)]

INITCONTENT_TRAITS = [gameutil.DamageModifierOwner("Not wearing a hat")]
INITCONTENT_ITEMS = [gameutil.Item("Crumpled piece of paper", 5, desc=False)]

INITCONTENT_CMD_NAP = gameutil.Command("take a nap", "global", defOutcome=gameutil.Outcome("def", random.randint(3300, 3670), desc=gameutil.DescriptionContainer(line="You take a nap. You wake up feeling fresh and hip, like the top dog you deep down know you are.")))

INITCONTENT_AMOUNT_SKILLS = 2
INITCONTENT_AMOUNT_TRAITS = 1
INITCONTENT_AMOUNT_ITEMS = 1

