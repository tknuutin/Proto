'''
Created on 7.7.2011

@author: Tarmo
'''

from lxml import etree
import os
import sys
import random
import requirements
import gameutil
import control

class Parser(object):
    def __init__(self, controller):
        self.controller = controller
        
    def parseNewItemSpawn(self, node):
        child = node.iterchildren().next()
        
        name = child.text.replace("\n", "")
        child = child.getnext()
        
        item = self.parseEmbeddedItemNode(child)
        child = child.getnext()
        
        msg = SpawnItemMessage(name, item)
        
        while child != None and child.tag == "spawn_req":
            req = self.reqParser.parseRequirement(child)
            
            if req.reqType == 0 or req.reqType == 3:
                msg.addSeeRequirement(req)
                msg.addSpawnRequirement(req)
            elif req.reqType == 1:
                msg.addSpawnRequirement(req)
            elif req.reqType == 2:
                msg.addSeeRequirement(req)
                
            child = child.getnext()
            
        if child != None and child.tag == "amount":
            msg.amount = int(child.text.replace("\n", ""))
            child = child.getnext()
        elif child != None and child.tag == "amount_lowerbound":
            min = int(child.text.replace("\n", ""))
            child = child.getnext()
            max = int(child.text.replace("\n", ""))
            msg.randomizeAmount(min, max)
            child = child.getnext()
            
        if child != None and child.tag == "position":
            msg.setItemPosition(child.text.replace("\n", ""))
            child = child.getnext()
        
        return msg
    
    def parseNewNpcSpawn(self, node):
        child = node.iterchildren().next()
        
        name = child.text.replace("\n", "")
        child = child.getnext()
        
        npc = self.controller.genParser.parseEmbeddedNpcNode(child)
        child = child.getnext()
        
        msg = SpawnNpcMessage(name, npc)
        
        while child != None and child.tag == "spawn_req":
            req = self.reqParser.parseRequirement(child)
            
            if req.reqType == 0 or req.reqType == 3:
                msg.addSeeRequirement(req)
                msg.addSpawnRequirement(req)
            elif req.reqType == 1:
                msg.addSpawnRequirement(req)
            elif req.reqType == 2:
                msg.addSeeRequirement(req)
                
            child = child.getnext()
            
        if child != None and child.tag == "amount":
            msg.amount = int(child.text.replace("\n", ""))
            child = child.getnext()
        elif child != None and child.tag == "amount_lowerbound":
            min = int(child.text.replace("\n", ""))
            child = child.getnext()
            max = int(child.text.replace("\n", ""))
            msg.randomizeAmount(min, max)
            child = child.getnext()
            
        return msg
        
    def parseTranseventNode(self, node):
        #TODO: implement event refs
        child = node.iterchildren().next()
        
        event = self.parseEmbeddedEventNode(child)
        event = event.toTransevent()
        
        child = child.getnext()
        
        if child != None and child.tag == "exclusive":
            event.setExclusive()
            child = child.getnext()
        
        while child != None and child.tag == "areaReq":
            event.addAreaRequirement(str(child.text.replace("\n", "")).lower())
            child = child.getnext()
            
        if child != None and child.tag == "chance":
            event.chance = int(child.text.replace("\n", ""))
            child = child.getnext()
            
        return event
        
    def parseEmbeddedEventNode(self, node):
        child = node.iterchildren().next()
        
        name = child.text.replace("\n", "")
        child = child.getnext()
        
        if child.tag == "dependency_list":
            #TODO: event dependency
            child = child.getnext()
        
        if child.tag == "keyword_list":
            #TODO: keywords
            child = child.getnext()
        
        singular = False
        if child.tag == "singular":
            singular = True
            child = child.getnext()
            
        defOutcome = self.parseOutcome(child)
        child = child.getnext()
        
        event = gameutil.Event(name, singular, defOutcome)
        
        while child != None and child.tag == "outcome":
            event.addOutcome(self.parseOutcome(child))
            child = child.getnext()
            
        return event
    
    def parseLocationNode(self, node):
        locTree = []
        exact = False
        child = node.iterchildren().next()
        
        if child.tag == "exact":
            exact = True
            child = child.getnext()
            
        locTree.append(child.text.replace("\n", ""))
        child = child.getnext()
        
        while child != None:
            locTree.append(child.text.replace("\n", ""))
            child = child.getnext()
            
        return gameutil.Location(locTree, exact)
    
    def parseDamageModifier(self, node):
        child = node.iterchildren().next()
        type = child.text.replace("\n", "")
        child = child.getnext()
        
        if child != None and child.tag == "resist_base":
            base = int(child.text.replace("\n", ""))
            mod = gameutil.DamageModifier("resist", type)
            mod.addModifierBase(base)
            return mod
        
        elif child != None and child.tag == "weakness_base":
            base = int(child.text.replace("\n", ""))
            mod = gameutil.DamageModifier("weakness", type)
            mod.addModifierBase(base)
            return mod
        
        elif child != None and child.tag == "correlation":
            child = child.iterchildren().next()
            
            isBiggerBetter = True
            #TODO: figure out what is going on here
            if child.text.replace("\n", "") == "false" or child.text.replace("\n", "") == "False":
                isBiggerBetter = False
            
            child = child.getnext()
            multiplier = int(child.text.replace("\n", ""))
            mod = gameutil.DamageModifier(type)
            mod.addCorrelation(isBiggerBetter, multiplier)
            
            return mod
        
        else:
            return False
    
    def parseItemCondition(self, node):
        child = node.iterchildren().next()
        
        name = child.text.replace("\n", "")
        child = child.getnext()
        
        #TODO: check this
        visible = node.get("visible", "false")
        if "false" in visible.lower():
            visible = False
        elif "true" in visible.lower():
            visible = True
        
        value = False
        if child != None and child.tag == "value":
            value = int(child.text.replace("\n", ""))
            child = child.getnext()
        elif child != None and child.tag == "value_min":
            min = int(child.text.replace("\n", ""))
            child = child.getnext()
            max = int(child.text.replace("\n", ""))
            value = random.randint(min, max)
            child = child.getnext()
            
        cond = gameutil.Condition(name, value, visible)
        
        if child != None and child.tag == "autoadjust":
            cond = self.parseAutoAdjust(child, cond)
        
        return cond
    
    def parseAutoAdjust(self, node, entity):
        child = node.iterchildren().next()
        
        mode = child.tag
        amount = int(child.text.replace("\n", ""))
        child = child.getnext()
        
        interval = 1
        if child.tag == "days":
            interval = 86400 * int(child.text.replace("\n", ""))
            child = child.getnext()
        elif child.tag == "minutes":
            interval = 60 * int(child.text.replace("\n", ""))
            child = child.getnext()
        else:
            interval = int(child.text.replace("\n", ""))
            child = child.getnext()
            
        threshold = int(child.text.replace("\n", ""))
        child = child.getnext()
        
        event = False
        if child != None and child.tag == "embeddedEvent":
            event = self.parseEmbeddedEventNode(child)
            child = child.getnext()
        
        elif child != None and child.tag == "launchedEvent":
            #TODO: parse external event
            pass
        
        entity.setAutoAdjust(mode, amount, interval, threshold, event)
        return entity
    
    def parseEmbeddedNpcNode(self, node):
        
        child = node.iterchildren().next()
        
        name = False
        desc = False
        if child != None and child.tag == "name":
            name = child.text.replace("\n", "")
            child = child.getnext()
            desc = child.text.replace("\n", "")
            child = child.getnext()
        
        ismonster = False
        aoa = False
        if child != None and child.tag == "monster":
            ismonster = True
            child = child.getnext()
        else:
            ismonster = False
            child = child.getnext()
            if child.tag == "angry_on_attack":
                aoa = True
                child = child.getnext()
                
        health = int(child.text.replace("\n", ""))
        child = child.getnext()
            
        npc = gameutil.Npc(name, desc, health, ismonster)
        npc.angryOnAttack = aoa
        
        if child != None and child.tag == "attack":
            achild = child.iterchildren().next()
            dmg = int(achild.text.replace("\n", ""))
            npc.setAttack(dmg)
            
            achild = achild.getnext()
            
            if achild.tag == "hits":
                npc.attackHits = int(achild.text.replace("\n", ""))
                achild = achild.getnext()
            
            if achild.tag == "hit_interval":
                npc.attackInterval = int(achild.text.replace("\n", ""))
                achild = achild.getnext()
                
            while achild != None and achild.tag == "damage_type":
                npc.addAttackDmgType(achild.text.replace("\n", ""))
                achild = achild.getnext()
            
            child = child.getnext()
        
        while child != None and child.tag == "activity":
            achild = child.iterchildren().next()
            
            angry = False
            if achild.tag == "angry":
                angry = True
                achild = achild.getnext()
                
            interval = int(achild.text.replace("\n", ""))
            achild = achild.getnext()
            
            desc = achild.text.replace("\n", "")
            achild = achild.getnext()
            
            act = gameutil.NpcActivity(angry, interval, desc)
            
            reqParser = requirements.ReqParser(self.controller)
            while achild != None and achild.tag == "requirement":
                act.addRequirement(reqParser.parseRequirement(achild))
                achild = achild.getnext()
            
            if achild != None and achild.tag == "launchedEvent":
                act.setLaunchedEvent(self.parseEmbeddedEventNode(child))
                achild = achild.getnext()
                
            if achild != None and achild.tag == "chance":
                act.chance = int(achild.text.replace("\n", ""))
            
            npc.addActivity(act)
            child = child.getnext()
        
        return npc
    
    def parseEmbeddedItemNode(self, node):
        child = node.iterchildren().next()
        
        name = child.text.replace("\n", "")
        child = child.getnext()
        
        size = False
        if child.tag == "size":
            size = int(child.text.replace("\n", ""))
            child = child.getnext()
            
        desc = False
        if child != None and child.tag == "description":
            desc = child.text.replace("\n", "")
            child = child.getnext()
        
        if child != None and child.tag == "weapon":
            wchild = child.iterchildren().next()
            dmg = int(wchild.text.replace("\n", ""))
            wchild = wchild.getnext()
            time = int(wchild.text.replace("\n", ""))
            wchild = wchild.getnext()
            
            verb = wchild.text.replace("\n", "")
            wchild = wchild.getnext()
            
            #TODO: this is dumb
            item = gameutil.Weapon(name, size, desc, dmg, time, verb)
            
            while wchild != None and wchild.tag == "verb":
                item.addWeaponVerb(wchild.text.replace("\n", ""))
                wchild = wchild.getnext()
            
            while wchild != None and wchild.tag == "type":
                item.addAttackType(wchild.text.replace("\n", ""))
                wchild = wchild.getnext()
                
            if wchild != None and wchild.tag == "ammo_per_shot":
                item.setAmmoPerShot(int(wchild.text.replace("\n", "")))
            
            child = child.getnext()
            
        else:
            item = gameutil.Item(name, size, desc)
        
        if child != None and child.tag == "equippable":
            type = child.text.replace("\n", "")
            item.setEquippable(type)
            child = child.getnext()
            
        if child != None and child.tag == "throwable":
            tchild = child.iterchildren().next()
            
            dmg = False
            if tchild != None and tchild.tag == "damage":
                dmg = int(tchild.text.replace("\n", ""))
                tchild = tchild.getnext()
                
            throwDmgTypes = ["impact"]
            while tchild != None and tchild.tag == "type":
                throwDmgTypes.append(tchild.text.replace("\n", ""))
                tchild = tchild.getnext()
                
            item.setThrowable(dmg, throwDmgTypes)
            child = child.getnext()
            
        if child != None and child.tag == "consumable":
            cchild = child.iterchildren().next()
            
            heal = False
            if cchild != None and cchild.tag == "health_healed":
                heal = int(cchild.text.replace("\n", ""))
                cchild = cchild.getnext()
            elif cchild != None and cchild.tag == "health_lost":
                heal = 0 - int(cchild.text.replace("\n", ""))
                cchild = cchild.getnext()
            
            consumeEvent = False
            if cchild != None and cchild.tag == "consume_effect":
                consumeEvent = self.parseEmbeddedEventNode(cchild)
                child = child.getnext()
            
            item.setConsumable(heal, consumeEvent)
            child = child.getnext()
        
        while child != None and child.tag == "condition":
            cond = self.parseItemCondition(child)
            child = child.getnext()
            item.addCondition(cond)
            
        return item

