'''
Created on Dec 27, 2012

@author: TarmoK
'''

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

EDIT_STATUS_CHOICES = (
                              ("AL", "Editable"),
                              ("OW", "Owner only"),
                              ("NO", "Superuser only"),
                              ("PR", "Processing"),
                              ("RM", "Removed")
                        )

PLAY_STATUS_CHOICES = (
                              ("VE", "Verified"),
                              ("PU", "Published"),
                              ("UN", "Unpublished"),
                              ("HO", "On hold"),
                              ("PR", "Processing"),
                              ("RM", "Removed")
                        )

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    premium = models.BooleanField(default=False, blank=False)
    disabled = models.BooleanField(default=False, blank=False)
    filtermode = models.IntegerField(default=0, blank=False)
    explorer_score = models.IntegerField(default=0, blank=False)
    designer_score = models.IntegerField(default=0, blank=False)
    
    def __unicode__(self):
        return self.user.username

class DBGame(models.Model):
    creator = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=256)
    verify_creator_only = models.BooleanField(default=False)
    publish_creator_only = models.BooleanField(default=False)
    notes = models.TextField()
    
    def __unicode__(self):
        return self.name

class DBGameModule(models.Model):
    adminname = models.CharField(max_length=126, blank=True, null=True)
    game = models.ForeignKey(DBGame, blank=True, null=True)
    creator = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now=True)
    design_status = models.CharField(max_length=2, choices=EDIT_STATUS_CHOICES, default="OW")
    play_status = models.CharField(max_length=2, choices=PLAY_STATUS_CHOICES, default="UN")
    randomizable = models.BooleanField(default=False)
    notes = models.TextField()
    hidden = models.BooleanField(default=False)
    players_count = models.IntegerField(default=0, blank=False)
    
    def is_editable(self, user):
        if (self.design_status == "AL" \
            or (self.design_status == "OW" \
                and user.id == self.creator.id)) \
        and not self.hidden \
        or user.is_superuser:
            print user.is_superuser
            print self.design_status
            print self.creator.id, user.id
            return True
        else:
            return False
        
    def is_playable(self, settings=None):
        #TODO: settings
        if self.play_status == "VE" or self.play_status == "PU":
            return True
        else:
            return False
    
    def get_design_status(self):
        for key, value in EDIT_STATUS_CHOICES:
            if self.design_status == key: return value
        return "Error"
    
    def get_play_status(self):
        for key, value in PLAY_STATUS_CHOICES:
            if self.play_status == key: return value
        return "Error"
    
    def __unicode__(self):
        return unicode(self.adminname)
    
    def getUnicode(self):
        return self.__unicode__()

class DBCondition(DBGameModule):
    variable = models.CharField(max_length=256)
    mode = models.IntegerField()
    other = models.CharField(max_length=256, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return self.variable + " " + ("<", "<=", ">=", ">=", "=")[self.mode] + str(self.number or self.other)
    
class DBEvent(DBGameModule):
    module = models.ForeignKey(DBGameModule, related_name="eventowner")
    desc = models.TextField()
    variable = models.CharField(max_length=256, null=True, blank=True)
    mode = models.IntegerField(null=True, blank=True)
    amount = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    new_variable_hidden = models.NullBooleanField(null=True, blank=True)
    condition = models.ForeignKey(DBCondition, null=True, blank=True, related_name="eventcondition")
    failevent = models.ForeignKey("DBEvent", null=True, blank=True, related_name="failowner")
    
    def __unicode__(self):
        return self.adminname + " (has condition)" if self.condition else "(no condition)"
    
class DBSession(models.Model):
    started = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.started
    
class EventTriggered(models.Model):
    session = models.ForeignKey(DBSession)
    event = models.ForeignKey(DBEvent)
    
class DBFeature(DBGameModule):
    module = models.ForeignKey(DBGameModule, related_name="featureowner")
    name = models.CharField(max_length=512)
    desc = models.TextField()
    
    def __unicode__(self):
        return self.module.adminname + ": " + self.name
    
class Alternative(DBGameModule):
    module = models.ForeignKey(DBGameModule, related_name="altowner")
    altname = models.CharField(max_length=512)
    
class DBLocation(DBGameModule):
    name = models.CharField(max_length=512)
    desc = models.TextField()
    ftdesc = models.TextField(null=True, blank=True)
    
    def get_absolute_url(self):
        return "/proto/editor/location/" + str(self.id)
    
    def __unicode__(self):
        return self.name
    
class LocationVisited(models.Model):
    session = models.ForeignKey(DBSession)
    location = models.ForeignKey(DBLocation)
    
class Connection(models.Model):
    locfrom = models.ForeignKey(DBLocation, related_name="locationfrom")
    locto = models.ForeignKey(DBLocation, related_name="locationto")
    twoway = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.locfrom.name + " to " + self.locto.name + " (twoway)" if self.twoway else ""


admin.site.register(UserProfile)
admin.site.register(DBGame)
admin.site.register(DBGameModule)
admin.site.register(DBCondition)
admin.site.register(DBEvent)
admin.site.register(DBFeature)
admin.site.register(DBLocation)
admin.site.register(Connection)














