'''
Created on 24.7.2011

@author: Tarmo
'''
import random
import parsers

class ReqParser(parsers.GenericParser):
    
    def __init__(self, controller):
        parsers.GenericParser.__init__(self, controller)
    
    def parseRequirement(self, node):
        child = node.iterchildren().next()
        type = node.get("type", "0")
        
        #parse requirement name. also checks if node really is req node
        if child.tag == "req_name":
            name = child.text
            child = child.getnext()
            
            reqc = ReqContainer(name, int(type))
            
            if child.tag == "failure_notice":
                reqc.addFailureNotice(self.parseTextToObject(child))
                child = child.getnext()
            
            if child.tag != "never":
                while child != None and child.tag == "location":
                    loc = self.parseLocationNode(child)
                    reqc.addLocationReq(loc)
                    child = child.getnext()
                    
                while child != None and child.tag == "visited":
                    loc = self.parseLocationNode(child)
                    reqc.addVisitedReq(loc)
                    child = child.getnext()
                    
                while child != None and child.tag == "not_visited":
                    loc = self.parseLocationNode(child)
                    reqc.addNotVisitedReq(loc)
                    child = child.getnext()
                    
                if child != None and child.tag == "exists":
                    reqc = self.parseExistReqs(child, reqc)
                    child = child.getnext()
                    
                if child != None and child.tag == "not_exists":
                    reqc = self.parseNotExistReqs(child, reqc)
                    child = child.getnext()
                    
                while child != None and child.tag == "comparison":
                    comp = self.parseComparison(child)
                    reqc.addComparison(comp)
                    child = child.getnext()
                    
                if child != None and child.tag == "experience":
                    reqc.addExpReq(int(child.text))
                    child = child.getnext()
                    
                if child != None and child.tag == "time":
                    timefrag = self.parseTimeNode(child)
                    if timefrag != False:  
                        reqc.addTimeReq(timefrag)
                    child = child.getnext()
                    
                while child != None and child.tag == "roll":
                    roll = self.parseRollNode(child)
                    reqc.addRollReq(roll)
                    child = child.getnext()
                    
                while child != None and child.tag == "other_req":
                    otherreq = self.parseRequirement(child)
                    reqc.addOtherReq(otherreq)
                    child = child.getnext()
                    
                while child != None and child.tag == "exception":
                    exception = self.parseRequirement(child)
                    reqc.addException(exception)
                    child = child.getnext()
                
                if child != None and child.tag == "resulting_outcome":
                    reqc.addOutcome(str(child.text))
            else:
                reqc.never = True
                
            return reqc
        
    def parseRollNode(self, node):
        child = node.iterchildren().next()
        
        #parsing name
        name = child.text
        child = child.getnext()
        
        #parsing base chance
        base = int(child.text)
        child = child.getnext()
        
        roll = Roll(name, base)
        
        #parsing value correlation
        if child.tag == "value_correlation":
            vchild = child.iterchildren().next()
            if vchild.tag == "stat_name":
                roll.addCorrelation("stat", vchild.tag)
            elif vchild.tag == "skill_name":
                roll.addCorrelation("skill", vchild.tag)
            elif vchild.tag == "status_name":
                roll.addCorrelation("status", vchild.tag)
                
            child = child.getnext()
        
        #parsing modifiers
        while child != None and child.tag == "modifier":
            child = child.iterchildren().next()
            
            req = False
            if child.tag == "requirement":
                req = self.parseRequirement(child)
                child = child.getnext()
                
            rollmod = False  
            if child.tag == "pos_effect":
                rollmod = RollModifier(int(child.text), True)
            else:
                rollmod = RollModifier(int(child.text), False)
            
            if req != False:
                rollmod.addReq(req)
                
            roll.addModifier(rollmod)
            
        return roll
    
    def parseTimeNode(self, node):
        
        child = node.iterchildren().next().iterchildren().next()
        timefrag = False
        
        if child == None:
            return False
        else:
            #parsing the first node of lowerbound
            ldays = 0
            lminutes = 0
            if child.tag == "gameday":
                ldays = int(child.text)
                child = child.getnext()
            
            if child.tag == "hour":
                lminutes = 60 * int(child.text)
                child = child.getnext()
                
            if child.tag == "minute":
                lminutes = lminutes + int(child.text)
            
        #parsing upperbound
        child = node.iterchildren().next().getnext()
        if child != None and child.iterchildren().next() != None:
            child = child.iterchildren().next()
            udays = 0
            uminutes = 0
            if child.tag == "gameday":
                udays = int(child.text)
                child = child.getnext()
            
            if child.tag == "hour":
                uminutes = 60 * int(child.text)
                child = child.getnext()
                
            if child.tag == "minute":
                uminutes = uminutes + int(child.text)
                
            timefrag = TimeReqFragment(lminutes, ldays, uminutes, udays)
            
        else:
            timefrag = TimeReqFragment(lminutes, ldays)
            
        return timefrag
        
    def parseComparison(self, node):
        child = node.iterchildren().next()
        
        #parsing first type
        firstname = child.text
        firsttype = False
        if child.tag == "stat_name":
            firsttype = "stat"
        elif child.tag == "skill_name":
            firsttype = "skill"
        elif child.tag == "status_name":
            type = "status"
        child = child.getnext()
        
        #parsing first_miss_false node. if exists, the first thing not existing will trigger a return as false
        firstMissFalse = False
        if child.tag == "first_miss_false":
            firstMissFalse = True
            child = child.getnext()
        
        #parsing second type
        secname = child.text
        sectype = False
        if child.tag == "stat_name":
            sectype = "stat"
        elif child.tag == "skill_name":
            sectype = "skill"
        elif child.tag == "status_name":
            type = "status"
        child = child.getnext()
        
        #parsing first_miss_false node. if exists, the first thing not existing will trigger a return as false
        secMissFalse = False
        if child != None and child.tag == "first_miss_false":
            secMissFalse = True
            child = child.getnext()
        
        comp = CompReqFragment(firsttype, firstname, sectype, secname)
        comp.firstMissFalse = firstMissFalse
        comp.secMissFalse = secMissFalse
        
        #parsing comparison mode
        if child != None and child.tag == "is_equal":
            comp.setIsEqual()
        else:
            if child != None and child.tag == "is_bigger":
                if child.getnext().tag == "or_equal":
                    comp.setIsBiggerOrEqual()
                else:
                    comp.setIsBigger()
            elif child.getnext().tag == "or_equal":
                comp.setIsSmallerOrEqual()
            else:
                comp.setIsSmaller()
        
        return comp
        
                
    def parseReqFragment(self, node):
        schild = node.iterchildren().next()
        
        #parsing name node
        name = schild.text
        schild = schild.getnext()
        
        type = False
        if node.tag == "status":
            type = "status"
        elif node.tag == "stat":
            type = "stat"
        elif node.tag == "skill":
            type = "skill"
        elif node.tag == "trait":
            type = "trait"
        
        frag = ReqFragment(name, type)
        
        #parsing value nodes. if absent assume only existence of thing is required
        if schild != None and schild.tag == "range":
            range = schild.text.split()
            frag.minValue = int(range[0])
            frag.maxValue = int(range[1])
            
        return frag
    
    def parseItemFragment(self, node):
        child = node.iterchildren().next()
        name = child.text
        frag = ItemReqFragment(name)
        
        child = child.getnext()
        if child != None:
            while child != None and child.tag == "item_condition":
                conChild = child.iterchildren().next()
                conName = conChild.text
                conChild = conChild.getnext()
                if conChild != None:
                    value = int(conChild.text)
                    frag.addCondition(conName, value)
                else:
                    frag.addCondition(conName, condValue=None)
                
                child = child.getnext()
        return frag
    
    def parseExistReqs(self, node, reqc):
        child = node.iterchildren().next()
        if child != None:
            while child != None and child.tag == "trait":
                frag = self.parseReqFragment(child)
                reqc.addExistTraitReq(frag)
                child = child.getnext()
                
            while child != None and child.tag == "stat":
                frag = self.parseReqFragment(child)
                reqc.addExistStatReq(frag)
                child = child.getnext()
                
            while child != None and child.tag == "skill":
                frag = self.parseReqFragment(child)
                reqc.addExistSkillReq(frag)
                child = child.getnext()
                
            while child != None and child.tag == "status":
                
                frag = self.parseReqFragment(child)
                reqc.addExistStatusReq(frag)
                child = child.getnext()
                
            while child != None and child.tag == "item":
                frag = self.parseItemFragment(child)
                reqc.addExistItemReq(frag)
                child = child.getnext()
            
            while child != None and child.tag == "keyword":
                reqc.addExistKeywordReq(child.text)
                child = child.getnext()
            return reqc
        
    def parseNotExistReqs(self, node, reqc):
        child = node.iterchildren().next()
        if child != None:
            while child != None and child.tag == "trait":
                frag = self.parseReqFragment(child)
                reqc.addNotTraitReq(frag)
                child = child.getnext()
                
            while child != None and child.tag == "stat":
                frag = self.parseReqFragment(child)
                if child.iterchildren().next() != None:
                    if child.iterchildren().next().tag == "max_value":
                        frag.maxValue = int(child.iterchildren().next().text)
                reqc.addNotStatReq(frag)
                child = child.getnext()
                
            while child != None and child.tag == "skill":
                frag = self.parseReqFragment(child)
                if child.iterchildren().next() != None:
                    if child.iterchildren().next().tag == "max_value":
                        frag.maxValue = int(child.iterchildren().next().text)
                reqc.addNotSkillReq(frag)
                child = child.getnext()
                
            while child != None and child.tag == "status":
                frag = self.parseReqFragment(child)
                if child.iterchildren().next() != None:
                    if child.iterchildren().next().tag == "max_value":
                        frag.maxValue = int(child.iterchildren().next().text)
                reqc.addNotStatusReq(frag)
                child = child.getnext()
                
            while child != None and child.tag == "item":
                frag = self.parseItemFragment(child)
                reqc.addNotItemReq(frag)
                child = child.getnext()
            
            while child != None and child.tag == "keyword":
                reqc.addNotKeywordReq(child.text)
                child = child.getnext()
            return reqc