class OutcomeParser(Parser):
    def __init__(self, controller):
        Parser.__init__(self, controller)
        self.reqParser = requirements.ReqParser(controller)
    
    def parseOutcome(self, node):
        #print "parseOutcome tag: " + node.tag
        child = node.iterchildren().next()
        
        name = str(child.text.replace("\n", ""))
        child = child.getnext()
        
        reqs = []
        #parsing req
        while child.tag == "requirement":
            reqs.append(self.reqParser.parseRequirement(child))
            child = child.getnext()
        
        #parsing description
        desc = False
        if child != None and child.tag == "description":
            desc = self.controller.genParser.parseTextToObject(child)
            child = child.getnext()
        
        #parsing time
        time = int(child.text.replace("\n", ""))
        outcome = gameutil.Outcome(name, time)
        if desc != False:
            outcome.addDescription(desc)
        child = child.getnext()
        
        for x in reqs:
            outcome.addRequirement(x)
        
        #parsing take_damage
        if child != None and child.tag == "take_damage":
            outcome.addTakeDamageNode(self.controller.genParser.parseDamageElement(child))
            child = child.getnext()
            
        #parsing heal
        if child != None and child.tag == "heal":
            outcome.addHealNode(self.controller.genParser.parseHealElement(child))
            child = child.getnext()
            
        #parsing exp gained
        if child != None and child.tag == "gain_exp":
            outcome.expGained = int(child.text.replace("\n", ""))
            child = child.getnext()
            
        #parsing new node
        if child != None and child.tag == "new":
            outcome.addNewNode(self.controller.genParser.parseNewElement(child))
            child = child.getnext()
        
        #parsing modify node
        if child != None and child.tag == "modify":
            outcome.addModifyNode(self.controller.genParser.parseModifyElement(child))
            child = child.getnext()
            
        #parsing launch event node
        if child != None and child.tag == "launch_event":
            outcome.eventLaunched = child.text.replace("\n", "")
            child = child.getnext()
            
        #parsing moving nodes
        if child != None and child.tag == "move_to_area":
            outcome.move_to_area = child.text.replace("\n", "")
            child = child.getnext()
        
        return outcome         

