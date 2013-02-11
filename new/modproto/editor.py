'''
Created on Jan 8, 2013

@author: TarmoK
'''

from django.http import HttpResponseRedirect
from django.template import RequestContext
from views import createTemplateData
from utilities import wrapTags, wrapTagsWithInnerData
from django.contrib.auth.decorators import login_required
from proto.models import DBLocation, DBCondition, DBEvent, DBFeature, UserProfile, DBGame

from django.shortcuts import render_to_response, redirect

class NullModule(object):
    """ A dummy module for forms which describe a new module. """
    def __init__(self):
        self.name = ""
        self.desc = ""
        self.ftdesc = ""
        self.id = 0
        self.adminname = ""
        
def get_empty_names(fields):
    """ Get the names of all the fields that have empty string values or None values. """
    empties = []
    for key, value in fields.iteritems():
        if value == None or value == "":
            empties.append(key)
    return ", ".join(empties)

def editor_error(request, template, message):
    """ Display editor error. """
    return render_to_response(template, createTemplateData({"location": NullModule(), "message" : message}), context_instance=RequestContext(request))

@login_required
def location_save(request):
    """ Save location View. """
    editorname = request.POST.get('editorname', None)
    name = request.POST.get('name', None)
    ftdesc = request.POST.get('ftdesc', None) or None
    desc = request.POST.get('desc', None)
    notes = request.POST.get('notes', None) or None
    if not UserProfile.objects.get(user=request.user).disabled:
        if editorname and name and desc:
            #TODO: allow custom games
            game = DBGame.objects.get(name="default")
            if not DBLocation.objects.filter(name=name, game=game).exists():
                newloc = DBLocation(creator=request.user, game=game, adminname=editorname, name=name, ftdesc=ftdesc, desc=desc, notes=notes)
                newloc.save()
                return redirect("/proto/editor/location/" + str(newloc.id))
            else:
                return editor_error(request, "location.html", "Location with that name already exists for the specified game.")
        else:
            return editor_error(request, "location.html", "Please input valid values to the fields: " + get_empty_names({"Name" : name, "Editor name" : editorname, "Description" : desc}))
    else:
        return editor_error(request, "location.html", "Error: User account disabled.")

@login_required  
def location(request, id=None, message=None):
    """ Editor Location form. """
    if request.POST:
        return location_save(request)
    if id:
        if id.isdigit() and DBLocation.objects.filter(id=int(id)).exists():
            oldlocation = DBLocation.objects.filter(id=int(id))[0]
            if oldlocation.is_editable(request.user):
                return render_to_response("location.html", createTemplateData({"location": oldlocation, "message" : message}), context_instance=RequestContext(request))
            else:
                return editor_error(request, "location.html", "Not editable by you.")
        else:
            return editor_error(request, "location.html", "Error: No such Location.")
    return render_to_response("location.html", createTemplateData({"location": NullModule(), "message" : message}), context_instance=RequestContext(request))

@login_required
def editor_main(request):
    """ Editor main view. """
    locations = DBLocation.objects.filter(creator=request.user)
    events = DBEvent.objects.filter(creator=request.user)
    features = DBFeature.objects.filter(creator=request.user)
    conditions = DBCondition.objects.filter(creator=request.user)
    return render_to_response("editor_main.html", createTemplateData({"locations": locations, "events" : events, "features" : features, "conditions" : conditions}), context_instance=RequestContext(request))