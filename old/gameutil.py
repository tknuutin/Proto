'''
Created on 16.10.2011

@author: Tarmo
'''
from requirements import checkRequirement
import random, copy
import control
import math

class Quest(object):
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        
class VisitedArea(object):
    def __init__(self, name, loc, time):
        self.name = str(name)
        self.location = loc
        self.visitCount = 0
        self.usedCommands = False
        self.usedNpcSpawns = False
        self.usedItemSpawns = False
        self.usedEvents = False
        self.lastVisit = time
        self.items = []
        self.npcs = []
        
    def addItem(self, item, itemPos):
        itemTuple = item, itemPos
        self.items.append(itemTuple)
        if len(self.items) > 1:
            self.items = sorted(self.items, key=lambda item: item[0].name)
        
    def incrementVisitCounter(self):
        self.visitCount = self.visitCount + 1
        
    def addUsedCommand(self, commandName):
        if self.usedCommands == False:
            self.usedCommands = []
        self.usedCommands.append(commandName)
        
    def addUsedEvent(self, eventName):
        if self.usedEvents == False:
            self.usedEvents = []
        self.usedEvents.append(eventName)
        
    def checkIfCommandUsed(self, commandName):
        if self.usedCommands == False:
            return False
        elif commandName in [x.name for x in self.usedCommands]:
            return True
        else: return False
        
    def checkIfEventUsed(self, eventName):
        if self.usedEvents == False:
            return False
        elif eventName in self.usedEvents:
            return True
        else: return False
    
    def checkIfItemSpawnUsed(self, spawnName):
        if self.usedItemSpawns == False:
            return False
        elif spawnName in self.usedItemSpawns:
            return True
        else: return False
    
    def checkIfNpcSpawnUsed(self, spawnName):
        if self.usedNpcSpawns == False:
            return False
        elif spawnName in self.usedNpcSpawns:
            return True
        else: return False
        
    def addUsedNpcSpawn(self, spawnName):
        if self.usedNpcSpawns == False:
            self.usedNpcSpawns = []
        self.usedNpcSpawns.append(spawnName)
        
    def addUsedItemSpawn(self, spawnName):
        if self.usedItemSpawns == False:
            self.usedItemSpawns = []
        self.usedItemSpawns.append(spawnName)
        

        

'''
Superclass for any class that owns Requirements. Implements functions for checking and adding requirements.
'''
class RequirementOwner(object):
    def __init__(self):
        self.reqs = []
    
    '''
    Checks the all the requirements of the object with the given controller. If the object has no requirements or at least
    one of the requirements is True, will return True. Also returns a notice with the type of String, if a requirement fails
    and it has a failureNotice attribute.
    
    Returns:     check - boolean if check passes, notice - either False or a String stating the reason for failing
    '''
    def checkRequirements(self, controller):
        if not self.reqs:
            return True, False
        else:
            notice = False
            for x in self.reqs:
                if checkRequirement(controller, x) == True:
                    #print "passing requirement " + x.name
                    return True, False
                #print "failing requirement " + x.name
                if x.failureNotice != False:
                    notice = x.failureNotice
            return False, notice
    
    '''
    Adds a requirement to the requirements of this object. Must be type ReqContainer.
    '''
    def addRequirement(self, req):
        if self.reqs == False:
            self.reqs = []
        self.reqs.append(req)

'''
Superclass for all classes owning Outcomes. Implements functions for adding and getting outcomes.
'''
class OutcomeOwner(object):
    def __init__(self):
        self.outcomes = []
    
    '''
    Get the outcome of the object based on the requirements. The first requirement that passes and has a resultingOutcome
    attribute will set the resulting outcome. If no passing requirement has a resultingOutcome, or a corresponding outcome is not
    found, will return the first outcome on the list - the default outcome.
    '''
    def getOutcome(self, controller):
        failureNotice = None
        
        for outcome in self.outcomes:
            if outcome.reqs:
                for req in outcome.reqs:
                    if checkRequirement(controller, req):
                        return outcome, None
                    elif not failureNotice and req.failureNotice:
                        failureNotice = req.failureNotice
            else:
                return outcome, None
        return None, failureNotice
    
    '''
    Adds a outcome to the outcomes of this object. Must be type Outcome.
    '''
    def addOutcome(self, outcome):
        self.outcomes.append(outcome)
    
