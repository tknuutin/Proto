'''
Created on 3.7.2011

@author: Tarmo
'''

import sys, os, random, copy
import gameview
import gameutil
import parsers

from requirements import checkRequirement
from interpreter import CommandInterpreter

OS_UNIX = True
PATH_AREASCHEMA = str(os.path.dirname(sys.argv[0])) + "areaschema.xsd"
PATH_HOME_BEDROOM = str(os.path.dirname(sys.argv[0])) + "base/area_home_bedroom.xml"

from sys import platform as _platform
if _platform == "win32":
    OS_UNIX = False
    PATH_AREASCHEMA = str(os.path.dirname(sys.argv[0])) + "\\areaschema.xsd"
    PATH_HOME_BEDROOM = str(os.path.dirname(sys.argv[0])) + "\\base\\area_home_bedroom.xml"

WEAPON_PUNCH = gameutil.Weapon("punch", 10, "Your powerful fist.", 5, 5, "punch")
WEAPON_KICK = gameutil.Weapon("kick", 10, "Your powerful leg.", 7, 3, "kick")
WEAPON_BITE = gameutil.Weapon("bite", 10, "Your powerful mouth.", 15, 10, "bite")
    


AREA_NAME_BEDROOM = "Apartment building - Stairs - Home - Bedroom"

