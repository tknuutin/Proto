'''
Created on Jan 8, 2013

@author: TarmoK
'''

from django.template import RequestContext
from views import createTemplateData
from utilities import wrapTags, wrapTagsWithInnerData
from django.contrib.auth.decorators import login_required
from proto.models import DBLocation, DBCondition, DBEvent, DBFeature

from django.shortcuts import render_to_response

class NullModule(object):
    def __init__(self):
        self.name = ""
        self.desc = ""
        self.ftdesc = ""
        self.id = 0
        self.adminname = ""
        
@login_required  
def location(request):
    if request.POST:
        pass
    return render_to_response("location.html", createTemplateData({"location": NullModule()}), context_instance=RequestContext(request))

@login_required
def editor_main(request):
    locations = DBLocation.objects.filter(creator=request.user)
    events = DBEvent.objects.filter(creator=request.user)
    features = DBFeature.objects.filter(creator=request.user)
    conditions = DBCondition.objects.filter(creator=request.user)
    return render_to_response("editor_main.html", createTemplateData({"locations": locations, "events" : events, "features" : features, "conditions" : conditions}), context_instance=RequestContext(request))