class ReqFragment(object):
    def __init__(self, name, fragtype):
        if type(name).__name__ != "str":
            name = str(name)
        self.name = name
        self.type = fragtype

        self.minValue = None
        self.maxValue = None
        
class ItemReqFragment(object):
    def __init__(self, name):
        self.name = str(name)
        self.conditions = False
        self.conditionValues = False
        
    def addCondition(self, condName, condValue):
        if self.conditions == False:
            self.conditions = []
            self.conditionValues = []
        self.conditions.append(condName)
        if condValue == None:
            self.conditionValues.append(False)
        elif type(condValue).__name__ != "int":
            self.conditionValues.append(False)
        else:
            self.conditionValues.append(condValue)
            
class TimeReqFragment(object):
    def __init__(self, lboundMin, lboundDay, uboundMin, uboundDay):
        self.lboundMin = False
        if lboundMin != None:
            if type(lboundMin).__name__ == "int":
                self.lboundMin = lboundMin
                
        self.lboundDay = False
        if lboundDay != None:
            if type(lboundDay).__name__ == "int":
                self.lboundDay = lboundDay
                
        if self.lboundDay == False and self.lboundMin == False:
            self.lboundMin = 60
            
        self.uboundMin = False
        if uboundMin != None:
            if type(uboundMin).__name__ == "int":
                self.uboundMin = uboundMin
                
        self.uboundDay = False
        if uboundDay != None:
            if type(uboundDay).__name__ == "int":
                self.uboundDay = uboundDay
                
        if self.lboundMin > 1439:
            self.lboundMin = 1439
        if self.uboundMin > 1439:
            self.uboundMin = 1439
        
        self.lboundTotal = 0
        if lboundMin != False:
            self.lboundTotal = self.lboundMin
        if lboundDay != False:
            self.lboundTotal = self.lboundTotal + (self.lboundDay * 24 * 60)
        
        self.uboundTotal = 0
        if uboundMin != False:
            self.uboundTotal = self.uboundMin
        if uboundDay != False:
            self.uboundTotal = self.uboundTotal + (self.uboundDay * 24 * 60)
            
        if self.uboundTotal > 0:
            self.checkBoundValidity()
            
    def checkBoundValidity(self):
        if self.uboundTotal <= self.lboundTotal:
            self.uboundMin = False
            self.uboundDay = False
            self.uboundTotal = 0
            
