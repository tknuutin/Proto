
import datetime, traceback
import uuid, sys
import game as protogame
from utilities import wrapTags, wrapTagsWithInnerData
from django.http import HttpResponse
from proto import models

session_dict = dict()
last_purge = datetime.datetime.now()
PURGE_PASS_INTERVAL = 300 #5 minutes between checks for old sessions
PURGE_THRESHOLD = 1800 #30 minutes for a session to get old

ERRORS_SINCE_START = 0
LAST_ERROR = None
SESSIONS_CREATED = 0

class WebView(object):
    """ Web interface controller. """
    def __init__(self, game):
        self.game = game
        self.log = []
    
    def get_response(self, main_text, uid):
        response = HttpResponse(content_type="text/xml")
        response.write(wrapTagsWithInnerData("result", wrapTagsWithInnerData("lines", main_text) + wrapTags("uid", uid)))
        return response    
        
    def send_command(self, command, uid):
        main_text = ""
        for text in self.game.send_command(command):
            main_text += wrapTags("line", text)
            self.log.append(text)
        return self.get_response(main_text, uid)
    
    def default_start(self, uid):
        main_text = ""
        for text in self.game.default_start():
            main_text += wrapTags("line", text)
            self.log.append(text)
        return self.get_response(main_text, uid)
    
    def create_logtext(self):
        text = "\nPlayer name: " + self.game.playername
        text += "GAME LOG-------------------"
        for x in self.log: 
            text += "\n" + x
        return text

class Session():
    """ Container for the DBSession and other objects. """
    def __init__(self, name, user):
        self.uid = str(uuid.uuid4().hex)
        dbsession = models.DBSession()
        dbsession.save()
        self.dbid = dbsession.id
        
        game = protogame.Game(name, dbsession, user)
        self.view = WebView(game)
        self.last_update = datetime.datetime.now()
        

def create_logfile(session, folderName, command, exception):
    """ Create log file for given session in the given folder with given supplemental info. """
    global ERRORS_SINCE_START, LAST_ERROR
    filename = type(exception).__name__ + "-" + str(datetime.datetime.today().date()) + "-" + str(datetime.datetime.today().time()).replace(":", "-").replace(".", "-")
    ERRORS_SINCE_START += 1
    try:
        logfile = open(folderName + "/" + filename + ".log", 'w')
        logfile.write("last command: " + str(command))
        logfile.write("\nTRACEBACK START " + "-" * 60 + "\n")
        traceback.print_exc(file=logfile)
        logfile.write("\nTRACEBACK END " + "-" * 60)
        logfile.write(session.view.create_logtext())
        logfile.close()
    except IOError:
        print "Warning: IOError!"
        traceback.print_exc()
        ERRORS_SINCE_START += 1
    LAST_ERROR = datetime.datetime.now()


def new_session(player_name, user):
    """ Create a new session with the given player name. Returns a HttpResponse with the game info and id. """
    global SESSIONS_CREATED
    session = Session(str(player_name).capitalize(), user)
    uid = session.uid
    session_dict[uid] = session
    SESSIONS_CREATED += 1
    
    try:
        response = session.view.default_start(uid)
        return response
    except Exception as e:
        print "Creating logfile"
        create_logfile(session, "errorlogs", "new_game", e)
        raise

def purge_nonupdated():
    """ Purge old sessions from memory, that is, sessions that have exceeded PURGE_THRESHOLD. """
    global last_purge
    
    print "Starting purge."
    
    todel = []
    for uid, session in session_dict.iteritems():
        delta = datetime.datetime.now() - session.last_update
        if (delta.days * 86400 + delta.seconds) > PURGE_THRESHOLD:
            todel.append(uid)
            models.DBSession.objects.get(id=session.dbid).delete()
    
    counter = 0
    for key in todel:
        
        del session_dict[key]
        counter += 1
    print "Purged " + str(counter) + " sessions."
    last_purge = datetime.datetime.now()

def update_session(command, uid):
    """ Update a session with the given command. Returns game info after the command as an XML HttpResponse. """
    global last_purge
    
    delta = datetime.datetime.now() - last_purge
    if (delta.days * 86400 + delta.seconds) > PURGE_PASS_INTERVAL:
        purge_nonupdated()
    
    if uid in session_dict:
        session = session_dict[uid]
        session.last_update = datetime.datetime.now()
        try:
            response = session.view.send_command(command, uid)
            return response
        except Exception as e:
            print "Creating logfile"
            create_logfile(session, "errorlogs", command, e)
            raise
    else:
        return HttpResponse("<result><error>Invalid session ID. This can be because your session has expired.</error></result>")
    
        