'''
Class defines a command for an area.
'''
class Command(OutcomeOwner):
    def __init__(self, name, type, singular=False, randomized=False, defOutcome=False):
        OutcomeOwner.__init__(self)
        
        self.name = str(name)
        self.type = type
        self.aliasList = []
        self.singular = singular
        self.randomized = randomized
        self.listReqs = []
        self.nextInSequence = False
        self.exclusiveSequence = False
        self.exclusive = False
        self.reqrefs = []
        
        if defOutcome:
            self.outcomes.append(defOutcome)
        
    '''
    Iterates through the list requirements and returns True if at least one of them holds true. Return False otherwise.
    '''
    def checkListRequirements(self, controller):
        if not self.listReqs:
            return True
        else:
            for x in self.listReqs:
                if checkRequirement(controller, x) == True:
                    return True
            return False
    
    '''
    Adds a list requirement for the command.
    '''  
    def addListRequirement(self, req):
        self.listReqs.append(req)
        
    '''
    Adds a list of aliases for the command.
    '''
    def addAliasList(self, alias):
        self.aliasList = map(lambda x: str(x).lower(), alias)
        
    def addOutcome(self, outcome):
        self.outcomes.append(outcome)
        for x in outcome.reqs:
            if x.name in self.reqrefs:
                self.listReqs.append(x)

'''
Container class for the elements of a description event. Can hold lines of text, paragraphs, and instructions between the paragraps.
'''
class DescriptionContainer(object):
    def __init__(self, line=False):
        self.line = line
        self.hasParagraphs = False
        self.pgraphs = []
    
    '''
    Adds a single line to the container. Sets the description into simple single line mode.
    '''
    def addSingleLine(self, line):
        self.line = str(line)
        self.hasParagraphs = False
    
    '''
    Adds a paragraph to the list of paragraphs. Must be DParagraphContainers.
    '''
    def addParagraph(self, p):
        self.hasParagraphs = True
        self.pgraphs.append(p)

'''
Container class for a paragraps. Must always include at least one line of text. Can contain strings or instructions.
'''
class DParagraphContainer(object):
    def __init__(self, line):
        self.firstLine = line
        self.hasElements = False
        self.elements = []
    
    '''
    Add an element to the container. Must be an Instruction or a string.
    '''
    def addElement(self, element):
        self.hasElements = True
        self.elements.append(element)

'''
An event in the game, composed of an Outcome, name, keywords, and other attributes.
'''
class Event(OutcomeOwner):
    def __init__(self, name, singular, outcome):
        OutcomeOwner.__init__(self)
        self.name = str(name)
        self.addOutcome(outcome)
        self.keywords = False
        self.singular = singular
        
    def addKeywordList(self, list):
        self.keywords = list
        
    def toTransevent(self):
        te = TransEvent(self.name, self.singular, self.outcomes[0])
        te.outcomes = self.outcomes
        return te
    
    def isTransevent(self):
        return False

'''
An event that happens when exiting or entering an area.
'''
class TransEvent(Event):
    def __init__(self, name, singular, outcome):
        Event.__init__(self, name, singular, outcome)
        
        self.exclusive = False
        self.areaReqs = []
        self.chance = False
        
    def setExclusive(self):
        self.exclusive = True
        
    def setChance(self, chance):
        self.chance = chance
        
    def addAreaRequirement(self, areaName):
        self.areaReqs.append(areaName)
        
    def isTransevent(self):
        return True

'''
A collection of Instructions and descriptions that result from a Command, Event, or similar entity.
'''
class Outcome(RequirementOwner):
    def __init__(self, name, time, desc=None):
        RequirementOwner.__init__(self)
        self.name = name
        self.time = time
        self.description = desc or False #TODO: refactor?
        self.damageNode = False
        self.healNode = False
        self.expGained = False
        self.newNode = False
        self.modifyNode = False
        self.eventLaunched = False
        self.move_to_area = False
        
    def addDescription(self, desc):
        self.description = desc
        
    def addTakeDamageNode(self, node):
        self.damageNode = node
    
    def addHealNode(self, node):
        self.healNode = node
        
    def addNewNode(self, node):
        self.newNode = node
        
    def addModifyNode(self, node):
        self.modifyNode = node

'''
A location described as a list of strings.
'''
class Location(object):
    def __init__(self, locTree, exact):
        self.name = None
        
        self.locTree = locTree
        self.exact = exact
        
    def getDescription(self):
        if self.name != None or self.name != False:
            return "You are in the " + str(self.name) + ". It seems to you that your exact location is: \n" + self.giveFormattedLoc()
        else:
            return "You decide that your exact location is " + self.giveFormattedLoc()
            
    def giveFormattedLoc(self):
        counter = 0
        temp = ""
        
        while counter < len(self.locTree):
            if counter != 0:
                temp = temp + " - "
            temp = temp + self.locTree[counter]
            counter = counter + 1
        
        return str(temp)
    
    def checkBranchLevel(self, comparisonLoc):
        lastMatch = 0
        
        compTree = comparisonLoc.locTree
        stop = False
        counter = 0
        
        while stop == False:
            if  counter >= len(compTree) or\
                counter >= len(self.locTree) or\
                self.locTree[counter] != compTree[counter]:
                
                stop = True
            else:
                lastMatch = counter + 1
                
            counter = counter + 1
        return lastMatch
    
    def isSameLocation(self, comparisonLoc):
        compTree = comparisonLoc.locTree
        isSame = True
        
        if len(self.locTree) == len(compTree):
            stop = False
            i = 0
            while stop == False:
                if self.locTree[i] != compTree[i]:
                    isSame = False
                i = i + 1
                if i > len(self.locTree) or isSame == False:
                    stop = True
        else:
            isSame = False
        return isSame
    
    def isSiblingLocation(self, comparisonLoc):
        compTree = comparisonLoc.locTree
        
        if len(self.locTree) == len(compTree):
            if len(self.locTree) == 1:
                if self.locTree[0] == compTree[0]:
                    return True
                else:
                    return False
            elif self.locTree[(len(self.locTree) - 2)] == compTree[(len(compTree) - 2)]:
                return True
            else:
                return False
                
        else:
            return False
        
    def isChildLocationOf(self, comparisonLoc):
        compTree = comparisonLoc.locTree
        
        if len(self.locTree) >= len(compTree):
            
            for i in range(len(self.locTree)):
                if self.locTree[i] != compTree[i]:
                    return False
            #if survived through the loop, return true
            return True
        
        else:
            return False
        