class CompReqFragment(object):
    def __init__(self, firsttype, firstName, sectype, secName):
        self.firsttype = firsttype
        self.sectype = sectype
        self.first = firstName
        self.second = secName
        self.firstMissFalse = False
        self.secMissFalse = False
        self.__modes__ = "equal", "smaller_or_equal", "smaller", "bigger_or_equal", "bigger"
        self.__mode__ = 0;
        
    def setIsEqual(self):
        self.__mode__ = 0
        
    def setIsSmallerOrEqual(self):
        self.__mode__ = 1
    
    def setIsSmaller(self):
        self.__mode__ = 2
        
    def setIsBiggerOrEqual(self):
        self.__mode__ = 3
        
    def setIsBigger(self):
        self.__mode__ = 4
        
    def getMode(self):
        return self.__modes__[self.__mode__]

class RollModifier(object):
    def __init__(self, effect, isPositive):
        if type(effect).__name__ != "int" or effect < 1 or effect > 99:
            self.effect = 1
        else:
            self.effect = effect
        self.isPositive = isPositive
        self.reqs = False
        
    def addReq(self, req):
        if self.reqs == False:
            self.reqs = []
        self.reqs.append(req)

class Roll(object):
    def __init__(self, name, chance):
        if type(name).__name__ == "QString":
            name = str(name)
        self.name = name
        if type(chance).__name__ != "int" or chance < 1 or chance > 99:
            self.chance = 1
        else:
            self.chance = chance
        self.correlationType = False
        self.correlationName = False
        self.modifiers = False
        
    def addCorrelation(self, type, name):
        if type == "stat" or type == "skill" or type == "status" and type(name).__name__ == "str":
            self.correlationType = type
            self.correlationName = name
            
    def addModifier(self, mod):
        if type(mod).__name__ == "RollModifier":
            if self.modifiers == False:
                self.modifiers = []
            self.modifiers.append(mod)
            
