'''
Created on 25.10.2011

@author: Tarmo
'''

import re

class InvalidVerb(Exception):
    def __init__(self, verbUsed):
        self.verbUsed = verbUsed
        
class InvalidTarget(Exception):
    def __init__(self, targetUsed):
        self.targetUsed = targetUsed
        
class MalformedCommand(Exception):
    def __init__(self):
        pass
    
class InvalidWeapon(Exception):
    def __init__(self, weaponUsed):
        self.weaponUsed = weaponUsed
        
class InvalidPrefix(Exception):
    def __init__(self, cmdName, prefix):
        self.cmdName = cmdName
        self.prefix = prefix

'''
Validator for attack commands. Can parse the attack command, target, and specified weapon from a single string.
'''
class AttackValidator(object):
    def __init__(self, game):
        self.game = game

        self.verbs = False
        self.weaponNames = False
        self.npcNames = False
        self.customWeapons = False
        
    def setCustomWeapons(self, weaponList):
        self.customWeapons = weaponList
        
    def setDefaultWeapons(self):
        self.customWeapons = False
    
    def setVerbs(self, verbs):
        self.verbs = verbs
        self.verbs.append("attack") #attack is always a valid verb
        
    def setWeaponNames(self, weaponNames):
        self.weaponNames = weaponNames
        
    def setNpcNames(self, npcNames):
        self.npcNames = npcNames
    
    '''
    Returns the part of the asdasd
    '''
    def getCommandWithoutPrefix(self, cmdName, prefix):
        partitioner = "^(" + prefix + ")(.*)"
        match = re.match(partitioner, cmdName)
        if match != None:
            return match.group(2).strip()
        raise InvalidPrefix(cmdName, prefix)
    '''
    Returns a list of weapons that have a matching verb.
    '''
    def getWeaponsWithVerb(self, verb):
        if not self.customWeapons:
            return filter(lambda x: verb.lower() in x.weaponVerbs, self.game.player.weapons) + \
                   filter(lambda x: verb.lower() in x.verbs, sum([x.actions for x in self.game.player.skills], []))
        else:
            return filter(lambda x: verb.lower() in x.weaponVerbs, self.customWeapons)
    
    '''
    Returns a list of NPCs that have the matching name.
    '''
    def getTargetsWithName(self, name):
        area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        return filter(lambda x: name.lower() == x.name.lower(), area.npcs)
    
    '''
    Tries to validate the verb portion of the command. Returns a tuple with two members. The first one will be the verb used.
    Second member of the tuple is a boolean noting if the given command contains more information.. True if string has more information
    after the verb, False if string ends there. Raises InvalidVerbException if no suitable verb is found.
    '''
    def getAttackVerbInformation(self, cmdName):
        verbValidator = "^(" + "|".join(self.verbs) + ") (.*)"
        verbOnlyValidator = "^(" + "|".join(self.verbs) + ")$"
        match = re.match(verbOnlyValidator, cmdName)
        if match != None:
            verb = match.group(1)
            return verb, False
        else:
            match = re.match(verbValidator, cmdName)
            if match != None:
                verb = match.group(1)
                return verb, True
            else:
                raise InvalidVerb(cmdName)
    
    '''
    Tries to validate the target portion of the command. Returns a tuple with two members. First one will be the name of the target.
    Second member of the tuple is a boolean noting if the given command contains more information after the verb and the target.
    True if string contains more information, False if string ends there. Raises InvalidTargetException if no suitable target is found.
    '''
    def getTargetInformation(self, cmdName):
        targetValidator = "^(" + "|".join(self.npcNames) + ") .*"
        targetStopValidator = "^(" + "|".join(self.npcNames) + ")$"
        match = re.match(targetStopValidator, cmdName)
        if match != None:
            targetName = match.group(1)
            return targetName, False
        else:
            match = re.match(targetValidator, cmdName)
            if match != None:
                targetName = match.group(1)
                return targetName, True
            else:
                raise InvalidTarget(cmdName)
        
    '''
    Tries to validate the weapon part of the command. Returns name of the weapon, if it matches the name of a weapon in the 
    list given to the Validator. If it does not match, InvalidWeaponException will be raised. If the valid weapon was not 
    preceded by " with ", MalformedCommandException will be raised.
    '''
    def getWeaponInformation(self, cmdName):
        withValidator = "^(with )(.*)"
        weaponValidator = "^(with )(" + "|".join(self.weaponNames) + ")$"
        
        match = re.match(withValidator, cmdName)
        if match != None:
            match = re.match(weaponValidator, cmdName)
            if match != None:
                weaponName = match.group(2)
                return weaponName
            else:
                try:
                    withoutPrefix = self.getCommandWithoutPrefix(cmdName, "with ")
                    raise InvalidWeapon(withoutPrefix)
                except InvalidPrefix(cmdName, "with ") as ipe:
                    #print "Invalid prefix: No \"" + ipe.prefix + "\" in " + cmdName
                    raise InvalidWeapon(cmdName)
        else:
            raise MalformedCommand()