'''
A class that implements the usecount attribute and the incrementUseCount-method.
'''
class UseCountable(object):
    def __init__(self):
        self.usecount = 0
        
    def incrementUseCount(self):
        self.usecount = self.usecount + 1

'''
Class that implements the basic attributes and methods related to owning DamageModifiers, that is, resists and weaknesses.
'''
class DamageModifierOwner(UseCountable):
    def __init__(self, name, resists=None, weaks=None):
        UseCountable.__init__(self)
        self.name = str(name)
        
        if resists:
            self.resists = [resists]
        else:
            self.resists = []
            
        if weaks:
            self.weaks = [weaks]
        else:
            self.weaks = []
        
    def getDescription(self):
        return self.name.upper() + " is a thing you have. " + self.getModifierDescription()
        
    def getModifierDescription(self):
        modstr = ""
        for x in self.resists:
            #print "modstr: " + modstr + x.getDescription() + " "
            modstr = modstr + x.getDescription() + " "
        for x in self.weaks:
            modstr = modstr + x.getDescription() + " "
        return modstr
    
    def addResist(self, resist):
        self.resists.append(resist)
        
    def addWeakness(self, weakness):
        self.weaks.append(weakness)

'''
A class with a numeric value that can be adjusted automatically and periodically due to certain attributes. Can also hold an event
that will be launched once the adjusting reaches a certain threshold.
'''
class Autoadjustable(UseCountable):
    def __init__(self, value):
        UseCountable.__init__(self)
        self.value = value
        self.hasAutoadjust = False
        
    def getAutoAdjustDescription(self):
        desc = "It has the value " + str(self.value) + ". "
        if self.hasAutoadjust:
            if self.autoadjustAdd:
                desc = desc + "The value is rising. "
            elif self.autoadjustMultiply:
                if self.autoadjustAmount > 1:
                    desc = desc + "The value is rising exponentially! "
                else:
                    desc = desc + "The value is decreasing exponentially! "
            else:
                desc = desc + "The value is decreasing. "
        return desc
    
    def setAutoAdjust(self, mode, amount, interval, threshold, event):
        if self.value != False:
            self.autoadjustAdd = False
            self.autoadjustSubtract = False
            self.autoadjustMultiply = False
            self.hasAutoadjust = True
            self.autoadjustEvent = False
            self.autoadjustAmount = amount
            self.lastAutoadjust = False
            
            if mode == "add":
                self.autoadjustAdd = True
            elif mode == "subtract":
                self.autoadjustSubtract = True
            else:
                self.autoadjustMultiply = True
                
            self.autoadjustInterval = interval
            self.autoadjustThreshold = threshold
            if event != None and event != False:
                self.autoadjustEvent = event

'''
Something that can have an attack. Attacks have damage, time, damage types, hits, and ammoPerShot attributes.
'''
class AttackOwner(object):
    def __init__(self):
        self.hasAttack = False
        
    def getAttackDescription(self):
        if self.hasAttack:
            desc = "It does " + str(self.attackDmg * self.attackHits) + " damage in " + str(self.attackTime) + " seconds. "
            if self.ammoPerShot != False:
                desc = desc + "It consumes " + str(self.ammoPerShot) + " ammo per shot. "
            return desc
        else: return ""
        
    def addAttack(self, damage, time):
        self.hasAttack = True
        self.attackDmg = damage
        self.attackTime = time
        self.attackTypes = []
        self.attackHits = 1
        self.ammoPerShot = False
        
    def addAttackType(self, type):
        if self.hasAttack:
            self.attackTypes.append(str(type))

