
import control, pickle
import datetime, traceback
import uuid, sys
from django.http import HttpResponse
from game.models import DBSavedGame

session_dict = dict()
last_purge = datetime.datetime.now()
PURGE_PASS_INTERVAL = 300 #5 minutes between checks for old sessions
PURGE_THRESHOLD = 1800 #30 minutes for a session to get old

ERRORS_SINCE_START = 0
LAST_ERROR = None
print "assigning sessions created now!"
SESSIONS_CREATED = 0

#Game session that contains the game interface and other game data.
class Session():
    def __init__(self, name):
        self.id = str(uuid.uuid4().hex)
        
        ctrl = control.MainController()
        self.view = ctrl.view
        self.view.setNameGiven(name)
        self.last_update = datetime.datetime.now()

#Create log file for given session in the given folder with given supplemental info info.
def createLogFile(session, folderName, command, exc_type, exc_value, exc_traceback):
    global ERRORS_SINCE_START, LAST_ERROR
    filename = str(session.id) + "-" + str(datetime.datetime.today().date()) + "-" + str(datetime.datetime.today().time()).replace(":", "-").replace(".", "-")
    ERRORS_SINCE_START += 1
    try:
        logfile = open(folderName + "/" + filename + ".log", 'w')
        logfile.write("last command: " + str(command))
        logfile.write("\nTRACEBACK START " + "-" * 60 + "\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=logfile)
        logfile.write("\nTRACEBACK END " + "-" * 60)
        logfile.write(session.view.createLogText())
        logfile.close()
    except IOError:
        print "Warning: IO error!"
        ERRORS_SINCE_START += 1
    LAST_ERROR = datetime.datetime.now()

#Load the given session of the given user 
def loadSession(user, savename):
    db_save = DBSavedGame.objects.get(user__exact=user, savename__exact=savename)
    
    save_file = db_save.save_file
    save_file.id = str(uuid.uuid4().hex)
    
    save_file.view.newLines = ["What were you doing again? You take a moment to look around and reacquint yourself with your surroundings."]
    game_data = save_file.view.getResponseXml(save_file.id)
    
    id = save_file.id
    session_dict[id] = save_file
    
    print "New session created with id " + str(id) + ". Now has " + str(len(session_dict)) + " sessions."
    
    response = HttpResponse(content_type="text/xml")
    response.write("<load_message><message>Load succesful!</message>" + game_data + "</load_message>")
    return response

#Save a given session to the given user with the given savename. Giving an existing savename will overwrite the old one.
def saveSession(user, sessionId, savename):
    session = session_dict[sessionId]
    name = session.view.nameGiven
    
    old = DBSavedGame.objects.filter(user__exact=user, savename__exact=savename)
    if old: old[0].delete()
        
    s = DBSavedGame(user=user, savename=savename, playername=name, date=datetime.datetime.today(), save_file=session)
    s.save()
    
    return "Saved succesfully."

#Create a new session with the given playername. Returns a HttpResponse with the game info and id.
def newSession(playerName):
    global SESSIONS_CREATED
    session = Session(str(playerName).capitalize())
    id = session.id
    session_dict[id] = session
    SESSIONS_CREATED += 1
    
    try:
        response = session.view.transmitCommand("new_game", id)
        return response
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        createLogFile(session, "errorlogs", "new_game", exc_type, exc_value, exc_traceback)
        raise

#Purge old sessions from memory, that is, sessions that have exceeded PURGE_THRESHOLD.
def purgeNonUpdated():
    global last_purge
    
    print "Starting purge."
    
    todel = []
    for id, session in session_dict.iteritems():
        delta = datetime.datetime.now() - session.last_update
        if (delta.days * 86400 + delta.seconds) > PURGE_THRESHOLD:
            todel.append(id)
    
    counter = 0
    for key in todel:
        del session_dict[key]
        counter += 1
    print "Purged " + str(counter) + " sessions."
    last_purge = datetime.datetime.now()

#Update a session with the given command. Returns game info after the command as an XML HttpResponse.
def updateSession(command, id):
    global last_purge
    
    delta = datetime.datetime.now() - last_purge
    if (delta.days * 86400 + delta.seconds) > PURGE_PASS_INTERVAL:
        purgeNonUpdated()
    
    if id in session_dict:
        session = session_dict[id]
        session.last_update = datetime.datetime.now()
        try:
            response = session.view.transmitCommand(command, id)
            return response
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            createLogFile(session, "errorlogs", command, exc_type, exc_value, exc_traceback)
            raise
    else:
        return HttpResponse("<result><error>Invalid session ID. This can be because your session has expired. Load the last autosave to continue.</error></result>")
    
        