def validate(schemaloc, xmlloc):
    schemaloc = str(schemaloc)
    xmlloc = str(xmlloc)
    if schemaloc == "" or os.path.isfile(schemaloc) == False:
        print("" + schemaloc + " doesn't exist or is unavailable.")
        return False
    else:
        if xmlloc == "" or os.path.isfile(xmlloc) == False:
            print("" + xmlloc + " doesn't exist or is unavailable.")
            return False
        else:
            schema = etree.XMLSchema(etree.parse(schemaloc))
            doc = etree.parse(xmlloc)
            
            if schema.validate(doc) == True:
                #print("" + xmlloc + " is valid according to " + schemaloc + "!")
                return True
            else:
                print("" + xmlloc + " is not valid according to " + schemaloc + "!")
                return False
            
class Message(object):
    def __init__(self, name):
        if name != False:
            self.name = str(name)
        else:
            self.name = False

class SpawnMessage(Message):
    TYPE_ITEM = 0
    TYPE_NPC = 1
    
    def __init__(self, name):
        Message.__init__(self, name)
        self.amount = 1
        self.spawnReqs = []
        self.seeReqs = []
        self.noticeText = None
        
    def randomizeAmount(self, min, max):
        self.amount = random.randint(min, max)
        
    def addSpawnRequirement(self, req):
        self.spawnReqs.append(req)
            
    def addSeeRequirement(self, req):
        self.seeReqs.append(req)

class SpawnNpcMessage(SpawnMessage):
    def __init__(self, name, npc):
        SpawnMessage.__init__(self, name)
        self.npc = npc
        self.type = self.TYPE_NPC
        self.spawnable = npc
        
class SpawnItemMessage(SpawnMessage):
    def __init__(self, name, item):
        SpawnMessage.__init__(self, name)
        self.item = item
        self.spawnable = item
        self.position = False
        self.type = self.TYPE_ITEM
        
    def setItemPosition(self, pos):
        self.position = pos