'''
An action that can be accessed through a verb or verbs. Can be associated with an attack or an event.
'''
class Action(AttackOwner):
    def __init__(self, verb):
        AttackOwner.__init__(self)
        self.verbs = [str(verb)]
        self.event = False
        self.name = False
        
    def getActionDescription(self):
        desc = "You can use it with the "
        if len(self.verbs) == 1:
            desc = desc + "verb '" + self.verbs[0] + "'. "
        elif len(self.verbs) > 1:
            desc = desc + "verbs "
            for i in range(0, len(self.verbs)):
                if i < (len(self.verbs) - 1):
                    desc = desc + "'" + self.verbs[i] + "', "
                else:
                    desc = desc + "and '" + self.verbs[i] + "'. "
        if self.hasAttack:
            desc = desc + self.getAttackDescription()
        return desc
        
    def addVerb(self, verb):
        self.verbs.append(str(verb))
            
    def setEvent(self, event):
        self.event = event

'''
A skill owned by the player. Can own damage modifiers and is autoadjustable. Can also own actions, which make it possible to attach
commands and attack to the skill.
'''
class Skill(DamageModifierOwner, Autoadjustable):
    def __init__(self, name, value, resists=None, weaks=None):
        DamageModifierOwner.__init__(self, name, resists, weaks)
        Autoadjustable.__init__(self, value)
        self.hasAutoAdjust = False
        self.actions = []
        
    def getDescription(self):
        desc = self.name.upper() + " is a skill you have. " + self.getAutoAdjustDescription() + self.getModifierDescription()
        if self.actions:
            desc = desc + "The skill gives you certain ABILITIES. "
            for x in self.actions:
                desc = desc + x.getActionDescription()
        return desc
        
    def addAction(self, action):
        action.name = self.name
        self.actions.append(action)

'''
A stat that can own damage modifiers and is autoadjustable. Should be a simple word and a numeric value.
''' 
class Stat(DamageModifierOwner, Autoadjustable):
    def __init__(self, name, value, resists=None, weaks=None):
        DamageModifierOwner.__init__(self, name, resists, weaks)
        Autoadjustable.__init__(self, value)
        self.hasAutoAdjust = False
        
    def getDescription(self):
        desc = self.name.upper() + " is a stat you have. " + self.getAutoAdjustDescription() + self.getModifierDescription()
        return desc

'''
Game variables. Should be usually invisible to the player. Used for mainly scripting. Can be local, which means they will be purged
when the player changes areas, or global, which means their scope includes all areas of the game.
'''
class Status(DamageModifierOwner, Autoadjustable):
    def __init__(self, name, value, local=False, visible=False, resists=None, weaks=None):
        DamageModifierOwner.__init__(self, name, resists, weaks)
        Autoadjustable.__init__(self, value)
        self.name = str(name)
        self.visible = visible
        self.local = local

'''
A modifier for taking damage. Can either increase (weakness) or decrease (resist) damage taken, possibly correlating with the value
of a DamageModifierOwner. Takes a type argument as string ('resist' or 'weakness'), a base attribute (the percentage of modification 
that will be done always), multiplier (1-5, bigger mulitplier means smaller strength in modifying), and a beneficial boolean.
Beneficial means a bigger DamageModifierOwner value correlates with less damage taken, non-beneficial means the opposite.
'''
class DamageModifier(object):
    
    TYPE_RESIST = 0
    TYPE_WEAKNESS = 1
    
    def __init__(self, type, dmgType, base, multiplier, beneficial):
        if "resist" in type:
            self.type = self.TYPE_RESIST
        else:
            self.type = self.TYPE_WEAKNESS
            
        self.dmgType = dmgType
            
        self.base = base
        self.multiplier = multiplier
        self.beneficial = beneficial
        
    def getDescription(self):
        desc = ""
        if self.type == self.TYPE_RESIST:
            if self.dmgType == "GLOBAL":
                if self.beneficial:
                    desc = desc + "It lowers all damage taken as the value increases."
                else:
                    desc = desc + "It lowers all damage taken as the value decreases."
            else:
                if self.beneficial:
                    desc = desc + "It lowers " + self.dmgType.upper() + " damage taken as the value increases."
                else:
                    desc = desc + "It lowers " + self.dmgType.upper() + " damage taken as the value decreases."
                    
        elif self.type == self.TYPE_WEAKNESS:
            if self.dmgType == "GLOBAL":
                if self.beneficial:
                    desc = desc + "It increases all damage taken as the value decreases."
                else:
                    desc = desc + "It increases all damage taken as the value increases."
            else:
                if self.beneficial:
                    desc = desc + "It increases " + self.dmgType.upper() + " damage taken as the value decreases."
                else:
                    desc = desc + "It increases " + self.dmgType.upper() + " damage taken as the value increases."
        return desc      
        
    def getType(self):
        if self.type == self.TYPE_RESIST:
            return "resist"
        else:
            return "weakness"

