'''
Created on Dec 17, 2012

@author: TarmoK
'''
PROTO_VERSION = "0.01"
ENABLE_GAME = True

from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.http import HttpResponse
from utilities import wrapTags, wrapTagsWithInnerData, validate_email
from django.contrib.auth.decorators import login_required
import sessions
from proto.models import UserProfile
from django.contrib.auth.models import User

def createTemplateData(add=None):
    """ Convenience function, this kinda sucks, refactor """
    BASIC_INFO = {"modme_version" : PROTO_VERSION, "STATIC_URL" : "/static/"}
    if add is not None:
        BASIC_INFO.update(add)
    return BASIC_INFO

@login_required
def settings(request):
    profile = UserProfile.objects.get(user=request.user)
    if request.POST:
        filtermode = request.POST.get('filter', None)
        profile.filtermode = 0 if filtermode == "verified" else 1
        profile.save()
        return render_to_response("settings.html", createTemplateData({"message" : "Settings saved.", "filter" : profile.filtermode}), context_instance=RequestContext(request))
    return render_to_response("settings.html", createTemplateData({"filter" : profile.filtermode}), context_instance=RequestContext(request))
            

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
                return render_to_response("proto_main.html", createTemplateData(), context_instance=RequestContext(request))
            else:
                return render_to_response("login.html", createTemplateData(add={"message" : "Something went wrong."}), context_instance=RequestContext(request))
        else:
            return render_to_response("login.html", createTemplateData(add={"message" : "Incorrect username or password."}), context_instance=RequestContext(request))
    else:
        return render_to_response("login.html", createTemplateData(), context_instance=RequestContext(request))

def register(request):
    if request.POST:
        username = request.POST.get('username', None)
        pass1 = request.POST.get('pass1', None)
        pass2 = request.POST.get('pass2', None)
        email = request.POST.get('email', None)
        
        if username and pass1 and pass2 and email:
            if pass1 != pass2:
                return render_to_response("register.html", createTemplateData(add={"message" : "Passwords do not match."}), context_instance=RequestContext(request))
            elif validate_email(email) == False:
                return render_to_response("register.html", createTemplateData(add={"message" : "Invalid email."}), context_instance=RequestContext(request))
            else:
                try:
                    User.objects.get(username=username)
                    return render_to_response("register.html", createTemplateData(add={"message" : "User already exists."}), context_instance=RequestContext(request))
                except User.DoesNotExist:
                    newuser = User.objects.create_user(username, email, pass1)
                    newuser.save()
                    newprofile = UserProfile(user=newuser)
                    newprofile.save()
                    return render_to_response("login.html", createTemplateData(add={"message" : "User account created succesfully!"}), context_instance=RequestContext(request))
                
    return render_to_response("register.html", createTemplateData(), context_instance=RequestContext(request))

@login_required
def logout_user(request):
    logout(request)
    return render_to_response("login.html", createTemplateData(add={"message" : "You have been logged out."}), context_instance=RequestContext(request))

def about(request):
    return render_to_response("about.html", createTemplateData(), context_instance=RequestContext(request))

def index(request, templateName="proto_main.html"):
    return render_to_response(templateName, createTemplateData(), context_instance=RequestContext(request))

def empty_index(request, templateName="empty.html"):
    return render_to_response(templateName, createTemplateData(), context_instance=RequestContext(request))

def play(request):
    if ENABLE_GAME:
        uid = str(request.GET.get("session", default=0))
        command = request.GET.get("command", default="something")
        
        if uid == "0":
            return sessions.new_session(command, request.user)
        else:
            return sessions.update_session(command, uid)
    else:
        return HttpResponse(content=wrapTagsWithInnerData("message", wrapTags("error", "Administrator has disabled the game for now. Sorry!")), content_type="text/xml")





