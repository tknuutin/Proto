'''
Created on Jan 8, 2013

@author: TarmoK
'''

from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.sites.models import get_current_site

from django.template import RequestContext
from views import createTemplateData
from utilities import wrapTags, wrapTagsWithInnerData, get_empty_names
from django.contrib.auth.decorators import login_required
from proto.models import DBLocation, DBCondition, DBEvent, DBFeature, UserProfile, DBGame, Connection, DBGameModule

from django.shortcuts import render_to_response, redirect

MODULE_FIELDS = {
    "location" : {
        "class" : DBLocation,
        "fieldnames" : (("adminname", "editorname"), "name", "ftdesc", "desc", "notes"), 
        "mandatoryfields" : (("Editor name", "adminname"), ("Name", "name"), ("First time description", "ftdesc"), ("Description", "desc"))
    },
    "feature" : {
        "class" : DBFeature,
        "fieldnames" : (("adminname", "editorname"), "moduleid", "name", "desc", "notes"), 
        "mandatoryfields" : (("Editor name", "adminname"), ("Name", "name"), ("Description", "desc"), ("Location to attach", "moduleid"))        
    }   
}

#TODO: refactor
DOMAIN = "http://www.modme-game.net"

class NullModule(object):
    """ A dummy module for forms which describe a new module. """
    def __init__(self, fields=None):
        self.name = (fields["name"]) if fields else ""
        self.desc = (fields["desc"]) if fields else ""
        self.ftdesc = (fields["ftdesc"]) if fields else ""
        self.id = 0
        self.adminname = (fields["adminname"]) if fields else ""
        self.notes = (fields["notes"]) if fields else ""
        self.module = (DBLocation.objects.get(id=int(fields["moduleid"]))) if fields and fields["moduleid"] and DBGameModule.objects.filter(id=int(fields["moduleid"])) else {"name" : "", "id" : ""}

def editor_error(request, moduletype, message):
    """ Display editor error. """
    messages.error(request, message)
    return render_to_response(moduletype + ".html", createTemplateData({moduletype: NullModule(), "user_can_edit_module" : False}), context_instance=RequestContext(request))

def get_fields_from_request(request, fieldnames=tuple(), mandatoryfields=tuple()):
    fields = {}
    for nameparameter in fieldnames:
        dbname = nameparameter[0] if not isinstance(nameparameter, basestring) else nameparameter
        postname = nameparameter[1] if not isinstance(nameparameter, basestring) else nameparameter
        fields[dbname] = request.POST.get(postname, None)
        
    for mandatoryname, field in mandatoryfields:
        if not field in fields: 
            return False, fields, "Please input valid values to the field: " + mandatoryname
        
    fields["creator"] = request.user
    #TODO: add other game support
    fields["game"] = DBGame.objects.get(name="default")
    return True, fields, "Fields okay."

@login_required
def module_save(request, cls, fieldnames, mandatoryfields, moduleid=None):
    """ Save generic module based on the request and lists of fields and mandatory fields. Can create a new module or can edit an existing module. """
    
    fieldsok, fields, message = get_fields_from_request(request, fieldnames=fieldnames, mandatoryfields=mandatoryfields)
    if fieldsok:
        if not UserProfile.objects.get(user=request.user).disabled:
            savesuccess, savemsg, created_id = cls.save_from_request(request, fields, moduleid=moduleid)
            if savesuccess:
                messages.success(request, savemsg)
                return HttpResponseRedirect(DOMAIN + reverse(cls.get_simple_name() + "-edit", args=(created_id,)))
            else:
                messages.error(request, savemsg)
                return render_to_response(cls.get_simple_name() + ".html", createTemplateData({cls.get_simple_name(): NullModule(fields), "user_can_edit_module" : False}), context_instance=RequestContext(request)) 
        else:
            return editor_error(request, cls.get_simple_name(), "Error: User account disabled.")
    else:
        return editor_error(request, cls.get_simple_name(), message)

@login_required
def module_delete(request, cls, moduleid):
    if cls.objects.filter(id=moduleid).exists():
        module = cls.objects.get(id=moduleid)
        if module.is_editable(request.user):
            #TODO: make status into deleted instead of actually deleting it?
            module.delete()
            messages.success(request, "Succesfully deleted " + cls.get_simple_name().capitalize())
            return HttpResponseRedirect(DOMAIN + reverse("editor-main"))
        else:
            messages.error("You are not authorized to delete this module.")
            return render_to_response(cls.get_simple_name() + ".html", createTemplateData({cls.get_simple_name(): module, "user_can_edit_module" : False}), context_instance=RequestContext(request))
    else:
        messages.error("Module not found.")
        return HttpResponseRedirect(reverse("editor-main"))
    