'''
Time class for the game time. Handles seconds, minutes, hours, and days. Counts days since begin point, and weekdays, but no month/year.
'''
class GlobalTime(object):
    def __init__(self):
        self.seconds = 20
        self.minutes = 4
        self.hours = 11
        self.day = 1
        self.weekday = "Tuesday"
        
    def getTotalMinutes(self):
        return self.minutes + 60 * (self.hours) + (1440 * (self.day - 1))
    
    def getTotalSeconds(self):
        return self.seconds + 60 * (self.minutes) + 3600 * self.hours + 86400 * (self.day - 1)
        
    def addSeconds(self, sAdd):
        sec = sAdd % 60
        min = (sAdd - sec) / 60
        if self.seconds + sec < 60:
            self.seconds = self.seconds + sec
            if min > 0:
                self.addMinutes(min)
        else:
            self.seconds = (self.seconds + sec) - 60
            min = min + 1
            self.addMinutes(min)
                
    def addMinutes(self, mAdd):
        min = mAdd % 60
        hr = (mAdd - min) / 60
        if self.minutes + min < 60:
            self.minutes = self.minutes + min
            if hr > 0:
                self.addHours(hr)
        else:
            self.minutes = (self.minutes + min) - 60
            hr = hr + 1
            self.addHours(hr)
            
    def addHours(self, hAdd):
        hr = hAdd % 24
        days = (hAdd - hr) / 24
        if self.hours + hr < 24:
            self.hours = self.hours + hr
            if days > 0:
                self.addDays(days)
        else:
            self.hours = (self.hours + hr) - 24
            days = days + 1
            self.addDays(days)
            
    def addDays(self, dAdd):
        self.day = self.day + dAdd
        wday = self.day % 7
        if wday == 1:
            self.weekday = "Tuesday"
        elif wday == 2:
            self.weekday = "Wednesday"
        elif wday == 3:
            self.weekday = "Thursday"
        elif wday == 4:
            self.weekday = "Friday"
        elif wday == 5:
            self.weekday = "Saturday"
        elif wday == 6:
            self.weekday = "Sunday"
        else:
            self.weekday = "Monday"

'''
A condition with a name and a value.
'''
class Condition(Autoadjustable):
    def __init__(self, name, value, visible):
        Autoadjustable.__init__(self, value)
        self.name = str(name)
        self.visible = visible
        
    def getConditionDescription(self):
        return "Its " + self.name.upper() + " attribute is about " + str(self.value) + ". "
        
'''
Implementation for owning Conditions and searching and returning them based on the name.
'''
class ConditionOwner(object):
    def __init__(self):
        self.conditions = dict()
    
    #TODO: refactor with dicts
    def getConditionWithName(self, name):
        if name in self.conditions:
            return self.conditions[name]
        else: return False
        
    def getConditionsDescription(self):
        if self.conditions:
            desc = ""
            for key, value in self.conditions.items():
                if value.visible == True:
                    desc = desc + value.getConditionDescription()
            return desc
        else: return ""
    
    def addCondition(self, condition):
        self.conditions[condition.name] = condition 


'''
An item with a name, size, description, and optional attributes including: equippable, throwable, consumable.
'''
class Item(ConditionOwner, UseCountable):
    def __init__(self, name, size, desc):
        ConditionOwner.__init__(self)
        UseCountable.__init__(self)
        self.name = str(name)
        self.size = size or 15
        self.equippable = False
        self.throwable = False
        self.consumable = False
        self.desc = desc
        
    def getDescription(self):
        return self.getItemDescription()
    
    def getItemDescription(self):
        desc = ""
        if self.desc == False:
            desc = "Not much to say. It's just a " + self.name.lower() + ". "
        else:
            desc = self.desc + " "
        
        things = []
        if self.equippable:
            things.append("equip")
        if self.throwable:
            things.append("throw")
        if self.consumable:
            things.append("eat")
            
        if things:
            if len(things) == 1:
                desc = desc + "You can probably try to " + things[0] + " it. "
            if len(things) == 2:
                desc = desc + "You can probably try to " + things[0] + " it, or " + things[1] + " it. "
            if len(things) == 3:
                desc = desc + "You can probably try to " + things[0] + ", " + things[1] + ", and " + things[2] + " it. "
            
        desc = desc + self.getConditionsDescription()
        
        return desc
        
    def setEquippable(self, type):
        self.equippable = True
        self.equipType = type
        
    def setThrowable(self, damage, throwDmgTypes):
        self.throwable = True
        self.throwDmg = damage
        self.throwDmgTypes = throwDmgTypes
            
    def setConsumable(self, healAmount, event):
        self.consumable = True
        self.consumeHealAmount = healAmount
        self.consumeEvent = event
            
    def isWeapon(self):
        return False