class CommandInterpreter(object):
    '''
    The main class for interpreting textual commands into actions in the game. Needs controller and game references.
    '''
    def __init__(self, controller, game):
        self.controller = controller
        self.game = game
        self.attackValidator = AttackValidator(game)
        
    def triggerCommand(self, command, outcome):
        if command.nextInSequence != False:
            command.nextInSequence.exclusive = True
            self.controller.addAreaCommand(command.nextInSequence)
            
        if self.game.exclusiveCommands and command.name == self.game.exclusiveCommands[0].name:
            self.game.exclusiveCommands.pop(0)
        
        self.controller.outcomeHandler.triggerOutcome(outcome)
                
    def __initiateCommand__(self, command):
        outcome, notice = command.getOutcome(self.controller)
        if outcome:
            if command.singular:
                try:
                    temp = command
                    self.game.areaCommands.remove(command)
                    self.game.addUsedSingularCommand(self.game.currentLocation, temp)
                except ValueError:
                    temp = command
                    self.game.globalCommands.remove(command)
                    self.game.addUsedSingularCommand(self.game.currentLocation, temp)
                self.controller.view.updateSideDisplay()
                
            self.triggerCommand(command, outcome)
        elif notice:
            self.controller.receiveDescription(notice)
        else:
            self.controller.displayLine("Can't do that, bro.")
            
    def __findTarget__(self, list, targetName):
        matches = filter(lambda x: x.name.lower() == targetName.lower(), list)
        if matches:
            return matches[0]
        else:
            return False
    
    def __findAnyNpc__(self, list):
        for i, x in enumerate(list):
            if x.isMonster() == True:
                return x, i
        #did not find monster, returning first npc
        return list[0], 0
    
    def __equippedItemAttackNpc__(self, npc):
        if self.game.player.equippedWeapon != False:
            self.__attackNpcWithWeapon__(npc, self.game.player.equippedWeapon, self.game.player.equippedWeapon.giveRandomVerb())
        else:
            self.__attackNpcWithWeapon__(npc, self.game.player.punch, self.game.player.punch.weaponVerbs[0])
            
    def __attackAnyNpcWithWeapon__(self, weapon, attackVerb):
        area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        
        if not area.npcs:
            self.controller.displayLine("There does not seem to be anything here to \"" + attackVerb + "\", as you put it.")
        else:
            self.__attackNpcWithWeapon__(self.__findAnyNpc__(area.npcs)[0], weapon, attackVerb)
    
    def __attackNpcWithWeapon__(self, npc, weapon, attackVerb):
        self.controller.advanceTime(weapon.attackTime)
        if self.game.player.health == 0:
            self.controller.killPlayer()
            self.controller.advanceTime(3800)
            return True
        if weapon.ammoPerShot != False:
            ammo = weapon.getConditionWithName("ammo")
            if ammo != False:
                ammoLeft = ammo.value - weapon.ammoPerShot
                if ammoLeft < 0: #value AFTER shooting!
                    self.controller.displayLine("Your " + weapon.name.upper() + " does not have enough ammo! Fuck!!")
                else:
                    ammo.value = ammoLeft
                    damageInflicted = npc.takeDamage(weapon.attackDmg)
                    self.controller.displayLine("You " + attackVerb + " the " + npc.name.upper() + " with your " + weapon.name.upper() + " causing " + str(damageInflicted) + " damage!")
                    self.controller.displayLine("Your " + weapon.name.upper() + " has " + str(ammo.value) + " ammo left.")
            else:
                self.controller.displayLine("Your " + weapon.name.upper() + " does not have ammo! Oh no!")
                    
        else:
            damageInflicted = npc.takeDamage(weapon.attackDmg)
            self.controller.displayLine("You " + attackVerb + " the " + npc.name.upper() + " with your " + weapon.name.upper() + " causing " + str(damageInflicted) + " damage!")
        self.__checkNpcDead__(npc)
        
    def __checkNpcDead__(self, npc):
        if npc.isDead():
            self.controller.displayLine(npc.name.upper() + " has been slain.")
            area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
            area.npcs.remove(npc)
            if npc.corpse:
                area.addItem(npc.corpse, False)
            if npc.onDeath:
                self.controller.receiveEvent(npc.onDeath)
        else:
            self.controller.displayLine(npc.name.upper() + " has " + str(npc.health) + " health left.")
        
    def getCorrectNounForm(self, word):
        list = ["A", "E", "Y", "U", "I", "O"]
        for x in list:
            if word.upper().startswith(x):
                return "an " + word
        return "a " + word
    
    def examineRoom(self):    
        area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        if not area.items and not area.npcs:
            self.controller.view.sendToMain("Looks like there is absolutely nothing else of importance here.")
        else:
            if area.items:
                for i in range(len(area.items)):
                    if area.items[i][1] == False:
                        self.controller.view.sendToMain("There is " + self.getCorrectNounForm(area.items[i][0].name.upper()) + " here.")
                    else:
                        self.controller.view.sendToMain("There is " + self.getCorrectNounForm(area.items[i][0].name.upper()) + " on the " + area.items[i][1] + ".")
            
            if area.npcs:
                for i in range(len(area.npcs)):
                    if area.npcs[i].angry:
                        self.controller.view.sendToMain("There is " + self.getCorrectNounForm(area.npcs[i].name.upper()) + " here. It is enraged by your presence!")
                    else:
                        self.controller.view.sendToMain("There is " + self.getCorrectNounForm(area.npcs[i].name.upper()) + " here.")
                    
        self.controller.view.sendEmptyLineMain()
            
    def __getStandardTargetName__(self, list):
        targetName = ""
        for i in range(1, len(list)):
            targetName = targetName + list[i] + " "
        targetName = targetName.strip().lower()
        return targetName
    
    def __equipItem__(self, words):
        if len(words) < 2:
            self.controller.displayLine("Equip what?")
        else:
            targetName = self.__getStandardTargetName__(words)
            
            temp = filter(lambda x: x.name.lower() == targetName.lower(), self.game.player.items)
            
            if temp:
                item = temp[0]
                if item.equippable:
                    self.game.player.equip(item.equipType, item)
                    if item.equipType == "weapon":
                        self.controller.displayLine("You now wield the " + item.name.upper() + "!")
                    else:
                        self.controller.displayLine("You put on the " + item.name.upper() + ".")
                else:
                    self.controller.displayLine("That doesn't even make any sense! Does " + item.name.upper() + " look equippable to you?")
            else:
                self.controller.displayLine("You don't seem to be carrying " + self.getCorrectNounForm(targetName.upper()) + ".")
                
    def __unequipItem__(self, words):
        if len(words) < 2:
            self.controller.displayLine("Unequip what?")
        else:
            targetName = self.__getStandardTargetName__(words)
            
            #print targetName
            #print self.game.player.equips.items()
            temp = filter(lambda x: x[1].name.lower() == targetName.lower(), self.game.player.equips.items())
            if self.game.player.equippedWeapon:
                temp.append(self.game.player.equippedWeapon)
            
            if temp:
                item = temp[0]
                self.game.player.unequipItemType(item.equipType)
                if item.equipType == "weapon":
                    self.controller.displayLine("You no longer wield the " + item.name.upper() + ".")
                else:
                    self.controller.displayLine("You take off the " + item.name.upper() + ".")
            else:
                self.controller.displayLine("You don't seem to have " + self.getCorrectNounForm(targetName.upper()) + " equipped.")
    
    def __determineTakeItem__(self, words):
        area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        
        if len(words) == 1:
            self.controller.displayLine("Take what?")
        else:
            targetName = self.__getStandardTargetName__(words)
            
            found = False
            for i, x in enumerate(area.items):
                if x[0].name.lower() == targetName.lower():
                    self.controller.newItem(area.items.pop(i)[0], False)
                    found = True
                    break
            if found == False:
                for i, x in enumerate(area.npcs):
                    if x.name.lower() == targetName.lower():
                        self.controller.displayLine(self.getCorrectNounForm(targetName).upper() + " is not something you can take and frankly that's a little bit inappropriate.")
                        found = True
                        break
                if found == False:
                    self.controller.displayLine("There does not seem to be " + self.getCorrectNounForm(targetName).upper() + " here.")
    
    def skillHasAttack(self, skill):
        for x in skill.actions:
            if x.hasAttack:
                return True
        return False
    
    def __checkStandardAttackCommand__(self, cmdName):
        #TODO: refactor so weapons aren't created every time
        area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        
        weapons = [self.game.player.punch, self.game.player.kick, self.game.player.bite]
        self.attackValidator.setCustomWeapons(weapons)
        self.attackValidator.setVerbs(["punch", "kick", "bite"])
        self.attackValidator.setWeaponNames(["fist", "leg", "mouth"])
        self.attackValidator.setNpcNames([x.name.lower() for x in area.npcs])
        
        success = self.__checkAttackCommand__(cmdName)
        self.attackValidator.setDefaultWeapons()
        return success
    
    def __checkCustomAttackCommand__(self, cmdName):
        area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        
        verbs = sum([x.weaponVerbs for x in self.game.player.weapons], [])
        verbs.extend(sum([x.verbs for x in sum([x.actions for x in self.game.player.skills], [])], []))
        self.attackValidator.setVerbs(verbs)
        weaponNames = [x.name.lower() for x in self.game.player.weapons]
        weaponNames.extend([y.name.lower() for y in filter(lambda x: self.skillHasAttack(x) == True, self.game.player.skills)])
        self.attackValidator.setWeaponNames(weaponNames)
        self.attackValidator.setNpcNames([x.name.lower() for x in area.npcs])
        
        return self.__checkAttackCommand__(cmdName)
    
    def __checkAttackCommand__(self, cmdName):
        cmdName = cmdName.strip()
        
        try:
            verb, moreInfo = self.attackValidator.getAttackVerbInformation(cmdName)
        except InvalidVerb:
            return False
        
        else:
            weapons = self.attackValidator.getWeaponsWithVerb(verb)
            if verb == "attack":
                area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        
                if not area.npcs:
                    self.controller.displayLine("There does not seem to be anything here to attack, you silly goober!")
                else:
                    self.__equippedItemAttackNpc__(self.__findAnyNpc__(area.npcs)[0])
                    
            elif moreInfo == False:
                self.__attackAnyNpcWithWeapon__(weapons[0], verb)
            else:
                
                try:
                    strippedCommand = self.attackValidator.getCommandWithoutPrefix(cmdName, verb)
                    targetName, moreInfo = self.attackValidator.getTargetInformation(strippedCommand)
                except InvalidTarget as ite:
                    self.controller.displayLine("Ain't no " + ite.targetUsed.upper() + " here, fool!")
                    
                else: 
                    npcs = self.attackValidator.getTargetsWithName(targetName)
                    if verb == "attack":
                        self.__equippedItemAttackNpc__(npcs[0])
                    elif moreInfo == False:
                        self.__attackNpcWithWeapon__(npcs[0], weapons[0], verb)
                    else:
                        
                        try:
                            prefix = verb + " " + targetName
                            strippedCommand = self.attackValidator.getCommandWithoutPrefix(cmdName, prefix)
                            weaponName = self.attackValidator.getWeaponInformation(strippedCommand)
                        except MalformedCommand:
                            self.controller.displayLine("Now you're not making any sense!")
                        except InvalidWeapon as iwe:
                            self.controller.displayLine("You don't have a weapon called " + iwe.weaponUsed.upper() + " that could " + verb + "!")
                            
                        else:
                            weapons = filter(lambda x: x.name.lower() == weaponName.lower(), weapons)
                            if not weapons:
                                self.controller.displayLine("You can't " + verb + " with your " + weaponName.upper() + ".")
                            else: 
                                self.__attackNpcWithWeapon__(npcs[0], weapons[0], verb)
            return True
        
    def examineName(self):
        self.controller.displayLine("Your name is " + self.game.player.name + ". Kind of a stupid name, but that's the one you chose.")
        
    def examineHealth(self):
        #TODO: implement different texts depending on health status
        self.controller.displayLine("You have about " + str(round(self.game.player.health, 1)) + " health left. You feel a bit dizzy.")
        
    def examineExperience(self):
        self.controller.displayLine("You have " + str(self.game.player.exp) + " experience. You don't know what that means. It's not like you're in some totally lame RPG.")
        
    def examineTime(self):
        #TODO: implement shit here
        self.controller.displayLine("You look a little to your right to check the time. Unfortunately you can't see the info screen since your presence is confined to the main screen.")
    
    def __checkCustomExamineCommand__(self, cmdName):
        area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        
        if cmdName == "examine room" or cmdName == "examine area":
            self.examineRoom()
        elif cmdName == "examine quest":
            self.controller.displayLine(self.game.quest.desc)
        elif cmdName == "examine location":
            self.controller.displayLine(self.game.currentLocation.getDescription())
        elif cmdName == "examine health":
            self.examineHealth()
        elif cmdName == "examine name":
            self.examineName()
        elif cmdName == "examine experience":
            self.examineExperience()
        elif cmdName == "examine time":
            self.examineTime()
        else:
        
            examinables = [self.game.player.punch, self.game.player.kick, self.game.player.bite]
            examinables.extend(area.npcs)
            examinables.extend(self.game.player.items)
            examinables.extend([x[0] for x in area.items])
            
            validNames = [x.name.lower() for x in examinables]
            validNames.extend(["trait " + x.name.lower() for x in self.game.player.traits])
            validNames.extend(["skill " + x.name.lower() for x in self.game.player.skills])
            validNames.extend(["stat " + x.name.lower() for x in self.game.player.stats])
            
            examineValidator = "^(examine) (" + "|".join(validNames) + ")$"
            
            if cmdName == "examine":
                self.controller.displayLine("Examine what exactly?")
            else:
                matchObj = re.match(examineValidator, cmdName)
                if matchObj != None:
                    targetName = str(matchObj.group(2))
                    
                    matchingTargets = filter(lambda x: targetName.lower() == x.name.lower(), examinables)
                    matchingTargets.extend(filter(lambda x: targetName.lower() == "trait " + x.name.lower(), self.game.player.traits))
                    matchingTargets.extend(filter(lambda x: targetName.lower() == "skill " + x.name.lower(), self.game.player.skills))
                    matchingTargets.extend(filter(lambda x: targetName.lower() == "stat " + x.name.lower(), self.game.player.stats))
                    
                    self.controller.displayLine(matchingTargets[0].getDescription())
                else:
                    self.controller.displayLine("It appears that there is no such thing in sight.")
    
    def __determineConsume__(self, list):
        area = self.game.visited[self.game.currentLocation.giveFormattedLoc()]
        
        if len(list) == 1:
            self.controller.displayLine(list[0].capitalize() + " what?")
        else:
            targetName = self.__getStandardTargetName__(list)
            
            found = False
            for i, x in enumerate(area.items):
                if x[0].name.lower() == targetName:
                    if x[0].consumable:
                        self.__consumeItem__(area.items.pop(i)[0])
                    else:
                        self.controller.displayLine("Can't eat that, bro!")
                    found = True
                    break
            if found == False:
                for i, x in enumerate(self.game.player.items):
                    if x.name.lower() == targetName:
                        if x.consumable:
                            self.__consumeItem__(self.game.player.items.pop(i))
                        else:
                            self.controller.displayLine("Can't eat that, bro!")
                        found = True
                        break
            
            if found == False:
                for i, x in enumerate(area.npcs):
                    if x.name.lower() == targetName.lower():
                        self.controller.displayLine(self.getCorrectNounForm(targetName).upper() + " is not something you can eat and frankly that's a little bit inappropriate.")
                        found = True
                        break
                if found == False:
                    self.controller.displayLine("There does not seem to be " + self.getCorrectNounForm(targetName).upper() + " here for you to gobble.")
    
    def __throw__(self, cmdList):
        self.controller.displayLine("Your feeble arms aren't suitable for throwing anything right now. You have a feeling this feature will be implemented later.")
    
    def __consumeItem__(self, item):
        mouthStrength = self.game.player.giveMembersWithName(self.game.player.stats, "Mouth power")[0].value
        if item.size >= mouthStrength:
            if item.consumeHealAmount > 0:
                self.controller.healPlayer(item.consumeHealAmount, item.name)
            if item.consumeEvent != False:
                self.controller.receiveEvent(item.consumeEvent)
            self.controller.view.updateSideDisplay()
        else:
            self.controller.displayLine("Your mouth simply isn't powerful enough.")
    
    def __checkReservedCommandMatch__(self, cmdName):
        cmdList = cmdName.split()
        
        if cmdName == "create error":
            raise Exception()
        
        if cmdList[0] == "examine":
            self.__checkCustomExamineCommand__(cmdName)
            return True
        
        if cmdList[0] == "take" or cmdList[0] == "grab":
            self.__determineTakeItem__(cmdList)
            return True
        
        if cmdList[0] == "equip" or cmdList[0] == "wear":
            self.__equipItem__(cmdList)
            return True
        
        if cmdList[0] == "unequip":
            self.__unequipItem__(cmdList)
            return True
        
        if cmdList[0] == "consume" or cmdList[0] == "eat":
            self.__determineConsume__(cmdList)
            return True
        
        if cmdList[0] == "throw":
            self.__throw__(cmdList)
            return True
        
        self.controller.view.suppressEmptyLines = True
        
        if self.__checkStandardAttackCommand__(cmdName) == True:
            self.controller.view.suppressEmptyLines = False
            return True
        
        if self.__checkCustomAttackCommand__(cmdName) == True:
            self.controller.view.suppressEmptyLines = False
            return True
        
        self.controller.view.suppressEmptyLines = False
        
        return False
    
    def printCommandNotFound(self, cmdName):
        self.controller.displayLine("You briefly consider if you should " + cmdName + ", but quickly abandon the notion as foolish.")
    
    def __checkCommandExclusivity__(self, command):
        if not self.game.exclusiveCommands or command.name == self.game.exclusiveCommands[0].name:
            return False
        else:
            return True
            
    def receiveCommand(self, cmdName):
        cmdName = str(cmdName)
        
        #TODO: more global commands such as interface ones?
        self.controller.view.sendEmptyLineMain()
        self.controller.displayCommandLine(">" + cmdName)
        
        #check areaCommands
        command = False
        for x in self.game.areaCommands:
            #print cmdName, type(cmdName).__name__, " - ", x.name, type(x.name).__name__
            if x.name == cmdName or cmdName.lower() in x.aliasList:
                command = x
        
        if command != False and self.__checkCommandExclusivity__(command) == False:
            self.__initiateCommand__(command)
            
        else:
            #check globalCommands
            command = False
            for x in self.game.globalCommands:
                if x.name == cmdName or cmdName.lower() in x.aliasList:
                    command = x
            if command != False and self.__checkCommandExclusivity__(command) == False:
                self.__initiateCommand__(command)
            
            elif self.__checkReservedCommandMatch__(cmdName) == False:
                self.printCommandNotFound(cmdName)
        