@login_required
def module_publish(request, cls, moduleid):
    if cls.objects.filter(id=moduleid).exists():
        module = cls.objects.get(id=moduleid)
        if module.is_editable(request.user):
            module.publish()
            module.save()
            messages.success(request, "Succesfully published " + cls.get_simple_name().capitalize())
            return render_to_response(cls.get_simple_name() + ".html", createTemplateData({cls.get_simple_name(): module, "user_can_edit_module" : True}), context_instance=RequestContext(request))
        else:
            messages.error("You are not authorized to publish this module.")
            return render_to_response(cls.get_simple_name() + ".html", createTemplateData({cls.get_simple_name(): module, "user_can_edit_module" : False}), context_instance=RequestContext(request))
    else:
        messages.error("Module not found.")
        return HttpResponseRedirect(reverse("editor-main"))
    
@login_required
def module_unpublish(request, cls, moduleid):
    if cls.objects.filter(id=moduleid).exists():
        module = cls.objects.get(id=moduleid)
        if module.is_editable(request.user) and (module.play_status != "VE" or request.user.is_superuser):
            module.unpublish()
            module.save()
            messages.success(request, "Succesfully unpublished " + cls.get_simple_name().capitalize())
            return render_to_response(cls.get_simple_name() + ".html", createTemplateData({cls.get_simple_name(): module, "user_can_edit_module" : True}), context_instance=RequestContext(request))
        else:
            messages.error("You are not authorized to unpublish this module.")
            return render_to_response(cls.get_simple_name() + ".html", createTemplateData({cls.get_simple_name(): module, "user_can_edit_module" : False}), context_instance=RequestContext(request))
    else:
        messages.error("Module not found.")
        return HttpResponseRedirect(reverse("editor-main"))
        
@login_required
def selector(request, moduletype):
    filtered = [loc for loc in DBLocation.objects.all() if loc.is_usable_in_editor(request.user)]
    return render_to_response(moduletype + "_select.html", createTemplateData({"locations": filtered}), context_instance=RequestContext(request))

def module(request, moduletype, moduleid=None):
    if request.POST:
        if "save" in request.POST:
            return module_save(request, MODULE_FIELDS[moduletype]["class"], 
                               fieldnames=MODULE_FIELDS[moduletype]["fieldnames"], 
                               mandatoryfields=MODULE_FIELDS[moduletype]["mandatoryfields"],
                               moduleid=moduleid)
            
        if "delete" in request.POST:
            return module_delete(request, MODULE_FIELDS[moduletype]["class"], moduleid)
        if "publish" in request.POST:
            return module_publish(request, MODULE_FIELDS[moduletype]["class"], moduleid)
        if "unpublish" in request.POST:
            return module_unpublish(request, MODULE_FIELDS[moduletype]["class"], moduleid)
        
    if moduleid:
        if moduleid.isdigit() and MODULE_FIELDS[moduletype]["class"].objects.filter(id=int(moduleid)).exists():
            oldmodule = MODULE_FIELDS[moduletype]["class"].objects.get(id=int(moduleid))
            if oldmodule.is_editable(request.user):
                return render_to_response(moduletype + ".html", createTemplateData({moduletype: oldmodule, "user_can_edit_module" : True}), context_instance=RequestContext(request))
            else:
                return render_to_response(moduletype + ".html", createTemplateData({moduletype: oldmodule, "user_can_edit_module" : False}), context_instance=RequestContext(request))
        else:
            messages.error(request, ("Error: No such %s" % (moduletype.capitalize())))
    return render_to_response(moduletype + ".html", createTemplateData({moduletype: NullModule(), "user_can_edit_module" : True}), context_instance=RequestContext(request))

@login_required  
def location(request, locationid=None): return module(request, "location", locationid)
@login_required  
def feature(request, locationid=None): return module(request, "feature", locationid)

@login_required
def editor_main(request):
    """ Editor main view. """
    locations = DBLocation.objects.all() if request.user.is_superuser else DBLocation.objects.filter(creator=request.user)
    events = DBEvent.objects.all() if request.user.is_superuser else DBEvent.objects.filter(creator=request.user)
    features = DBFeature.objects.all() if request.user.is_superuser else DBFeature.objects.filter(creator=request.user)
    conditions = DBCondition.objects.all() if request.user.is_superuser else DBCondition.objects.filter(creator=request.user)
    return render_to_response("editor_main.html", createTemplateData({"locations": locations, "events" : events, "features" : features, "conditions" : conditions}), context_instance=RequestContext(request))