'''
An Item with an attack and one or more verbs to activate the attack.
'''
class Weapon(Item, AttackOwner):
    def __init__(self, name, size, desc, weaponDmg, time, verb):
        Item.__init__(self, name, size, desc)
        AttackOwner.__init__(self)
        self.setEquippable("weapon")
        self.weaponVerbs = [str(verb)]
        self.addAttack(weaponDmg, time)
        
    def addWeaponVerb(self, verb):
        self.weaponVerbs.append(str(verb))
        
    def setAmmoPerShot(self, amount):
        self.ammoPerShot = amount
        
    def needsAmmo(self):
        if self.ammoPerShot == False:
            return False
        else:
            return True
        
    def isWeapon(self):
        return True
    
    def giveRandomVerb(self):
        return random.choice(self.weaponVerbs)

'''
An activity for an Npc that will be launched periodically.
'''
class NpcActivity(RequirementOwner):
    def __init__(self, angry, interval, desc):
        RequirementOwner.__init__(self)
        self.needsToBeAngry = angry
        self.interval = interval
        self.desc = str(desc)
        self.event = False
        self.chance = 0
        self.launchedEvent = False
        self.lastInitiated = 0
        
    def setLaunchedEvent(self, event):
        self.launchedEvent = event
        
    def roll(self):
        return random.randint(0, 100) < self.chance

'''
A non-player character in the game world. Can be completely passive, angry by default, or angry only after attacked by player.
'''
class Npc(ConditionOwner):
    def __init__(self, name, desc, health, isMonster, corpse=None, onDeath=None):
        ConditionOwner.__init__(self)
        
        if isMonster:
            self.__monster__ = True
            self.angryOnAttack = True
            self.setAttack(10)
            self.addAttackDmgType("impact")
            self.angry = True
        else:
            self.__monster__ = False
            self.angryOnAttack = False
            self.angry = False
            
        self.hasAttack = False
        self.lastGrowl = 0
        self.growlInterval = 10
        self.consumable = False
        
        self.corpse = corpse
        
        self.onDeath = onDeath
        
        self.health = health
        self.activities = []
        
        self.name = name or self.randomizeName()
        
        if not desc:
            if isMonster:
                self.desc = "It is a horrifying monster. Not much else to say."
            else:
                self.desc = "Man who cares. It's just some " + self.name.lower() + " doing something that could not interest you whatsoever."
        else: self.desc = str(desc)
        
        self.__dead__ = False
        
    def generateCorpse(self):
        self.corpse = Item("Corpse of " + self.name, 30, "It's the corpse of " + self.name + ". It's kinda gross. You don't want to look at it.")
        
    def getGrowlDescription(self):
        return self.name.upper() + " growls menacingly!"
        
    def getDescription(self):
        return self.desc + " It has " + str(self.health) + " health left. " + self.getConditionsDescription()
        
    def addActivity(self, act):
        self.activities.append(act)
    
    #TODO: refactor this
    def randomizeName(self):
        mnames1 = ["Horrid", "Smelly", "The", "Vicious" , "Magnetic", "Thrice Blessed", "Space", "Fanatic", "Dark", "Evil", "Crazed", \
               "Jolly", "Weird", "Awesome", "Giant", "Tiny", "Nanohuge", "Non-Magnetic", "Ultimate", "French", "Fancy"]
        
        mnames2 = ["Man", "Hobo", "Villager", "Soldier", "Mafioso", "Italian Man", "Dog", "Woman", "Person", "Thing", "Cloud", "Alien", \
                   "Grapefarmer", "Car Mechanic", "Preacher", "Minion", "Imp", "Satan"]
        
        fnames1 = ["Kid", "Dude", "Guy", "Lady", "Stunning Dame", "Scientist", "Man", "Hobo", "Villager", "Soldier", "Mafioso", \
                  "Italian Man", "Car Mechanic", "Student"]
        
        if self.isMonster():
            num = random.randint(0, 100)
            if num > 90:
                name = mnames1.pop(random.randint(0, len(mnames1) - 1))
                name = name + " " + mnames1.pop(random.randint(0, len(mnames1) - 1))
                name = name + " " + mnames2.pop(random.randint(0, len(mnames2) - 1))
            elif num > 20:
                name = mnames1.pop(random.randint(0, len(mnames1) - 1))
                name = name + " " + mnames2.pop(random.randint(0, len(mnames2) - 1))
            else:
                name = mnames2.pop(random.randint(0, len(mnames2) - 1))
        else:
            num = random.randint(0, 100)
            if num > 80:
                name = mnames1.pop(random.randint(0, len(mnames1) - 1))
                name = name + " " + fnames1.pop(random.randint(0, len(fnames1) - 1))
            else:
                name = fnames1.pop(random.randint(0, len(fnames1) - 1))
            
        return name
    
    def isDead(self):
        return self.__dead__
    
    def die(self):
        self.__dead__ = True
    
    def takeDamage(self, amount):
        self.angry = True
        start = self.health
        self.health = self.health - amount
        if self.health <= 0:
            self.health = 0
            self.die()
        return start - self.health
                    
    def isMonster(self):
        return self.__monster__
        
    def setAttack(self, damage):
        self.hasAttack = True
        self.attackDmg = damage
        self.attackHits = 1
        self.attackInterval = 8
        self.attackTypes = False
        self.lastAttack = False
    
    def addAttackDmgType(self, type):
        if self.hasAttack:
            if not self.attackTypes:
                self.attackTypes = []
            self.attackTypes.append(type)
            
