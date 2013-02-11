'''
Created on 8.3.2012

@author: Tarmo
'''
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
import sessions
import datetime
import settings
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from game.models import DBSavedGame, DBGameModule, NewsArticle
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from utilities import wrapTags, wrapTagsWithInnerData
from game.models import DBArea


MODME_VERSION = "DEV0.01"
GAMEMODULES_START_COUNT = DBGameModule.objects.all().count()
SERVER_START = datetime.datetime.now()

ENABLE_GAME = True
ENABLE_UNVERIFIED = True
ENABLE_REGISTER = True
ENABLE_DESIGNER = True
ENABLE_PUBLISH = True

@login_required
def serverInfo(request):
    now = datetime.datetime.now()
    delta = now - SERVER_START
    uptime_str = str(delta.days) + " days, " + str(delta.seconds / 60) + " minutes."
    num_gamemodules = DBGameModule.objects.all().count()
    num_new_gamemodules = num_gamemodules - GAMEMODULES_START_COUNT
    num_users = User.objects.all().count()
    if sessions.LAST_ERROR != None:
        last_error_time = sessions.LAST_ERROR.isoformat()
    else:
        last_error_time = "None"
    
    info = {"timestamp" : now.isoformat(), "uptime" : uptime_str, "num_sessions" : len(sessions.session_dict), \
            "num_gamemodules" : num_gamemodules, "num_new_gamemodules" : num_new_gamemodules, "num_users" : num_users, \
            "num_errors" : sessions.ERRORS_SINCE_START, "last_error_time" : last_error_time, \
            "num_sessions_total" : sessions.SESSIONS_CREATED, \
            "play" : str(ENABLE_GAME), \
            "unver" : str(ENABLE_UNVERIFIED), \
            "register" : str(ENABLE_REGISTER), \
            "designer" : str(ENABLE_DESIGNER), \
            "publish" : str(ENABLE_PUBLISH), \
            "areas" : DBArea.objects.all()
            }
    
    return render_to_response("server_info.html", createTemplateData(info), context_instance=RequestContext(request))

def createTemplateData(add=None):
    BASIC_INFO = {"modme_version" : MODME_VERSION, "STATIC_URL" : settings.STATIC_URL}
    if add is not None:
        BASIC_INFO.update(add)
    return BASIC_INFO

def login_user(request):
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print "trying to authenticate: " + str(username) + ", " + str(password)

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render_to_response("game.html", createTemplateData(), context_instance=RequestContext(request))
            else:
                return render_to_response("login.html", createTemplateData(add={"message" : "Something went wrong."}), context_instance=RequestContext(request))
        else:
            return render_to_response("login.html", createTemplateData(add={"message" : "Incorrect username or password."}), context_instance=RequestContext(request))
    else:
        return render_to_response("login.html", createTemplateData(), context_instance=RequestContext(request))

@login_required
def logout_user(request):
    logout(request)
    return render_to_response("login.html", createTemplateData(add={"message" : "You have been logged out."}), context_instance=RequestContext(request))
    
def unverified(request):
    return index(request, templateName="unverified.html")

def about(request):
    return render_to_response("about.html", createTemplateData(), context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def control(request):
    return render_to_response("control.html", createTemplateData(), context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def site_feature_control(request):
    global ENABLE_GAME, ENABLE_UNVERIFIED, ENABLE_REGISTER, ENABLE_DESIGNER, ENABLE_PUBLISH
    
    response = HttpResponse(content_type="text/xml")
    toggle = request.GET.get("toggleFeature", default="")
    if toggle == "play": ENABLE_GAME = not ENABLE_GAME
    if toggle == "unver": ENABLE_UNVERIFIED = not ENABLE_UNVERIFIED
    if toggle == "publish": ENABLE_PUBLISH = not ENABLE_PUBLISH
    if toggle == "register": ENABLE_REGISTER = not ENABLE_REGISTER
    if toggle == "designer": ENABLE_DESIGNER = not ENABLE_DESIGNER
    
    xml = wrapTags("play", str(int(ENABLE_GAME)))
    xml += wrapTags("unver", str(int(ENABLE_UNVERIFIED)))
    xml += wrapTags("publish", str(int(ENABLE_PUBLISH)))
    xml += wrapTags("register", str(int(ENABLE_REGISTER)))
    xml += wrapTags("designer", str(int(ENABLE_DESIGNER)))
    
    response.write(wrapTagsWithInnerData("control", xml))
    return response

def index(request, templateName="game.html"):
    news = NewsArticle.objects.all().order_by("-date", "title")[:10]
    return render_to_response(templateName, createTemplateData({"news" : news}), context_instance=RequestContext(request))

def play(request):
    if ENABLE_GAME:
        id = str(request.GET.get("session", default=0))
        command = request.GET.get("command", default="something")
        
        if id == "0":
            return sessions.newSession(command)
        else:
            return sessions.updateSession(command, id)
    else:
        return HttpResponse(content=wrapTagsWithInnerData("message", wrapTags("error", "Administrator has disabled the game for now. Sorry!")), content_type="text/xml")

@login_required
def loadgame(request):
    savename_message = request.GET.get("savename", default="")
    
    if savename_message is not "" and ENABLE_GAME:
        return sessions.loadSession(request.user, savename_message)
    else:
        response = HttpResponse(content_type="text/xml")
        response.write(wrapTagsWithInnerData("load_message", wrapTags("message", "Load failed")))
        return response

@login_required
def loadgames_popup(request):
    savedgames = DBSavedGame.objects.filter(user=request.user)
    return render_to_response("loadgames.html", createTemplateData({"saved_games" : savedgames}), context_instance=RequestContext(request))

@login_required
def savegame(request):
    savename_message = request.GET.get("savename", default="")
    sessionId = str(request.GET.get("session", default="0"))
    response_text = ""
    if savename_message is not "" and sessionId in sessions.session_dict:
        response_text = sessions.saveSession(request.user, sessionId, savename_message)
    else:
        response_text = "Something went wrong!"
        
    response = HttpResponse(content_type="text/xml")
    response.write(wrapTags("save_response", response_text))
    return response

@login_required
def savedgames_popup(request):
    savedgames = DBSavedGame.objects.filter(user=request.user)
    return render_to_response("savedgames.html", createTemplateData({"saved_games" : savedgames}), context_instance=RequestContext(request))
    
           
