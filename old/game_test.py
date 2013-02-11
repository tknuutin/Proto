'''
Created on 27.6.2012

@author: Tarmo
'''

import control
import gameview
import os, sys

class TestView(gameview.MainWindowView):
    def transmitCommand(self, command, id, printResult=True):
        if self.gameStart:
            self.gameStart = False
            self.addLine(">" + self.nameGiven.lower())
            self.owner.newGame()
        else:
            self.owner.receiveCommand(command.lower().encode('utf-8'))
            self.updateSideDisplay()
        
        return self.getResponse(id, printResult=printResult)
    
    def getResponse(self, id, printResult=True):
        if printResult: 
            for text in self.newLines:
                print text
            self.newLines = []
        else:
            a = self.newLines
            self.newLines = []
            return a

def main():
    ctrl = control.MainController()
    test_view = TestView(ctrl)
    test_view.setNameGiven("Buttlord Wiener")
    ctrl.view = test_view
    
    startGame(test_view)
    
def startGame(view):
    cmd = ""
    control.PATH_AREASCHEMA = str(os.path.dirname(sys.argv[0])) + "\\areaschema.xsd"
    control.PATH_HOME_BEDROOM = str(os.path.dirname(sys.argv[0])) + "\\base\\area_home_bedroom.xml"
    
    print "--- Starting test session. \n"
    
    auto = True
    
    if not auto:
        while cmd != "quit":
            print "You giev command! > "
            cmd = raw_input()
            
            if cmd == "run autotest":
                runAutoTest(view)
                break
            
            view.transmitCommand(cmd, "test_session")
    else: 
        runAutoTest(view)
        
    print "--- Ending test session."

def test_cmd(view, cmd): return view.transmitCommand(cmd, "test_id", printResult=False)

def checkSpawningWorks(view):
    test_cmd(view, "start game")
    test_cmd(view, "open curtains")
    test_cmd(view, "go to the kitchen")
    r = test_cmd(view, "examine room")
    print "--Current game text--"
    for text in r:
        print text
    print "--End current game text--"
    if r[len(r) - 1] == "Looks like there is absolutely nothing else of importance here.": return False
    else: return True
    
def nullTest(view):
    return True

def runAutoTest(view):
    a = [(checkSpawningWorks, "spawntest"), (nullTest, "null")]
    for test, name in a:
        if not test(view): print "FAILURE: " + name
        else: print "OK: " + name

if __name__ == '__main__':
    main()