class AreaParser(OutcomeParser):
    def __init__(self, controller, areaLoc):
        OutcomeParser.__init__(self, controller)
        
        self.areaLoc = str(areaLoc)
        self.good = True
        
        if areaLoc == "" or os.path.isfile(areaLoc) == False:
            #print("File " + areaLoc + " doesn't exist or is unavailable.")
            self.doc = None
            self.good = False
        else:
            self.doc = etree.parse(str(areaLoc))
            self.good = True
        
    def checkDependency(self, node):
        for child in node.getchildren():
            if child.tag == "dependency":
                schemaloc = control.PATH_AREASCHEMA
                
                xmlloc = ""
                if control.OS_UNIX:
                    xmlloc = str(os.path.dirname(sys.argv[0])) + str(child.text.replace("\n", ""))
                else:
                    xmlloc = str(os.path.dirname(sys.argv[0])) + "/" + str(child.text.replace("\n", ""))
                
                if validate(schemaloc, xmlloc) != True:
                    self.controller.displayLine("You suddenly feel a great disturbance, as if something called " + xmlloc + " was missing or invalid!")
                    self.controller.displayLine("You feel you should probably stop playing and check your XML files.")
                    return False
        return True
        
    def parseIntoCurrentArea(self):
        
        node = self.doc.getroot().iterchildren().next()
        
        name = False
        if node != None and node.tag == "name":
            name = node.text.replace("\n", "")
        node = node.getnext()
        
        #parsing uniqueid
        node = node.getnext()
        
        if node != None and node.tag == "dependency_list":
            if self.checkDependency(node) != True:
                #print "checking dependency and failing the fuck out of dis!"
                return False
            node = node.getnext()
            
        #parsing keywords
        #TODO: parse keywords
        if node != None and node.tag == "keywordlist":
            node = node.getnext()
            
        #parsing hidelocation
        if node != None and node.tag == "hide_location":
            self.controller.hideLocation = True
            node = node.getnext()
            
        #parsing override locations
        #TODO: parse override
        if node != None and node.tag == "override":
            node = node.getnext()
        
        #parsing location
        #TODO: refactor setting loc name here
        if node != None and node.tag == "location":
            loc = self.parseLocationNode(node)
            loc.name = name
            self.controller.setCurrentLocation(loc)
            node = node.getnext()
            
        #parsing fasttravellable
        #TODO: fast travel
        if node != None and node.tag == "fastTravellable":
            node = node.getnext()
            
        enterEvents = []
        while node != None and node.tag == "enterEvent":
            enterEvents.append(self.parseTranseventNode(node))
            node = node.getnext()
        if enterEvents != False:
            self.controller.receiveTranseventList(enterEvents)
        
        #parsing description
        if node != None and node.tag == "area_description":
            child = node.iterchildren().next()
            #check if current location is found in visited. if not, send first_time description node. if so, send default one.
            firstDesc = False
            if child != None and child.tag == "first_time":
                firstDesc = self.controller.genParser.parseTextToObject(child)
                child = child.getnext()
            defDesc = self.controller.genParser.parseTextToObject(child)
            #depreaceated? self.controller.gameutil.currentLocation.addDescription(defDesc)
                
            if requirements.checkVisited(self.controller, self.controller.game.currentLocation) == False and firstDesc != False:
                self.controller.receiveDescription(firstDesc)
            else:
                self.controller.receiveDescription(defDesc)
                
            node = node.getnext()
        
        while node != None and node.tag == "movecommand":
            cmd = self.parseCommandNode(node)
            if not (cmd.singular == True and \
                    self.controller.game.checkSingularCommandUsed(self.controller.game.currentLocation, cmd.name) == True):
                self.controller.addAreaCommand(cmd)
            node = node.getnext()
            
        while node != None and node.tag == "command":
            cmd = self.parseCommandNode(node)
            if not (cmd.singular == True and \
                    self.controller.game.checkSingularCommandUsed(self.controller.game.currentLocation, cmd.name) == True):
                self.controller.addAreaCommand(cmd)
            node = node.getnext()
            
        while node != None and node.tag == "cmd_sequence":
            cmd = self.parseCommandSequence(node)
            
            stop = False
            while stop == False:
                if not self.controller.game.checkSingularCommandUsed(self.controller.game.currentLocation, cmd.name) == True:
                    self.controller.addAreaCommand(cmd)
                    stop = True
                elif cmd.nextInSequence != False:
                    cmd = cmd.nextInSequence
                else:
                    stop = True
                    
            node = node.getnext()
        
        if node != None and node != None and node.tag == "entities":
            child = node.iterchildren().next()
            
            while child != None and child.tag == "npc":
                self.parseNpcEntityNode(child)
                child = child.getnext()
            
            while child != None and child.tag == "item":
                self.parseItemEntityNode(child)
                child = child.getnext()
            
            node = node.getnext()
        
        while node != None and node.tag == "exitEvent":
            self.controller.addExitEvent(self.parseTranseventNode(node))
            node = node.getnext()
        
        return True
    
    def parseCommandSequence(self, node):
        child = node.iterchildren().next()
        
        exclusiveSequence = False
        if child != None and child.tag == "exclusive":
            exclusiveSequence = True
            child = child.getnext()
        
        firstCommand = self.parseCommandNode(child)
        firstCommand.singular = True
        if exclusiveSequence:
            firstCommand.exclusiveSequence = True
        child = child.getnext()
        
        cmd = self.parseCommandNode(child)
        cmd.singular = True
        if exclusiveSequence:
            cmd.exclusiveSequence = True
        firstCommand.nextInSequence = cmd
        child = child.getnext()
        
        while child != None and child.tag == "cmd":
            cmd2 = self.parseCommandNode(child)
            cmd2.singular = True
            if exclusiveSequence:
                cmd2.exclusiveSequence = True
            cmd.nextInSequence = cmd2
            cmd = cmd2
            child = child.getnext()
        
        return firstCommand
        
    def parseNpcEntityNode(self, node):
        self.controller.spawnAreaElement(self.parseNewNpcSpawn(node), quietMode=True, TYPE_ITEM=False, TYPE_NPC=True)
        
    def parseItemEntityNode(self, node):
        self.controller.spawnAreaElement(self.parseNewItemSpawn(node), quietMode=True, TYPE_ITEM=True, TYPE_NPC=False)
    
    def parseCommandNode(self, node):
        
        #parse name
        child = node.iterchildren().next()
        name = child.text.replace("\n", "")
        
        type = False
        singular = False
        randomized = False
        
        child = child.getnext()
        
        #parse alias
        alias = []
        while child != None and child.tag == "alias":
            alias.append(str(child.text.replace("\n", "")))
            child = child.getnext()
        
        #parse singular
        if child != None and child.tag == "singular":
            singular = True
            child = child.getnext()
        
        #parse type
        if node.tag == "movecommand":
            type = "move"
        else:
            type = child.text.replace("\n", "")
        child = child.getnext()
        
        cmd = gameutil.Command(name, type, singular, randomized)
        if alias != False:
            cmd.addAliasList(alias)
        
        #TODO: enum reqtypes?
        #parse requirements 
        while child != None and (child.tag == "list_requirement" or child.tag == "req_ref"):
            if child.tag == "list_requirement":
                req = self.reqParser.parseRequirement(child)
                cmd.addListRequirement(req)
                child = child.getnext()
            else:
                cmd.reqrefs.append(child.text.replace("\n", ""))
                child = child.getnext()
        
        #TODO: implement randomized outcomes
        if child != None and child.tag == "randomized_outcome":
            child = child.getnext()
        else:
            cmd.addOutcome(self.parseOutcome(child))
            child = child.getnext()
            while child != None and child.tag == "outcome":
                cmd.addOutcome(self.parseOutcome(child))
                child = child.getnext()
        
        return cmd

