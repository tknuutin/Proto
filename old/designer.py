'''
Created on 16.6.2012

@author: Tarmo
'''
from django.middleware.csrf import get_token #required for Ajax post
from django.template import RequestContext
from django.http import HttpResponse
import settings
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from game.models import DBArea, DBCommand
from django.contrib.auth.decorators import login_required
import views
import utilities as u
from django.utils import simplejson

def save_area(user, json_data):
    save_id = json_data["module_info"]["module_id"]
    if save_id == "" or save_id == "0":
        new_area = DBArea(creator=user, play_status="UN", design_status="OW", name=json_data["module_info"]["name"], location=json_data["module_info"]["location"], \
               fast_travel=u.parseBool(json_data["module_info"]["fast_travel"]), first_desc_xml=u.dictToXml("description", json_data["ft_desc"]), \
               default_desc_xml=u.dictToXml("description", json_data["def_desc"]), notes=json_data["notes"])
        new_area.save()
        id = new_area.id
        return "Save succesful.", id
        
    elif u.idExists(save_id):
        area = DBArea.objects.get(id=save_id)
        
        #TODO: features, transevents
        if (area.isEditable() and user.id == area.creator.id) or user.is_superuser:
            area.name = json_data["module_info"]["name"]
            area.location = json_data["module_info"]["location"]
            area.fast_travel = u.parseBool(json_data["module_info"]["fast_travel"])
            area.first_desc_xml = u.dictToXml("description", json_data["ft_desc"])
            area.default_desc_xml = u.dictToXml("description", json_data["def_desc"])
            area.notes = json_data["notes"]
            area.save()
            return "Save succesful.", area.id

@login_required
def design_main(request):
    areas = DBArea.objects.filter(creator=request.user)
    commands = DBCommand.objects.filter(creator=request.user)
    return render_to_response("design_main.html", views.createTemplateData({"areas": areas, "commands" : commands}), context_instance=RequestContext(request))

@login_required
def new(request, type):
    #TODO: add functionality
    dummy = u.DummyA()
    dummy.created_by = request.user
    if type == "area":
        return render_to_response("design_area.html", views.createTemplateData({"area": dummy, "d_title_prefix" : "New"}), context_instance=RequestContext(request))
    elif type == "command":
        return render_to_response("design_command.html", views.createTemplateData({"area": dummy, "command": dummy, "d_title_prefix" : "New"}), context_instance=RequestContext(request))
    else:
        return render_to_response("notfound.html", views.createTemplateData(), context_instance=RequestContext(request))
    

@login_required
def edit(request, type, id_given):
    #TODO: add functionality
    types = {"area" : DBArea, "command" : DBCommand}
    return render_to_response("design_area.html", views.createTemplateData({"area": types[type].objects.get(id=id_given), "d_title_prefix" : "Edit"}), context_instance=RequestContext(request))

@login_required
def get_info(request, type, id):
    if type == "area":
        return render_to_response("response_area.xml", views.createTemplateData({"area": DBArea.objects.get(id=id)}), context_instance=RequestContext(request))
    else:
        return render_to_response("generic_response.xml", views.createTemplateData({"message" : "Something went wrong", "id" : id}), context_instance=RequestContext(request))

@login_required
def remove(request, type, id):
    if type == "area":
        area = DBArea.objects.get(id=int(id))
        if area.creator.id == request.user.id or request.user.is_superuser():
            area.delete()
            message = "Area deleted."
        else:
            message = "Permission denied."
            
        return render_to_response("generic_response.xml", views.createTemplateData({"message" : message}), context_instance=RequestContext(request))
    else:
        return render_to_response("generic_response.xml", views.createTemplateData({"error" : "Something went wrong"}), context_instance=RequestContext(request))

@login_required
def save(request, type):
    get_token(request)
    id = ""
    message = "Something went wrong."
    
    if request.method == "POST" and views.ENABLE_DESIGNER or request.user.is_superuser:
        json_data = simplejson.loads(request.raw_post_data)
        
        if type == "area":
            message, id = save_area(request.user, json_data)
        if type == "command":
            print str(json_data)
            print u.dictToXml("lreqs", json_data["list_reqs"])
                
    return render_to_response("generic_response.xml", views.createTemplateData({"message" : message, "id" : id}), context_instance=RequestContext(request))