class ReqContainer(object):
    def __init__(self, name, reqType):
        if type(name).__name__ == "QString":
            name = str(name)
        self.name = name
        self.reqType = reqType
        self.never = False
        self.locationReq = []
        self.visitedReq = []
        self.notVisitedReq = []
        self.existTrait = []
        self.existStat = []
        self.existSkill = []
        self.existStatus = []
        self.existItem = []
        self.existKeyword = []
        self.notTrait = []
        self.notStat = []
        self.notSkill = []
        self.notStatus = []
        self.notItem = []
        self.notKeyword = []
        self.comparison = []
        self.expReq = False
        self.timeReq = False
        self.rollReq = []
        self.failureNotice = False
        self.otherReqs = []
        self.exceptionList = []
        self.result = False
        self.numOfParts = 0
    
    def addLocationReq(self, loc): 
        self.locationReq.append(loc)
        self.numOfParts = self.numOfParts + 1
            
    def addVisitedReq(self, loc):
        self.visitedReq.append(loc)
        self.numOfParts = self.numOfParts + 1
            
    def addNotVisitedReq(self, loc):
        self.notVisitedReq.append(loc)
        self.numOfParts = self.numOfParts + 1
        
    def addExistTraitReq(self, rfrag):
        self.existTrait.append(rfrag)
        self.numOfParts = self.numOfParts + 1
            
    def addExistStatReq(self, rfrag):
        self.existStat.append(rfrag)
        self.numOfParts = self.numOfParts + 1
            
    def addExistSkillReq(self, rfrag):
        self.existSkill.append(rfrag)
        self.numOfParts = self.numOfParts + 1
            
    def addExistStatusReq(self, rfrag):
        self.existStatus.append(rfrag)
        self.numOfParts = self.numOfParts + 1
            
    def addExistItemReq(self, irfrag):
        self.existItem.append(irfrag)
        self.numOfParts = self.numOfParts + 1
            
    def addExistKeywordReq(self, kword):
        self.existKeyword.append(kword)
        self.numOfParts = self.numOfParts + 1
            
    def addNotTraitReq(self, rfrag):
        self.notTrait.append(rfrag)
        self.numOfParts = self.numOfParts + 1
            
    def addNotStatReq(self, rfrag):
        self.notStat.append(rfrag)
        self.numOfParts = self.numOfParts + 1
            
    def addNotSkillReq(self, rfrag):
        self.notSkill.append(rfrag)
        self.numOfParts = self.numOfParts + 1
            
    def addNotStatusReq(self, rfrag):
        self.notStatus.append(rfrag)
        self.numOfParts = self.numOfParts + 1
            
    def addNotItemReq(self, irfrag):
        self.notItem.append(irfrag)
        self.numOfParts = self.numOfParts + 1
            
    def addNotKeywordReq(self, kword):
        self.notKeyword.append(kword)
        self.numOfParts = self.numOfParts + 1
            
    def addComparison(self, comp):
        self.comparison.append(comp)
        self.numOfParts = self.numOfParts + 1
            
    def addExpReq(self, minExp):
        self.expReq = minExp
        self.numOfParts = self.numOfParts + 1
            
    def addTimeReq(self, trfrag):
        self.timeReq = trfrag
        self.numOfParts = self.numOfParts + 1
            
    def addRollReq(self, roll):
        self.rollReq.append(roll)
        self.numOfParts = self.numOfParts + 1
            
    def addFailureNotice(self, notice):
        self.failureNotice = notice
            
    def addOtherReq(self, req):
        self.otherReqs.append(req)
        self.numOfParts = self.numOfParts + 1
    
    def addException(self, req):
        self.exceptionList.append(req)
            
    def addOutcome(self, outcomeName):
        self.result = str(outcomeName)