class ModifyMessage(Message):
    __modes__ = "add", "subtract", "multiply", "new_value"
    
    def __init__(self, name, type, popularityNumber):
        Message.__init__(self, name)
        self.randomMember = False
        self.popularityNumber = False
        if name == False and popularityNumber == False:
            self.randomMember = True
        elif name == False:
            self.popularityNumber = popularityNumber
        self.type = str(type).lower()
        self.message = False
        self.value = False
        self.percentage = False
        self.autoadjust = False
        self.fallback = False
        self.__mode__ = False
    
    #TODO: this is retarded. you are retarded. refactor this
    def setMode(self, modeStr):
        if self.__modes__[0] in modeStr:
            self.__mode__ = 0
        elif self.__modes__[1] in modeStr:
            self.__mode__ = 1
        elif self.__modes__[2] in modeStr:
            self.__mode__ = 2
        else:
            self.__mode__ = 3
    
    def setAutoAdjust(self, mode, amount, interval, threshold, event):
        self.autoadjust = True
        self.autoadjustMode = mode
        self.autoadjustAmount = amount
        self.autoadjustInterval = interval
        self.autoadjustThreshold = threshold
        self.autoadjustEvent = event
        
    def getMode(self):
        return self.__modes__[self.__mode__]
        
    def randomizeValue(self, min, max):
        self.value = random.randint(min, max)
        
class StatusModifyMessage(ModifyMessage):
    def __init__(self, name, modifyPopularNumber):
        ModifyMessage.__init__(self, name, "status", modifyPopularNumber)
        self.__vismode__ = False
        self.local = False
        
    def setVisible(self):
        self.__vismode__ = 1
    
    def setInvisible(self):
        self.__vismode__ = 2
    
    def setVisToggle(self):
        self.__vismode__ = 3
        
    def setNoVisChange(self):
        self.__vismode__ = False
        
    def getVisibilityMode(self):
        if self.__vismode__ == 1:
            return "set_visible"
        elif self.__vismode__ == 2:
            return "set_invisible"
        elif self.__vismode__ == 3:
            return "toggle"
        else:
            return False
        
class ItemModifyMessage(object):
    def __init__(self, name, modifyPopularNumber=False):
        if name != False:
            self.name = str(name)
        else:
            self.name = False
        if name == False:
            self.modifyPopularNumber = modifyPopularNumber
        self.type = "item"
        self.message = False
        self.lose = False
        self.drop = False
        self.conditions = []
        
    def addCondition(self, cond):
        self.conditions.append(cond)

class Instruction(object):
    def trigger(self, controller):
        pass

class TakeDamageInstruction(Instruction):
    def __init__(self, amount, reason, type):
        Instruction.__init__(self)
        self.amount = amount
        self.reason = reason
        self.type = type
        self.percentage = False
        
    def trigger(self, controller):
        if self.percentage:
            amount = controller.game.player.health * 0.01 * self.amount
        else:
            amount = self.amount
        controller.takeDamage(amount, self.reason, self.type)
        
class HealInstruction(Instruction):
    def __init__(self, amount, reason):
        Instruction.__init__(self)
        self.amount = amount
        self.reason = reason
        
    def trigger(self, controller):
        controller.healPlayer(self.amount, self.reason)
        
class NewElementInstruction(Instruction):
    def __init__(self):
        Instruction.__init__(self)
        self.newStats = []
        self.newTraits = []
        self.newSkills = []
        self.newStatus = []
        self.newItems = []
        self.newSpawn = []
        
    def addNewStat(self, stat, reason):
        self.newStats.append((stat, reason))
        
    def addNewTrait(self, trait, reason):
        self.newTraits.append((trait, reason))
        
    def addNewSkill(self, skill, reason):
        self.newSkills.append((skill, reason))
        
    def addNewStatus(self, status, reason):
        self.newStatus.append((status, reason))
        
    def addNewItem(self, item, reason):
        self.newItems.append((item, reason))
        
    def addNewSpawn(self, spawn):
        self.newSpawn.append(spawn)
        
    def trigger(self, controller):
        for x in self.newStats:
            controller.newStat(x[0], x[1])
        for x in self.newTraits:
            controller.newTrait(x[0], x[1])
        for x in self.newSkills:
            controller.newSkill(x[0], x[1])
        for x in self.newItems:
            controller.newItem(x[0], x[1])
        for x in self.newStatus:
            controller.newStatus(x[0], x[1])
        for x in self.newSpawn:
            if x.TYPE_ITEM:
                controller.spawnAreaElement(x, TYPE_ITEM=True)
            else:
                controller.spawnAreaElement(x, TYPE_ITEM=False)
        
