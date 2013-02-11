from django.http import HttpResponse

from gameutil import Quest

from utilities import wrapTags, wrapTagsWithInnerData

class MainWindowView():
    def __init__(self, creator):
        self.owner = creator
        self.suppressEmptyLines = False
        self.log = []
        self.newLines = []
        self.nameGiven = "Someone"
        self.emptyLineBeforeText = False
        self.commandList = []
        self.healthViewText = ""
        self.expViewText = ""
        self.questViewText = ""
        self.locationViewText = ""
        self.timeViewText = ""
        self.gameStart = True
        
    def createLogText(self):
        text = "\nplayer name: " + self.nameGiven
        text += "\nhealth " + self.healthViewText
        text += "\nexp: " + self.expViewText
        text += "\nquest: " + self.questViewText
        text += "\nlocation: " + self.locationViewText
        text += "\ntime: " + self.timeViewText
        text += "GAME LOG-------------------"
        for x in self.log: 
            text += "\n" + x
        return text
        
    def addLine(self, line):
        self.newLines.append(line)
        self.log.append(line)
        
    def setNameGiven(self, name):
        self.nameGiven = str(name)
        
    def createInfoText(self): 
        infoText = wrapTags("name", self.nameGiven) + wrapTags("health", self.healthViewText) + wrapTags("experience", self.expViewText)
        
        if self.owner.game.player.equippedWeapon:
            infoText += wrapTags("weapon", self.owner.game.player.equippedWeapon.name)
        else:
            infoText += wrapTags("weapon", "Punch")
        
        infoText += wrapTags("quest", self.questViewText) + wrapTags("location", self.locationViewText) + wrapTags("time", self.timeViewText)
        return wrapTagsWithInnerData("info", infoText)
    
    def updateInfoView(self):
        self.setHealthDisplay(self.owner.game.player.health)
        self.setExpDisplay(self.owner.game.player.exp)
        self.setTimeDisplay(self.owner.game.time.weekday, self.owner.game.time.hours, self.owner.game.time.minutes, self.owner.game.time.seconds)
        
        #TODO: refactoooor
        self.owner.game.quest = Quest("Get milk", "Your quest is to find milk from somewhere, possibly buy it with money from a store.")
        self.setQuestDisplay(self.owner.game.quest.name)
    
    def createStatsText(self):
        self.updateCommandText()
        
        statsText = ""
        for command in self.commandList:
            statsText += wrapTagsWithInnerData("command", wrapTags("command_name", command.name) + wrapTags("command_type", command.type)) + "\n"
        for trait in self.owner.game.player.traits:
            statsText += wrapTags("trait_name", trait.name) + "\n"
        for stat in self.owner.game.player.stats:
            statsText += wrapTagsWithInnerData("stat", wrapTags("stat_name", stat.name) + wrapTags("stat_value", stat.value)) + "\n"
        for skill in self.owner.game.player.skills:
            statsText += wrapTagsWithInnerData("skill", wrapTags("skill_name", skill.name) + wrapTags("skill_value", skill.value)) + "\n"
        for item in self.owner.game.player.items:
            statsText += wrapTags("item_name", item.name) + "\n"
        
        return wrapTagsWithInnerData("stats", statsText)
    
    def createMainText(self):
        mainText = ""
        for text in self.newLines:
            mainText += "\n" + text
        return wrapTags("main", mainText)
    
    def createTabbedWordsText(self):
        text = ""
        area = self.owner.game.visited[self.owner.game.currentLocation.giveFormattedLoc()]
        for x in area.npcs:
            text += wrapTags("entity", x.name.lower())
        for x in area.items:
            text += wrapTags("entity", x[0].name.lower())
            
        return wrapTagsWithInnerData("tabs", text)
    
    def getResponse(self, id):
        response = HttpResponse(content_type="text/xml")
        response.write(self.getResponseXml(id))
        return response
    
    def getResponseXml(self, id):
        text = wrapTagsWithInnerData("result", self.createInfoText() + self.createStatsText() + self.createMainText() + self.createTabbedWordsText() + wrapTags("id", id))
        self.newLines = []
        return text
    
    def getGameObject(self):
        return self.owner.game
    
    def loadGame(self, gameObject):
        
        self.owner.loadGame(gameObject)
        
    def transmitCommand(self, command, id):
        if self.gameStart:
            self.gameStart = False
            self.addLine(">" + self.nameGiven.lower())
            self.owner.newGame()
        else:
            self.owner.receiveCommand(command.lower().encode('utf-8'))
            self.updateSideDisplay()
        
        return self.getResponse(id)
        
    def start(self):
        pass
            
    def askName(self):
        #TODO: reimplement this
        return self.nameGiven
        
    def sendCommandLineToMain(self, text):
        if self.emptyLineBeforeText == True and self.suppressEmptyLines == False:
            self.addLine("")
        self.addLine(text)
        self.emptyLineBeforeText = False
    
    def sendToMain(self, text):
        if self.emptyLineBeforeText == True and self.suppressEmptyLines == False:
            self.addLine("")
        self.addLine(text)
        self.emptyLineBeforeText = False
        
    def sendEmptyLineMain(self):
        self.emptyLineBeforeText = True
        
    def clearMain(self):
        #TODO: reimplement
        pass
        
    def updateCommandText(self):
        self.commandList = []
        for command in self.owner.game.areaCommands:
            if command.checkListRequirements(self.owner) == True \
            and (not self.owner.game.exclusiveCommands \
            or command.name == self.owner.game.exclusiveCommands[0].name):
                self.commandList.append(command)    
                
        for command in self.owner.game.globalCommands:
            if command.checkListRequirements(self.owner) == True:
                self.commandList.append(command)
                
    def updateCommandWindow(self):
        pass
        
    def updateStatWindow(self):
        pass
        
    def updateItemWindow(self):
        pass
        
    def updateTraitWindow(self):
        pass
        
    def updateSkillWindow(self):
        pass
        
    def updateSideDisplay(self):
        self.updateTraitWindow()
        self.updateSkillWindow()
        self.updateStatWindow()
        self.updateItemWindow()
        
    def setNameDisplay(self, text):
        pass
        
    def setHealthDisplay(self, text):
        self.healthViewText = str(text)
        
    def setExpDisplay(self, text):
        self.expViewText = str(text)
        
    def setQuestDisplay(self, text):
        self.questViewText = str(text)
        
    def setLocation(self, loc):
        self.setLocationDisplay(str(loc))
        
    def setLocationDisplay(self, text):
        self.locationViewText = str(text)
        
    def setTimeDisplay(self, weekday, hours, minutes, secs):
        if hours < 10:
            strhours = "0" + str(hours)
        else:
            strhours = str(hours)
        if minutes < 10:
            strmins = "0" + str(minutes)
        else:
            strmins = str(minutes)
        if secs < 10:
            strsecs = "0" + str(secs)
        else:
            strsecs = str(secs)
            
        self.timeViewText = (weekday + ", " + strhours + ":" + strmins + ":" + strsecs) 
        
    def showErrorDialog(self, errorText):
        self.addLine("!!! " + str(errorText))