def checkLocation(controller, locationReq):
    #check if given requirement location is the same or child location of current game location
    if type(locationReq).__name__ == "Location":
        if locationReq.isChildLocation(controller.game.currentLocation) == False:
            return False
    elif type(locationReq).__name__ == "list":
        #iterate through the list of location reqs (treat as OR) and see if any are child locations of currentlocation
        found = False
        for x in locationReq:
            if locationReq.isChildLocation(controller.game.currentLocation) == True:
                found = True
        if found == False:
            return False
    return True

def checkVisited(controller, visitedReq):
    #check if the visitedArea object has visitcount larger than 0
    if type(visitedReq).__name__ == "Location":
        try:
            area = controller.game.visited[visitedReq.giveFormattedLoc()]
        except KeyError:
            return False
        #print "area: " + area.name + ", " + str(area.visitCount)
        if area.visitCount > 0:
            return True
        else:
            return False
    elif type(visitedReq).__name__ == "list":
        for x in visitedReq:
            try:
                area = controller.game.visited[x.giveFormattedLoc()]
            except KeyError:
                return False
            if area.visitCount > 0:
                return True
            else:
                return False
    return True

def checkNotExist(notExistReq, attributeContainer):
    for x in notExistReq:
        found = False
        for attr in attributeContainer:
            if attr.name.lower() == x.name.lower():
                if x.minValue and x.maxValue:
                    if attr.value < x.minValue or attr.value > x.maxValue:
                        #attribute found but it is NOT within range, continue to next attribute
                        break
                    else:
                        #attribute found and IS within range!
                        found = True
                else:
                    #attribute found!
                    found = True
            #attribute did not match, continue to next attribute
        if found: return False
    return True

def checkExist(existReq, attributeContainer):
    for x in existReq:
        found = False
        for attr in attributeContainer:
            if attr.name.lower() == x.name.lower():
                if x.minValue and x.maxValue:
                    if attr.value >= x.minValue and attr.value <= x.maxValue:
                        #attribute and is in range, continue to next attribute
                        found = True
                        break
                else:
                    #attribute found, continue to next attribute
                    found = True
                    break
        if not found: return False
    return True

def checkExistItem(itemreq, controller):
    #check if all attributes exist
    for x in itemreq:
        found = False
        for y in controller.game.player.items:
            if y.name.lower() == x.name.lower():
                found = True
        if found == False:
            return False
    return True

def __checkComparison__(controller, compReq):
    firstList = False
    if compReq.firsttype == "stat":
        firstList = controller.game.player.stats
    elif compReq.firsttype == "skill":
        firstList = controller.game.player.skills
    elif compReq.firsttype == "status":
        firstList = []
        firstList.extend(controller.game.localStatus)
        firstList.extend(controller.game.globalStatus)
    
    #if first attribute is not found, will return false if firstMissFalse is true will return true.
    firstFound = False
    firstValue = False
    for x in firstList:
        if x.name == compReq.firstName:
            firstFound = True
            firstValue = x.value
    if firstFound == False:
        if compReq.firstMissFalse == True:
            return False
        
    seclist = False
    if compReq.sectype == "stat":
        seclist = controller.game.player.stats
    elif compReq.sectype == "skill":
        seclist = controller.game.player.skills
    elif compReq.sectype == "status":
        seclist = []
        seclist.extend(controller.game.localStatus)
        seclist.extend(controller.game.globalStatus)
    
    #if first attribute is not found, will return false if firstMissFalse is true will return true.
    secFound = False
    secValue = False
    for x in seclist:
        if x.name == compReq.secName:
            secFound = True
            secValue = x.value
    if secFound == False:
        if compReq.secMissFalse == True:
            return False
        elif firstFound == False:
            return True
    
    if firstFound == True and secFound == True:
        if compReq.getMode() == "equal":
            if firstValue == secValue:
                return True
            else: return False
        if compReq.getMode() == "bigger":
            if firstValue > secValue:
                return True
            else: return False
        if compReq.getMode() == "bigger_or_equal":
            if firstValue >= secValue:
                return True
            else: return False
        if compReq.getMode() == "smaller":
            if firstValue < secValue:
                return True
            else: return False
        if compReq.getMode() == "smaller_or_equal":
            if firstValue <= secValue:
                return True
            else: return False