class ModifyInstruction(Instruction):
    def __init__(self):
        Instruction.__init__(self)
        self.modifyStats = False
        self.modifyTraits = False
        self.modifySkills = False
        self.modifyStatus = False
        self.modifyItems = False
        self.modifySpawn = False
        self.modifyItem = False
        
    def addModifyStat(self, msgObj):
        if self.modifyStats == False:
            self.modifyStats = []
        self.modifyStats.append(msgObj)
        
    def addModifyTrait(self, traitName, message, popularityNumber):
        if self.modifyTraits == False:
            self.modifyTraits = []
        self.modifyTraits.append((traitName, message, popularityNumber))
        
    def addModifySkill(self, msgObj):
        if self.modifySkills == False:
            self.modifySkills = []
        self.modifySkills.append(msgObj)
        
    def addModifyStatus(self, msgObj):
        if self.modifyStatus == False:
            self.modifyStatus = []
        self.modifyStatus.append(msgObj)
        
    def addModifyItem(self, msgObj):
        if self.modifyItem == False:
            self.modifyItem = []
        self.modifyItem.append(msgObj)
        
    def trigger(self, controller):
        if self.modifyStats != False:
            for x in self.modifyStats:
                controller.modifyStat(x)
        if self.modifyTraits != False:
            for x in self.modifyTraits:
                controller.removeTrait(x)
        if self.modifySkills != False:
            for x in self.modifySkills:
                controller.modifySkill(x)
        if self.modifyItems != False:
            for x in self.modifyItems:
                controller.modifyItem(x)
        if self.modifyStatus != False:
            for x in self.modifyStatus:
                controller.modifyStatus(x)
        if self.modifySpawn != False:
            #TODO: implement
            pass