class Game(object):
    def __init__(self, playerName):
        
        self.saveLocation = False
        self.player = Player(playerName)
        self.lastLocationName = False
        self.currentLocationName = False
        self.currentLocation = False
        self.time = GlobalTime()
        self.globalStatus = []
        self.localStatus = []
        self.visited = dict()
        self.globalCommands = []
        self.areaCommands = []
        self.exitEvents = []
        self.exclusiveCommands = []
        self.quest = None
        self.lastAreaDescription = None
        
        self.initGameStartContent()
        
    def giveMemberWithPopularity(self, list, popularityNumber):
        tempList = list
        if len(tempList) > 1:
            tempList = sorted(tempList, key=lambda x: x.usecount, reverse=True)
        if popularityNumber > len(tempList):
            return tempList[len(tempList) - 1]
        else:
            return tempList[popularityNumber - 1]
        
    def removePlayerAttribute(self, list, member):
        if member not in self.initialStats:
            return self.player.removeAttribute(list, member)
        else:
            return False
        
    def initGameStartContent(self):
        for x in copy.deepcopy(control.INITCONTENT_STATS):
            self.player.gainStat(x)
        
        skills = copy.deepcopy(control.INITCONTENT_SKILLS)
        for i in range(0, control.INITCONTENT_AMOUNT_SKILLS): #number of initial skills
            if skills:
                num = random.randint(0, len(skills) - 1)
                self.player.gainSkill(skills[num])
                skills.pop(num)
        
        traits = copy.deepcopy(control.INITCONTENT_TRAITS)
        for i in range(0, control.INITCONTENT_AMOUNT_TRAITS): #number of initial traits
            if traits:
                num = random.randint(0, len(traits) - 1)
                self.player.gainTrait(traits[num])
                traits.pop(num)
        
        items = copy.deepcopy(control.INITCONTENT_ITEMS)
        for i in range(0, control.INITCONTENT_AMOUNT_ITEMS): #number of initial items
            if items:
                num = random.randint(0, len(items) - 1)
                self.player.gainItem(items[num])
                items.pop(num)
        
        self.globalCommands.append(copy.deepcopy(control.INITCONTENT_CMD_NAP))
    
    #TODO: ugh
    def __checkKey__(self, key):
        if type(key).__name__ == "Location":
            key = key.giveFormattedLoc()
        return key
        
    def addUsedSingularCommand(self, locationKey, commandName):
        locationKey = self.__checkKey__(locationKey)
        self.visited[locationKey].addUsedCommand(commandName)
        
    def addUsedSingularEvent(self, locationKey, eventName):
        self.visited[locationKey].addUsedEvent(eventName)
            
    def addVisitedArea(self, locationKey, visitedArea):
        locationKey = self.__checkKey__(locationKey)
        self.visited[locationKey] = visitedArea
            
    def checkSingularCommandUsed(self, locationKey, commandName):
        locationKey = self.__checkKey__(locationKey)
        return self.visited[locationKey].checkIfCommandUsed(commandName)
    
    def checkSingularEventUsed(self, locationKey, eventName):
        return self.visited[locationKey].checkIfEventUsed(eventName)
    
    def checkItemSpawnUsed(self, locationKey, spawnName):
        locationKey = self.__checkKey__(locationKey)
        return self.visited[locationKey].checkIfItemSpawnUsed(spawnName)
    
    def checkNpcSpawnUsed(self, locationKey, spawnName):
        locationKey = self.__checkKey__(locationKey)
        return self.visited[locationKey].checkIfNpcSpawnUsed(spawnName)
    
    def addUsedItemSpawn(self, locationKey, spawnName):
        locationKey = self.__checkKey__(locationKey)
        self.visited[locationKey].addUsedItemSpawn(spawnName)
        
    def addUsedNpcSpawn(self, locationKey, spawnName):
        locationKey = self.__checkKey__(locationKey)
        self.visited[locationKey].addUsedNpcSpawn(spawnName)
        
    def addAreaItem(self, locationKey, item, itemPos):
        locationKey = self.__checkKey__(locationKey)
        self.visited[locationKey].addItem(item, itemPos)
        
    def addAreaNpc(self, locationKey, item):
        locationKey = self.__checkKey__(locationKey)
        self.visited[locationKey].npcs.append(item)
        