def checkComparisonRequirement(controller, compReq):
    for x in compReq:
        if __checkComparison__(controller, x) == False:
            return False
    #if we make it here, all comparisons in list are true
    return True
    
def checkRollRequirement(controller, roll):
    #TODO: add correlation calculations
    for r in roll:
        chance = r.chance
        
        if r.modifiers != False:
            #check all modifiers
            for x in r.modifiers:
                
                reqsPassed = True
                if x.reqs != False:
                    #check all reqs
                    for y in x.reqs:
                        if checkRequirement(controller, y) == False:
                            reqsPassed = False
            
                if reqsPassed == True:
                    if x.isPositive == True:
                        chance = chance * (100 + x.effect * 0.01)
                    else:
                        chance = chance * (100 - x.effect * 0.01)
                        
            if chance < 1:
                chance = 1
            elif chance > 99:
                chance = 99
            
            chance = int(chance)
            
        num = random.randint(0, 100)
        if num < chance:
            return True
        else:
            return False
        
def checkRequirement(controller, req):
    #TODO: block testing
    checkFailed = False
    if req.never == True:
        checkFailed = True
    else:
    
        if req.locationReq:
            if checkLocation(req.locationReq) == False:
                checkFailed = True
            
        if req.visitedReq:
            if checkVisited(controller, req.visitedReq) == False:
                checkFailed = True
                
        if req.notVisitedReq:
            if checkVisited(controller, req.notVisitedReq) == True:
                checkFailed = True
                
        if req.existTrait:
            if checkExist(req.existTrait, controller.game.player.traits) == False:
                checkFailed = True
                    
        if req.existStat:
            if checkExist(req.existStat, controller.game.player.stats) == False:
                checkFailed = True
                     
        if req.existSkill:
            if checkExist(req.existSkill, controller.game.player.skills) == False:
                checkFailed = True
        
        if req.existStatus:
            if checkExist(req.existStatus, controller.game.localStatus) == False:
                if checkExist(req.existStatus, controller.game.globalStatus) == False:
                    checkFailed = True
        
        if req.existItem:
            if checkExistItem(req.existItem, controller) == False:
                checkFailed = True
        
        if req.existKeyword:
            #TODO: implement keywords
            pass
        if req.notTrait:
            if checkNotExist(req.notTrait, controller.game.player.traits) == False:
                checkFailed = True
                    
        if req.notStat:
            if checkNotExist(req.notStat, controller.game.player.stats) == False:
                checkFailed = True
                     
        if req.notSkill:
            if checkNotExist(req.notSkill, controller.game.player.skills) == False:
                checkFailed = True
        
        if req.notStatus:
            if checkNotExist(req.notStatus, controller.game.localStatus) == False or \
               checkNotExist(req.notStatus, controller.game.globalStatus) == False:
                checkFailed = True
        if req.notItem:
            if checkNotExist(req.notItem, controller) == True:
                checkFailed = True
        
        if req.notKeyword:
            #TODO: implement keywords
            pass
        
        if req.comparison:
            if checkComparisonRequirement(controller, req.comparison) == True:
                checkFailed = True
                
        if req.expReq != False:
            if controller.game.player.exp < req.expReq:
                checkFailed = True
                
        if req.timeReq != False:
            if controller.game.time.getTotalMinutes() < req.timeReq.lboundTotal:
                checkFailed = True
            else:
                if req.timeReq.uboundTotal != False and req.timeReq.uboundTotal > 0:
                    if controller.game.time.getTotalMinutes() > req.timeReq.uboundTotal:
                        checkFailed = True
        if req.rollReq:
            if checkRollRequirement(controller, req.rollReq) == False:
                checkFailed = True
                
        #TODO: check XSD. should be treated as OR?
        if req.otherReqs:
            for x in req.otherReqs:
                if checkRequirement(x) == False:
                    checkFailed = True
                    
        #TODO: check XSD. should be treated as OR?
        #if we make it here, req is true. will return true except if req exceptions are true.
        if req.exceptionList:
            for x in req.exceptionList:
                if checkRequirement(x) == True:
                    checkFailed = True
        
    if checkFailed == True:
        return False
    else:
        return True
    
        