INITCONTENT_SKILLS = [gameutil.Skill("Spastic Twitching", 5), \
                      gameutil.Skill("Rolling with the punches", 3, resists=gameutil.DamageModifier("resist", "impact", 10, 3, True)), \
                      gameutil.Skill("Eating", 30), \
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

class MainController(object):
    def __init__(self):
        '''
        Constructor
        '''
        self.view = gameview.MainWindowView(self)
        self.genParser = parsers.GenericParser(self)
        self.game = False
        self.commandInterpreter = False
        self.timeHandler = False
        self.outcomeHandler = False
        self.entityHandler = False
    
    def execute(self):
        self.view.start()
        
        #print("Ending program.")
        
    def ready(self):
        self.view.sendToMain("Welcome to ModularGameAlpha!")
        self.view.sendEmptyLineMain()
        self.view.sendToMain("Press 'New Game' to start.")
        
    def newGame(self):
        #print ("New game!")
        playername = self.view.askName()
        if playername != False:
            self.view.clearMain()
            self.view.sendToMain("Your name is " + playername + ".")
            self.view.sendEmptyLineMain()
            self.view.setNameDisplay(playername)
            
            self.game = gameutil.Game(playername)
            self.commandInterpreter = CommandInterpreter(self, self.game)
            self.timeHandler = TimeHandler(self, self.game)
            self.outcomeHandler = OutcomeHandler(self, self.game)
            self.entityHandler = EntityHandler(self, self.game)
            
            self.view.updateInfoView()
            
            self.view.updateTraitWindow()
            self.view.updateStatWindow()
            self.view.updateSkillWindow()
            self.view.updateItemWindow()
            
            schemaloc = PATH_AREASCHEMA
            xmlloc = PATH_HOME_BEDROOM
            
            if parsers.validate(schemaloc, xmlloc) == True:
                self.newArea(xmlloc)
            else:
                self.view.showErrorDialog("There was an error validating XML. Check log for details.")
    
    def killPlayer(self):
        self.view.suppressEmptyLines = False
        self.game.player.health = 0
        desc = gameutil.DescriptionContainer()
        desc.addSingleLine("You have been slain!")
        self.receiveDescription(desc)
        self.view.sendEmptyLineMain()
        
        desc = gameutil.DescriptionContainer()
        desc.addSingleLine("You suddenly wake up in your bedroom. Seems like you blacked out there for a second. You have vague unsettling memories of pain and dying, but they are fading already.")
        self.receiveDescription(desc)
        
        if self.game.currentLocation.giveFormattedLoc() != AREA_NAME_BEDROOM: #do not reload if already in bedroom
            #TODO: refactor?
            areaLoc = PATH_HOME_BEDROOM
            
            parser = parsers.AreaParser(self, areaLoc)
            self.game.areaCommands = []
            if parser.good == True:
                self.game.localStatus = []
                parser.parseIntoCurrentArea()
            
        self.game.player.health = 100
        self.view.setHealthDisplay(str(self.game.player.health))
    
    def newArea(self, areaLoc):
        
        if self.game.exitEvents:
            self.receiveTranseventList(self.game.exitEvents)
        
        if self.game.currentLocation != False:
            
            key1 = str(self.game.currentLocation.giveFormattedLoc())
            self.game.visited[key1].incrementVisitCounter()
            
        self.hideLocation = False
        
        parser = parsers.AreaParser(self, areaLoc)
        self.game.areaCommands = []
        if parser.good == True:
            self.game.localStatus = []
            self.game.exitEvents = []
            
            self.game.lastLocationName = self.game.currentLocationName
            parser.parseIntoCurrentArea()
            
            #print monsters, set attackTimer
            area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
            
            if area.npcs:
                for x in area.npcs:
                    if x.angry:
                        self.view.sendToMain("There is " + self.commandInterpreter.getCorrectNounForm(x.name.upper()) + " here. It is enraged by your presence!")
                    
                    if x.hasAttack:
                        x.lastAttack = self.game.time.getTotalSeconds()
        
    def setCurrentLocation(self, loc):
        self.game.currentLocation = loc
        self.game.currentLocationName = str(loc.name)
        
        #try to access the VisitedArea object of the current location. if KeyError is thrown, add new visitedArea
        try:
            area = self.game.visited[loc.giveFormattedLoc()]
        except KeyError:
            area = gameutil.VisitedArea(loc.name, loc, self.game.time.getTotalMinutes())
            self.game.addVisitedArea(loc.giveFormattedLoc(), area)
        
        if self.hideLocation == False: 
            self.view.setLocation(loc.name)
        else:
            self.view.setLocation("???")
            
        area = self.game.visited[loc.giveFormattedLoc()]
    
    def spawnAreaElement(self, message, quietMode=False, TYPE_ITEM=False, TYPE_NPC=True): 
        self.entityHandler.spawnAreaElement(message, quietMode=quietMode, TYPE_ITEM=TYPE_ITEM, TYPE_NPC=TYPE_NPC)
                    
    def addExitEvent(self, event):
        self.game.exitEvents.append(event)
        
    def receiveTranseventList(self, eventList):
        exclusiveEvents = filter(lambda x: x.exclusive == True, eventList)
        
        if exclusiveEvents:
            eventList = [exclusiveEvents[0]]
                
        for x in eventList:
            chance = x.chance
            if chance == False:
                chance = 100
                
            if self.game.lastLocationName.lower() in x.areaReqs or not x.areaReqs:
                if random.randint(0, 100) <= chance:
                    self.receiveEvent(x)
                else:
                    pass
                    #print "Chance failed"
            else:
                pass
                #print "AreaReq failed. areareqs: " + str(x.areaReqs)
        
    def receiveEvent(self, event):
        outcome, notice = event.getOutcome(self)
        if outcome and self.game.checkSingularEventUsed(self.game.currentLocation.giveFormattedLoc(), event.name) == False:
            self.outcomeHandler.triggerOutcome(outcome)
            
            if event.singular == True:
                self.game.addUsedSingularEvent(self.game.currentLocation.giveFormattedLoc(), event.name)
                
        elif notice:
            self.receiveDescription(notice)
        
    def addAreaCommand(self, command):
        self.game.areaCommands.append(command)
            
        if command.exclusive == True:
            self.game.exclusiveCommands.append(command)
            
    def takeDamage(self, baseAmount, reason, type):
        amount = self.game.player.damage(baseAmount, type)
        if amount != False:
            if reason == False:
                text = "You take " + str(round(amount, 1)) + " damage!"
            else:
                text = reason + " hits you for " + str(round(amount, 1)) + " damage!"
            self.displayLine(text)
            self.view.sendEmptyLineMain()
            self.view.setHealthDisplay(str(round(self.game.player.health, 1)))
        if self.game.player.health <= 0.1:
            return False
        else:
            return True
            
    def healPlayer(self, amount, reason):
        amount = self.game.player.heal(amount)
        if amount != False:
            if reason == False:
                text = "You regenerate " + str(amount) + " health."
            else:
                text = reason + " regenerates " + str(amount) + " of your health!"
            self.displayLine(text)
            self.view.sendEmptyLineMain()
            self.view.setHealthDisplay(str(self.game.player.health))

    def newTrait(self, trait, message=None): self.entityHandler.newTrait(trait, message)
    def newStat(self, stat, message=None): self.entityHandler.newStat(stat, message)  
    def newSkill(self, skill, message=None): self.entityHandler.newSkill(skill, message) 
    def newItem(self, item, message=None): self.entityHandler.newItem(item, message)     
    def newStatus(self, status, message=None): self.entityHandler.newStatus(status, message)
    def removeTrait(self, name, message=None): self.entityHandler.removeTrait(name, message) 
    def modifyStatus(self, msg): self.entityHandler.modifyStatus(msg)
    def modifySkill(self, msg): self.entityHandler.modifySkill(msg)
    def modifyStat(self, msg): self.entityHandler.modifyStat(msg)
    def modifyItem(self, msg): self.entityHandler.modifyItem(msg)
    
    
    def receiveDescription(self, desc):
        if desc.hasParagraphs == False:
            self.view.sendToMain(desc.line)
            self.view.sendEmptyLineMain()
        else:
            for x in desc.pgraphs:
                self.view.sendToMain(x.firstLine)
                self.view.sendEmptyLineMain()
                
                if x.hasElements == True:
                    for element in x.elements: 
                        if type(element).__name__ == "str":         # element is str text
                            self.view.sendToMain(element)
                            self.view.sendEmptyLineMain()
                        else:
                            element.trigger(self)
                self.view.sendEmptyLineMain()
                
    def receiveAreaDescription(self, desc):
        self.game.lastAreaDescription = desc
        self.receiveDescription(desc)
              
    def receiveCommand(self, cmdName):
        self.commandInterpreter.receiveCommand(cmdName)
        
    def advanceTime(self, seconds):
        self.timeHandler.advanceTime(seconds)
        
    def displayCommandLine(self, line):
        self.view.sendCommandLineToMain(line)
        
    def displayLine(self, line):
        self.view.sendToMain(line)
        
    def loadGame(self, game):
        self.game = game
        self.commandInterpreter = CommandInterpreter(self, self.game)
        self.timeHandler = TimeHandler(self, self.game)
        self.outcomeHandler = OutcomeHandler(self, self.game)
        self.entityHandler = EntityHandler(self, self.game)
        
        self.receiveDescription(self.game.lastAreaDescription)
            
        self.view.updateInfoView()
            
    def launchOptions(self):
        pass
        #print ("Launching options not implemented yet!")
        
    def quitGame(self):
        pass
        #print ("Quitting game!")
        
    def launchHelp(self):
        pass
        #print ("Help not implemented yet!")
        
    def updateExp(self, value):
        self.view.sendToMain("Gained " + value + "exp!")
        self.game.player.exp = self.game.player.exp + value
        self.view.setExpDisplay(self.game.player.exp)

class Handler(object):
    def __init__(self, controller, game):
        self.controller = controller
        self.game = game

class EntityHandler(Handler):
    def __init__(self, controller, game):
        Handler.__init__(self, controller, game)
        
    def spawnAreaElement(self, message, quietMode=False, TYPE_ITEM=False, TYPE_NPC=True):
        areaKey = self.game.currentLocation.giveFormattedLoc()
        if not self.game.checkNpcSpawnUsed(areaKey, message.name):
            
            #if at least one requirement passes, or there are no reqs
            if not [req for req in message.spawnReqs if not checkRequirement(self.controller, req)]:
                
                self.game.addUsedNpcSpawn(areaKey, message.name)
                for i in range(0, message.amount):
                    if TYPE_ITEM:
                        self.game.addAreaItem(areaKey, copy.deepcopy(message.item), message.position)
                    else:
                        self.game.addAreaNpc(areaKey, copy.deepcopy(message.npc))
                        
                if not quietMode:
                    if message.noticeText: self.controller.displayLine(str(message.noticeText))
                    else:
                        if message.amount == 1:
                            self.controller.displayLine("A " + message.spawnable.name + " appears in the room!")
                        else:
                            self.controller.displayLine(str(message.amount) + " " + message.spawnable.name + " appear in the room!")
        
    def newTrait(self, trait, message):
        eventSuccess = self.game.player.gainTrait(trait)
        if eventSuccess != False:
            if message == False:
                text = "You gained the trait " + trait.name.upper() + "."
            else:
                text = message
            self.controller.displayLine(text)
            self.controller.view.updateTraitWindow()
            
    def newStat(self, stat, message=None):
        eventSuccess = self.game.player.gainStat(stat)
        if eventSuccess != False:
            if not message:
                text = "You gained the stat " + stat.name.upper() + "."
            else:
                text = message
            self.controller.displayLine(str(text))
            self.controller.view.updateStatWindow()
            
    def newSkill(self, skill, message=None):
        eventSuccess = self.game.player.gainSkill(skill)
        if eventSuccess != False:
            if not message:
                text = "You gained the skill " + skill.name.upper() + "."
            else:
                text = message
            self.controller.displayLine(text)
            self.controller.view.updateSkillWindow()
            
    def newItem(self, item, message=None):
        eventSuccess = self.game.player.gainItem(item)
        if eventSuccess != False:
            if not message:
                text = "You gained the item " + item.name.upper() + "."
            else:
                text = message
            self.controller.displayLine(text)
            self.controller.view.updateItemWindow()
            
    def newStatus(self, status, message=None):
        if status.local == False:
            self.game.globalStatus.append(status)
        else:
            self.game.localStatus.append(status)
        if message:
            self.controller.displayLine(message)
        
    def removeTrait(self, name, message):
        eventSuccess = self.game.removePlayerAttribute(self.game.player.traits, name)
        if eventSuccess == True:
            if message == False:
                text = "You have lost the trait " + name + "."
            else:
                text = message
            self.controller.displayLine(text)
            self.controller.view.updateTraitWindow()
    
    def findMemberFromMessage(self, msg, lst):
        member = False
        if msg.name == False and msg.popularityNumber == False:
            member = random.choice(lst)
        elif msg.name == False:
            member = self.game.giveMemberWithPopularity(lst, msg.popularityNumber)
        else:
            matchingMembers = self.game.player.giveMembersWithName(lst, msg.name)
            if matchingMembers != False:
                member = matchingMembers[0]
        return member
    
    def modifyMember(self, msg, lst, member, quietMode=False):
        memberType = type(member).__name__.lower()
        
        #if subtract and 100 percent, remove given member
        if msg.getMode() == "subtract" and msg.percentage == True and msg.value == 100:
            eventSuccess = self.game.player.removePlayerAttribute(lst, member)
            if eventSuccess == True:
                if msg.message == False and quietMode == False:
                    text = "You have lost the " + memberType + " " + msg.name.upper() + "."
                else:
                    text = msg.message
                if quietMode == False:
                    self.controller.displayLine(text)
        
        elif msg.getMode() == "add":
            val = member.value
            if msg.percentage == True:
                add = member.value * (1 - msg.value * 0.01)
            else:
                add = msg.value
            val = val + add
            member.value = val
            
            if msg.message == False:
                    text = "The " + memberType + " " + member.name.upper() + " is increased by a stunning " + str(add) + " units!"
            else:
                text = msg.message
            if quietMode == False:
                self.controller.displayLine(text)
            
        elif msg.getMode() == "subtract":
            val = member.value
            if msg.percentage == True:
                subtract = member.value * (1 - msg.value * 0.01)
            else:
                subtract = msg.value
            val = val - subtract
            member.value = val
            
            if msg.message == False:
                    text = "The " + memberType + " " + member.name.upper() + " is descreased by " + str(subtract) + " units."
            else:
                text = msg.message
            if quietMode == False:
                self.controller.displayLine(text)
        
        elif msg.getMode() == "multiply":
            val = member.value
            temp = val * msg.value
            member.value = temp
            
            if msg.message == False:
                    text = "The " + memberType + " " + member.name.upper() + " is increased by a stunning " + str(temp - val) + " units!"
            else:
                text = msg.message
            if quietMode == False:
                self.controller.displayLine(text)
            
        elif msg.getMode() == "new_value":
            member.value = msg.value
            
            if msg.message == False:
                    text = "The " + memberType + " " + member.name.upper() + " is now exactly " + str(msg.value) + ". Whoah!"
            else:
                text = msg.message
            if quietMode == False:
                self.controller.displayLine(text)
        
        member.incrementUseCount()
        self.controller.view.updateSideDisplay()
        
    def resolveFallBack(self, msg):
        if msg.fallback != False:
            if msg.type == "stat":
                self.newStat(gameutil.Stat(msg.name, msg.fallback))
            elif msg.type == "skill":
                self.newSkill(gameutil.Skill(msg.name, msg.fallback))
            elif msg.type == "status":
                self.newStatus(gameutil.Status(msg.name, msg.fallback))
        
    def modifyStatus(self, msg):
        slist = self.game.localStatus
        member = self.findMemberFromMessage(msg, slist)
        if member != False:
            self.modifyMember(msg, slist, self.findMemberFromMessage(msg, slist), quietMode=True)
        else:
            slist = self.game.globalStatus
            member = self.findMemberFromMessage(msg, slist)
            if member != False:
                self.modifyMember(msg, slist, self.findMemberFromMessage(msg, slist), quietMode=True)
            else:
                #print "resolving fallback"
                self.resolveFallBack(msg)
        #print member.name, str(member.value)
    
    def modifySkill(self, msg):
        skills = self.game.player.skills
        member = self.findMemberFromMessage(msg, skills)
        if member != False:
            self.modifyMember(msg, skills, member)
        else:
            self.resolveFallBack(msg)
        
    def modifyStat(self, msg):
        stats = self.game.player.stats
        member = self.findMemberFromMessage(msg, stats)
        if member != False:
            self.modifyMember(msg, stats, member)
        else:
            self.resolveFallBack(msg)
        
    def modifyItem(self, msg):
        items = self.game.player.items
        member = self.findMemberFromMessage(msg, items)
        if member:
            if msg.drop:
                self.game.removePlayerAttribute(self.game.player.items, member)
                area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
                area.items.append(member, False)
            elif msg.lose:
                self.game.removePlayerAttribute(self.game.player.items, member)
            else:
                for x in msg.conditions:
                    condition = self.findMemberFromMessage(x, member.conditions)
                    if condition:
                        self.modifyMember(x, member.conditions, x, quietMode=True)
            
            if msg.message:
                self.controller.displayLine(msg.message)
        
class OutcomeHandler(Handler):
    def __init__(self, controller, game):
        Handler.__init__(self, controller, game)
        
    def triggerOutcome(self, outcome):
        
        self.controller.advanceTime(outcome.time)
        if self.game.player.health <= 0.1:
            self.controller.killPlayer()
            
        else:
            if outcome.description != False:
                self.controller.receiveDescription(outcome.description)
            if outcome.damageNode != False:
                outcome.damageNode.trigger(self.controller)
            if outcome.healNode != False:
                outcome.healNode.trigger(self.controller)
            if outcome.expGained != False:
                num = self.game.player.gainExp(outcome.expGained)
                self.controller.displayLine("You gained " + str(num) + " experience!")
            if outcome.newNode != False:
                outcome.newNode.trigger(self.controller)
            if outcome.modifyNode != False:
                outcome.modifyNode.trigger(self.controller)
            if outcome.eventLaunched != False:
                eout = outcome.eventLaunched.getOutcome()
                if eout:
                    self.triggerOutcome(eout)
                
            self.controller.view.updateSideDisplay()
            
            #TODO: get location from somewhere better
            if outcome.move_to_area != False:      
                schemaloc = PATH_AREASCHEMA
                
                xmlloc = ""
                if OS_UNIX:
                    xmlloc = str(os.path.dirname(sys.argv[0])) + str(outcome.move_to_area)
                else:
                    xmlloc = str(os.path.dirname(sys.argv[0])) + "/" + str(outcome.move_to_area)
                
                if parsers.validate(schemaloc, xmlloc) == True:
                    self.controller.newArea(xmlloc)
                else:
                    self.controller.view.showErrorDialog("There was an error validating XML. Check log for details.")
        
        #TODO: refactor, checking this twice!
        if self.game.player.health <= 0.1:
            self.controller.killPlayer()
        
class TimeHandler(Handler):
    def __init__(self, controller, game):
        Handler.__init__(self, controller, game)
        
    def __handleNpcAttacks__(self, npc):
        if npc.angry and npc.hasAttack and (npc.lastAttack + npc.attackInterval) < self.game.time.getTotalSeconds():
            if npc.lastAttack == False:
                for i in range(0, npc.attackHits):
                    self.controller.takeDamage(npc.attackDmg, npc.name.upper(), npc.attackTypes)
            else:
                timedifference = self.game.time.getTotalSeconds() - npc.lastAttack
                playerAlive = True
                while timedifference > 0 and playerAlive:
                    for i in range(0, npc.attackHits):
                        playerAlive = self.controller.takeDamage(npc.attackDmg, npc.name.upper(), npc.attackTypes)
                    timedifference = timedifference - npc.attackInterval
            npc.lastAttack = self.game.time.getTotalSeconds()
            
    def __handleNpcActivites__(self, npc):
        time = self.game.time.getTotalSeconds()
        triggered = False
        for x in npc.activities:
            if not (npc.angry == False and x.needsToBeAngry == True) \
               and x.lastInitiated < (time - x.interval) \
               and x.checkRequirements(self)[0] == True \
               and x.roll() == True:
                triggered = True
                self.controller.displayLine(x.desc)
                if x.launchedEvent != False:
                    self.controller.receiveEvent(x.launchedEvent)
                x.lastInitiated = time
                
        if triggered == False \
           and npc.lastGrowl < (time - npc.growlInterval) \
           and npc.angry == True:
            self.controller.displayLine(npc.getGrowlDescription())
            npc.lastGrowl = time
            
    def checkAutoadjustThreshold(self, aa):
        if aa.autoadjustAdd or aa.autoadjustMultiply:
            if aa.value >= aa.autoadjustThreshold:
                aa.hasAutoadjust = False
                if aa.autoadjustEvent != False:
                    self.controller.receiveEvent(aa.autoadjustEvent)
        else:
            if aa.value <= aa.autoadjustThreshold:
                aa.hasAutoadjust = False
                if aa.autoadjustEvent != False:
                    self.controller.receiveEvent(aa.autoadjustEvent)
    
    def __autoadjustMembers__(self, members):
        currentTime = self.game.time.getTotalSeconds()
        removables = []
        for x in members:
            if x.hasAutoadjust == True:
                if x.lastAutoadjust == False:
                    x.lastAutoadjust = currentTime
                elif x.lastAutoadjust < (currentTime - x.autoadjustInterval):
                    
                    if x.autoadjustAdd:
                        x.value = x.value + x.autoadjustAmount
                    elif x.autoadjustSubtract:
                        x.value = x.value - x.autoadjustAmount
                    elif x.autoadjustMultiply:
                        x.value = x.value * x.autoadjustAmount
                    
                    x.lastAutoadjust = currentTime
                    self.checkAutoadjustThreshold(x)
                    if x.value <= 0:
                        removables.append(x)
                        
        #TODO: find a new place for this
        for x in removables:
            if type(x).__name__ == "Stat" or type(x).__name__ == "Skill":
                self.controller.displayLine("You have lost the " + type(x).__name__.lower() + " " + x.name.upper() + " as a result the value dropping too low!")
            members.remove(x)
    
    def __handleAutoadjusts__(self):
        area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        
        self.__autoadjustMembers__(self.game.localStatus)
        self.__autoadjustMembers__(self.game.globalStatus)
        self.__autoadjustMembers__(self.game.player.skills)
        self.__autoadjustMembers__(self.game.player.stats)
        for x in area.npcs:
            if x.conditions:
                self.__autoadjustMembers__([x[1] for x in x.conditions.items()])
        for x in area.items:
            if x[0].conditions:
                self.__autoadjustMembers__([x[1] for x in x[0].conditions.items()])
        for x in self.game.player.items:
            if x.conditions:
                self.__autoadjustMembers__([x[1] for x in x.conditions.items()])
                
        self.controller.view.updateSideDisplay()
            
    def advanceTime(self, seconds):
        self.game.time.addSeconds(seconds)
        
        area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        for x in area.npcs:
            self.__handleNpcAttacks__(x)
            self.__handleNpcActivites__(x)
        self.__handleAutoadjusts__()
        
        self.controller.view.setTimeDisplay(self.game.time.weekday, self.game.time.hours, self.game.time.minutes, self.game.time.seconds)
        