def calculateResist(baseDmg, baseResist, value, multiplier, beneficial=True):
    if value == 0:
        return 0
    else:
        THRESHOLD = 0.8
        result = 0
        
        if multiplier == 1:
            multiplier = 1.5
        elif multiplier == 2:
            multiplier = 2.3
        elif multiplier == 3:
            multiplier = 3.5
        elif multiplier == 4:
            multiplier = 4.2
        else:
            multiplier = 5.0
        
        dmg = 0
        if beneficial: dmg = baseDmg * (100 - baseResist) * 0.01
        else: dmg = baseDmg
        
        result = math.pow(THRESHOLD, ((value / multiplier) * 0.1)) * dmg
        if not beneficial:
            result = baseDmg - result
            result = result * (100 - baseResist) * 0.01
            
        return round(result, 1)
    
def iterateDamageTypes(player, baseAmount, types):
    if types:
        #resist handling
        ownersWithResists = filter(lambda x: x.resists, player.skills + player.stats + player.traits)
        
        temp = []
        for type in types:
            for x in ownersWithResists:
                dmgTypeArray = [y.dmgType for y in x.resists]
                if (type in dmgTypeArray or "GLOBAL" in dmgTypeArray) and x not in temp:
                    temp.append(x)
        ownersWithResists = temp
        
        for owner in ownersWithResists:
            for resist in owner.resists:
                if resist.dmgType in types:
                    #print str(baseAmount), str(resist.base), str(owner.value), str(resist.multiplier), str(resist.beneficial)
                    baseAmount = calculateResist(baseAmount, resist.base, owner.value, resist.multiplier, resist.beneficial)
                    
    return baseAmount
        
class Player(object):
    def __init__(self, name):
        self.name = str(name)
        self.health = 100
        self.armor = 0
        self.exp = 10
        self.traits = []
        self.stats = []
        self.skills = []
        self.items = []
        self.weapons = []
        self.equippedWeapon = False
        self.equips = dict()
        self.punch = copy.deepcopy(control.WEAPON_PUNCH)
        self.kick = copy.deepcopy(control.WEAPON_KICK)
        self.bite = copy.deepcopy(control.WEAPON_BITE)
    
    #TODO: equipping generic items
    #def getEquippedItemsDescription(self):
        
        
    def equip(self, type, item):
        if type.lower() == "weapon":
            if item.isWeapon():
                self.equippedWeapon = item
                return True
            else:
                return False
        else:
            if type not in self.equips:
                self.equips[type] = item
                return True
            else:
                return False
    
    #TODO: unequipping is completely stupid right now.
    def unequipItemType(self, type):
        if type.lower() == "weapon":
            if self.equippedWeapon == False:
                return False
            else:
                self.equippedWeapon = False
                return True
        else:
            if type in self.equips:
                del self.equips[type]
                return True
            else:
                return False
            
    def unequipItemName(self, itemName):
        temp = False
        for key, equippedItem in self.equips.items():
            if equippedItem.name.lower() == itemName.lower():
                temp = key
                break
        
        if temp == False:
            return False
        else:
            del self.equips[temp]
            return True
        
    def damage(self, baseAmount, types):
        if types:
            baseAmount = iterateDamageTypes(self, baseAmount, types)

        #TODO: check for global resists and apply armor
        self.health = self.health - baseAmount
        if self.health <= 0:
            self.health = 0
            
        return baseAmount
        
    def heal(self, amount):
        #TODO: implement heal types
        if amount > 0:
            self.health = self.health + amount
            return amount
        else:
            return False
        
    def removeAttribute(self, list, member):
        if member in list:
            list.remove(member)
            return True
        else:
            return False
        
    def sortTraits(self):
        if len(self.traits) > 1:
            self.traits = sorted(self.traits, key=lambda trait: trait.name)
            
    def sortStats(self):
        if len(self.stats) > 1:
            self.stats = sorted(self.stats, key=lambda stat: stat.name)
            
    def sortSkills(self):
        if len(self.skills) > 1:
            self.skills = sorted(self.skills, key=lambda skill: skill.name)
            
    def sortItems(self):
        if len(self.items) > 1:
            self.items = sorted(self.items, key=lambda item: item.name)
                
    def giveMembersWithName(self, list, name):
        matches = filter(lambda x: x.name.lower() == name.lower(), list)
        if matches:
            return matches
        else:
            return False
    
    #TODO: add multiple instance handling (existValues)
    def gainTrait(self, trait):
        if self.giveMembersWithName(self.traits, trait.name) == False:
            self.traits.append(trait)
            self.sortTraits()
            return True
        else:
            return False
        
    def gainExp(self, exp):
        #TODO: exp gaining modifiers?
        self.exp = self.exp + exp
        return exp
    
    def gainStat(self, stat):          
        if self.giveMembersWithName(self.stats, stat.name) == False:
            self.stats.append(stat)
            self.sortStats()
            return True
        else:
            return False
        
    def gainSkill(self, skill):          
        if self.giveMembersWithName(self.skills, skill.name) == False:
            self.skills.append(skill)
            self.sortSkills()
            return True
        else:
            return False
        
    def gainItem(self, item):
        self.items.append(item)
        if item.isWeapon():
            self.weapons.append(item)
        self.sortItems()
        return True