class GenericParser(Parser):
    def __init__(self, controller):
        Parser.__init__(self, controller)
        
    def parseTextToObject(self, node):
        child = node.iterchildren().next()
        desc = gameutil.DescriptionContainer()
        
        if child.tag == "single_line":
            child = child
            desc.addSingleLine(child.text.replace("\n", ""))
            
        elif child.tag == "p":
            stop = False
            
            while stop == False:
                pChild = child.iterchildren().next()
                pgraph = gameutil.DParagraphContainer(pChild.text.replace("\n", ""))
                
                pChild = pChild.getnext()
                
                while pChild != None:
                    nodename = pChild.tag
                    if nodename == "text" or nodename == "line":
                        pgraph.addElement(pChild.text.replace("\n", ""))
                    elif nodename == "new":
                        pgraph.addElement(self.parseNewElement(pChild))
                    elif nodename == "modify":
                        pgraph.addElement(self.parseModifyElement(pChild))
                    elif nodename == "take_damage":
                        pgraph.addElement(self.parseDamageElement(pChild))
                    elif nodename == "heal":
                        pgraph.addElement(self.parseHealElement(pChild))
                    pChild = pChild.getnext()
                
                desc.addParagraph(pgraph)          
                child = child.getnext()
                if child == None:
                    stop = True
         
        return desc

    def parseDamageElement(self, node):
        child = node.iterchildren().next()
        amount = 0
        reason = False
        type = []
        percentage = False
            
        if child != None:
            amount = int(child.text.replace("\n", ""))
            if child.tag == "percentage":
                percentage = True
            
        child = child.getnext()
        if child != None and child.tag == "reason":
            reason = child.text.replace("\n", "")
            child = child.getnext()
            
        while child != None:
            type.append(child.text.replace("\n", ""))
            child = child.getnext()
            
        tdi = TakeDamageInstruction(amount, reason, type)
        if percentage:
            tdi.percentage = True
                
        return tdi
        
    def parseHealElement(self, node):
        child = node.iterchildren().next()
        
        amount = 0
        reason = False
            
        if child != None and child.tag == "amount":                                # heal is a flat amount
            amount = int(child.text.replace("\n", ""))
        else:                                                           # heal is a percentage
            amount = int(child.text.replace("\n", "")) * 0.01 * self.player.health
            
        child = child.getnext()
        if child != None and child.tag == "reason":
            reason = child.text.replace("\n", "")
            child = child.getnext()
            
        return HealInstruction(amount, reason)
            
    def parseNewElement(self, node):
        child = node.iterchildren().next()
        
        element = NewElementInstruction()
        
        while child != None and child.tag == "trait":
            trait, reason = self.parseNewTrait(child)
            element.addNewTrait(trait, reason)
            child = child.getnext()
            
        while child != None and child.tag == "stat":
            stat, reason = self.parseNewStat(child)
            element.addNewStat(stat, reason)
            child = child.getnext()
            
        while child != None and child.tag == "skill":
            skill, reason = self.parseNewSkill(child)
            element.addNewSkill(skill, reason)
            child = child.getnext()
            
        while child != None and child.tag == "status":
            status, reason = self.parseNewStatus(child)
            element.addNewStatus(status, reason)
            child = child.getnext()
            
        while child != None and child.tag == "item":
            item, reason = self.parseNewItem(child)
            element.addNewItem(item, reason)
            child = child.getnext()
            
        while child != None and child.tag == "spawn":
            spawns = self.parseNewSpawn(node)
            for x in spawns: element.addNewSpawn(x)
            child = child.getnext()
            
        return element
    
    def parseNewSpawn(self, node):
        child = node.iterchildren().next()
        
        message = None
        if child.tag == "message":
            message = child.text.replace("\n", "")
            child = child.getnext()
        
        spawns = []
        while child.tag == "spawned_item":
            spawns.append(self.parseNewItemSpawn(child))
            child = child.getnext()
        
        while child.tag == "spawned_item":
            spawns.append(self.parseNewItemSpawn(child))
            child = child.getnext()
            
        return spawns
        
    def parseNewTrait(self, node):
        tChild = node.iterchildren().next()
        name = tChild.text.replace("\n", "")
        
        newTrait = gameutil.DamageModifierOwner(name, False, False)
        message = False
        
        tChild = tChild.getnext()
        
        if tChild != None and tChild.tag == "autoadjust":
            newTrait = self.parseAutoAdjust(tChild, newTrait)
            tChild = tChild.getnext()
        
        while tChild != None and tChild.tag == "addResist":
            resist = self.parseDamageModifier(tChild)
            newTrait.addResist(resist)
            tChild = tChild.getnext()
            
        while tChild != None and tChild.tag == "addWeakness":
            weakness = self.parseDamageModifier(tChild)
            newTrait.addWeakness(weakness)
            tChild = tChild.getnext()
            
        return newTrait, message
                        
    def parseNewStat(self, node):
        sChild = node.iterchildren().next()
        name = sChild.text.replace("\n", "")
        
        message = False
        value = 1
        
        sChild = sChild.getnext()
        
        if sChild != None and sChild.tag == "message":
            message = sChild.text.replace("\n", "")    
            sChild = sChild.getnext()
        
        if sChild != None and sChild.tag == "value":
            value = int(sChild.text.replace("\n", ""))
            sChild = sChild.getnext()
        elif sChild != None and sChild.tag == "value_min":
            minVal = int(sChild.text.replace("\n", ""))
            sChild = sChild.getnext()
            maxVal = int(sChild.text.replace("\n", ""))
            
            value = random.randint(minVal, maxVal)
            sChild = sChild.getnext()
            
        newStat = gameutil.Stat(name, value)
            
        if sChild != None and sChild.tag == "autoadjust":
            newStat = self.parseAutoAdjust(sChild, newStat)
            sChild = sChild.getnext()
        
        while sChild != None and sChild.tag == "addResist":
            resist = self.parseDamageModifier(sChild)
            newStat.addResist(resist)
            sChild = sChild.getnext()
            
        while sChild != None and sChild.tag == "addWeakness":
            weakness = self.parseDamageModifier(sChild)
            newStat.addWeakness(weakness)
            sChild = sChild.getnext()
            
        return newStat, message
    
    def parseAction(self, node):
        child = node.iterchildren().next()
        
        action = gameutil.Action(child.text.replace("\n", ""))
        child = child.getnext()
        
        while child != None and child.tag == "verb":
            action.addVerb(child.text.replace("\n", ""))
            child = child.getnext()
            
        if child != None and child.tag == "damage":
            dmg = int(child.text.replace("\n", ""))
            child = child.getnext()
            time = int(child.text.replace("\n", ""))
            
            action.addAttack(dmg, time)
            child = child.getnext()
            
            while child != None and child.tag == "type":
                action.addAttackType(child.text.replace("\n", ""))
                child = child.getnext()
        
        if child != None and child.tag == "action_event":
            action.setEvent(self.parseEmbeddedEventNode(node))
            child = child.getnext()
        
        return action
            
        
    def parseNewSkill(self, node):
        sChild = node.iterchildren().next()
        name = sChild.text.replace("\n", "")
        
        message = False
        value = 1
        
        sChild = sChild.getnext()
        
        if sChild != None and sChild.tag == "message":
            message = sChild.text.replace("\n", "")
            sChild = sChild.getnext()
        
        if sChild != None and sChild.tag == "value":
            value = int(sChild.text.replace("\n", ""))
            sChild = sChild.getnext()
        elif sChild != None and sChild.tag == "value_min":
            minVal = int(sChild.text.replace("\n", ""))
            sChild = sChild.getnext()
            maxVal = int(sChild.text.replace("\n", ""))
            
            value = random.randint(minVal, maxVal)
            sChild = sChild.getnext()
            
        newSkill = gameutil.Skill(name, value)
            
        if sChild != None and sChild.tag == "autoadjust":
            newSkill = self.parseAutoAdjust(sChild, newSkill)
            sChild = sChild.getnext()
        
        while sChild != None and sChild.tag == "addResist":
            resist = self.parseDamageModifier(sChild)
            newSkill.addResist(resist)
            sChild = sChild.getnext()
            
        while sChild != None and sChild.tag == "addWeakness":
            weakness = self.parseDamageModifier(sChild)
            newSkill.addWeakness(weakness)
            sChild = sChild.getnext()
            
        while sChild != None and sChild.tag == "addAction":
            newSkill.addAction(self.parseAction(sChild))
            sChild = sChild.getnext()
                
        return newSkill, message
        
    def parseNewStatus(self, node):
        sChild = node.iterchildren().next()
        name = sChild.text.replace("\n", "")
        
        value = False
        message = False
        
        sChild = sChild.getnext()
        
        if sChild != None and sChild.tag == "message":
            message = sChild.text.replace("\n", "")     
            sChild = sChild.getnext()
            
        local = False
        if sChild != None and sChild.tag == "local":
            local = True
            sChild = sChild.getnext()
            
        visible = False
        if sChild != None and sChild.tag == "visible":
            visible = True
            sChild = sChild.getnext()
        
        if sChild != None and sChild.tag == "value":
            value = int(sChild.text.replace("\n", ""))
            sChild = sChild.getnext()
        elif sChild != None and sChild.tag == "value_min":
            minVal = int(sChild.text.replace("\n", ""))
            sChild = sChild.getnext()
            maxVal = int(sChild.text.replace("\n", ""))
            
            value = random.randint(minVal, maxVal)
            sChild = sChild.getnext()
            
        newStatus = gameutil.Status(name, value, local, visible)
            
        if sChild:
            if sChild.tag == "autoadjust":
                newStatus = self.parseAutoAdjust(sChild, newStatus)
                sChild = sChild.getnext()
            
            if sChild:
                stop = False

                while stop == False:
                    if sChild.tag == "addResist":
                        resist = self.parseDamageModifier(sChild)
                        newStatus.addResist(resist)
                        sChild.getnext()
                    elif sChild.tag == "addWeakness":
                        weakness = self.parseDamageModifier(sChild)
                        newStatus.addWeakness(weakness)
                        sChild.getnext()
                    elif sChild != None == True:
                        stop = True
                    else:
                        stop = True
        
        return newStatus, message
        
    def parseNewItem(self, node):
        iChild = node.iterchildren().next()
        item = False
        
        if iChild != None and iChild.tag == "item_ref":
            #TODO: implement item ref parsing
            #print "item ref parsing not implemented yet"
            pass
        elif iChild != None and iChild.tag == "item_node":
            item = self.parseEmbeddedItemNode(iChild)
            
        iChild = iChild.getnext()
        
        message = False
        if iChild != None and iChild.nodeName == "message":
            message = iChild.text.replace("\n", "")
            self.controller.displayLine(message)
        
        return item, message
    
    def parseModifyElement(self, node):
        node = node.iterchildren().next()
        
        instruction = ModifyInstruction()
        
        if node != None:
            while node != None and node.tag == "remove_trait":
                traitName, message, popularityNumber = self.parseModifyTrait(node)
                instruction.addModifyTrait(traitName, message, popularityNumber)
                node = node.getnext()
                
            while node != None and node.tag == "stat":
                msg = self.parseModifyStat(node)
                instruction.addModifyStat(msg)
                node = node.getnext()
            
            while node != None and node.tag == "skill":
                msg = self.parseModifySkill(node)
                instruction.addModifySkill(msg)
                node = node.getnext()
                
            while node != None and node.tag == "status":
                msg = self.parseModifyStatus(node)
                instruction.addModifyStatus(msg)
                node = node.getnext()
                
            while node != None and node.tag == "item":
                msg = self.parseModifyItem(node)
                instruction.addModifyItem(msg)
                node = node.getnext()
                
            #TODO: add npc modifying
            
        return instruction
                    
    def parseModifyTrait(self, node):
        child = node.iterchildren().next()
        tName = False
        popularityNumber = False
        if child != None and child.tag == "trait_name":
            tName = child.text.replace("\n", "")
        elif child != None and child.tag == "popularity":
            popularityNumber = int(child.text.replace("\n", ""))
        elif child != None and child.tag == "random":
            pass
                
        child = child.getnext()
        message = False
                
        if child != None:
            if child.tag == "message":
                message = child.text.replace("\n", "")
                
        return tName, message, popularityNumber
        
    def parseModifyStat(self, node):
        modifymsg = self.__parseModifyStatSkill__(node)
        return modifymsg
        
    def parseModifySkill(self, node):
        modifymsg = self.__parseModifyStatSkill__(node)
        return modifymsg
        
    def __parseModifyStatSkill__(self, node):
        child = node.iterchildren().next()
        name = False
        popularityNumber = False
        if child != None and str(child.tag).find("name") > -1:
            name = child.text.replace("\n", "")
        elif child != None and child.tag == "popularity":
            popularityNumber = int(child.text.replace("\n", ""))
        elif child != None and child.tag == "random":
            #TODO: implement
            pass
        
        type = node.tag
            
        msgObj = ModifyMessage(name, type, popularityNumber)
        
        child = child.getnext()
                
        if child != None and child.tag == "message":
            msgObj.message = child.text.replace("\n", "")       
            child = child.getnext()
        
        if child != None and str(child.tag).find("random") > -1:
            min = int(child.iterchildren().next().text.replace("\n", ""))
            max = int(child.iterchildren().next().getnext().text.replace("\n", ""))
            msgObj.randomizeValue(min, max)
            
        else:
            msgObj.value = int(child.text.replace("\n", ""))
        
        msgObj.setMode(child.tag)
        child = child.getnext()
        
        if child != None and child.tag == "fallback":
            msgObj.fallback = int(child.text.replace("\n", ""))
            child = child.getnext()
            
        if child != None and child.tag == "percentage":
            msgObj.percentage = True
            child = child.getnext()
        
        if child != None and child.tag == "setAutoAdjust":
            self.parseAutoAdjust(child, msgObj)
        
        return msgObj
            
    def parseModifyStatus(self, node):
        child = node.iterchildren().next()
        name = False
        popularityNumber = False
        if str(child.tag).find("name") > -1:
            name = child.text.replace("\n", "")
        elif child != None and child.tag == "popularity":
            popularityNumber = int(child.text.replace("\n", ""))
                
        child = child.getnext()
        
        msgObj = StatusModifyMessage(name, popularityNumber)
                
        if child != None and child.tag == "message":
            msgObj.message = child.text.replace("\n", "")       
            child = child.getnext()
            
        if child != None and child.tag == "set_visible":
            msgObj.setVisible()
            child = child.getnext()
        elif child != None and child.tag == "set_invisible":
            msgObj.setInvisible()
            child = child.getnext()
        elif child != None and child.tag == "toggle":
            msgObj.setVisToggle()
            child = child.getnext()
        
        if child != None:
            if "_random" in child.tag:
                rchild = child.iterchildren().next()
                min = rchild.text.replace("\n", "")
                rchild = rchild.getnext()
                max = rchild.text.replace("\n", "")
                msgObj.randomizeValue(min, max)
            else:
                msgObj.value = int(child.text.replace("\n", "").replace("\n", ""))
        
        msgObj.setMode(child.tag)
        child = child.getnext()
        
        if child != None and child.tag == "fallback":
            msgObj.fallback = int(child.text.replace("\n", ""))
            child = child.getnext()
            
        if child != None and child.tag == "percentage":
            msgObj.percentage = True
            child = child.getnext()
        
        if child != None and child.tag == "setAutoAdjust":
            self.parseAutoAdjust(child, msgObj)
        
        return msgObj
    
    def parseModifyItem(self, node):
        child = node.iterchildren().next()
        name = child.text.replace("\n", "")
        
        child = child.getnext()
        
        msgObj = ItemModifyMessage(name)
                
        if child != None and child.tag == "message":
            msgObj.message = child.text.replace("\n", "")       
            child = child.getnext()
            
        while child != None and child.tag == "condition":
            cond = self.__parseModifyStatSkill__(child)
            msgObj.addCondition(cond)
            child = child.getnext()
            
        if child != None and child.tag == "lose":
            msgObj.lose = True
        elif child != None and child.tag == "drop":
            msgObj.drop = True
        
        print msgObj
        return msgObj
