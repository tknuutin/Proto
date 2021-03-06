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
    
    @classmethod
    def save_from_request(cls, request, fields, moduleid=None):
        raise NotImplementedError("Save method for class %d not implemented" % (cls.__name__))
    
    def publish(self):
        self.play_status = "PU"
        
    def unpublish(self):
        self.play_status = "UN"
        
    def verify(self):
        self.play_status = "VE"
    
    def is_editable(self, user):
        if (self.design_status == "AL" \
            or (self.design_status == "OW" \
                and user.id == self.creator.id)) \
        and not self.hidden \
        or user.is_superuser:
            return True
        else:
            return False
        
    def is_usable_in_editor(self, user):
        if (self.design_status == "AL" \
            or self.design_status == "OW") \
        and not self.hidden \
        or user.is_superuser:
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
        return self.adminname + " (has condition)" if self.condition else " (no condition)"
    
class DBSession(models.Model):
    started = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.started
    
class EventTriggered(models.Model):
    session = models.ForeignKey(DBSession)
    event = models.ForeignKey(DBEvent)
    
class DBFeature(DBGameModule):
    location = models.ForeignKey("DBLocation", related_name="features")
    name = models.CharField(max_length=512)
    desc = models.TextField()
    
    @classmethod
    def get_simple_name(cls): return "feature"
    
    @classmethod
    def save_from_request(cls, request, fields, moduleid=None):
        if DBLocation.objects.filter(id=fields["moduleid"]).exists():
            fields["location"] = DBLocation.objects.get(id=fields["moduleid"])
            del fields["moduleid"]
            
            if not cls.objects.filter(name=fields["name"], location=fields["location"]).exists() and not moduleid:
                newfeature = cls(**fields)
                newfeature.save()
                return True, "Succesfully created new Feature.", newfeature.id
            else:
                oldfeature = cls.objects.get(id=moduleid)
                if oldfeature.is_editable(request.user) and not cls.objects.filter(name=fields["name"], location=fields["location"]).exclude(id=moduleid).exists():
                    for field, value in fields.iteritems():
                        setattr(oldfeature, field, value)
                    
                    oldfeature.save()
                    return True, "Succesfully saved changes to Feature.", oldfeature.id
                else:
                    return False, "Feature with that name already exists for the specified module.", moduleid
        else:
            return False, "Attaching Module ID not found.", None
    
    def __unicode__(self):
        return self.location.adminname + ": " + self.name
    
class Alternative(DBGameModule):
    module = models.ForeignKey(DBGameModule, related_name="alternatives")
    altname = models.CharField(max_length=512)
    
class DBLocation(DBGameModule):
    name = models.CharField(max_length=512)
    desc = models.TextField()
    ftdesc = models.TextField(null=True, blank=True)
    
    @classmethod
    def get_simple_name(cls): return "location"
    
    def get_absolute_url(self):
        return "/proto/editor/location/" + str(self.id)
    
    def __unicode__(self):
        return self.name
    
    @classmethod
    def save_from_request(cls, request, fields, moduleid=None):
        if not cls.objects.filter(name=fields["name"], game=fields["game"]).exists() and not moduleid:
            newloc = cls(**fields)
            newloc.save()
            return True, "Succesfully created new Location.", newloc.id
        else:
            oldloc = cls.objects.get(id=moduleid)
            if oldloc.is_editable(request.user) and not cls.objects.filter(name=fields["name"], game=fields["game"]).exclude(id=moduleid).exists():
                for field, value in fields.iteritems():
                    setattr(oldloc, field, value)
                    
                conn_save_success, msg = Connection.save_from_request(request, oldloc)
                if not conn_save_success: return False, msg, oldloc.id
                conn_delete_success, msg = Connection.delete_from_request(request, oldloc)
                if not conn_delete_success: return False, msg, oldloc.id
                
                oldloc.save()
                return True, "Succesfully saved changes to Location.", oldloc.id
            else:
                return False, "Location with that name already exists for the specified game.", moduleid
    
class LocationVisited(models.Model):
    session = models.ForeignKey(DBSession)
    location = models.ForeignKey(DBLocation)
    
class Connection(models.Model):
    locfrom = models.ForeignKey(DBLocation, related_name="locationfrom")
    locto = models.ForeignKey(DBLocation, related_name="locationto")
    twoway = models.BooleanField(default=True)
    
    @classmethod
    def save_from_request(cls, request, locationfrom):
        counter = 1
        
        print "is nc_1 in post? " + str("nc_" + str(counter) in request.POST)
        while "nc_" + str(counter) in request.POST:
            loctoid = request.POST["nc_" + str(counter)]
            if DBLocation.objects.filter(id=loctoid).exists():
                if locationfrom.is_editable(request.user):
                    newconn = Connection(locfrom=locationfrom, locto=DBLocation.objects.get(id=loctoid))
                    newconn.save()
                    counter += 1
                else:
                    return False, "Not authorized to add a Connection here."
            else:
                return False, "Invalid Connection id."
        return True, ""
    
    @classmethod
    def delete_from_request(cls, request, locationfrom):
        counter = 1
        while "rc_" + str(counter) in request.POST:
            connid = request.POST["rc_" + str(counter)]
            if Connection.objects.filter(id=connid).exists():
                if locationfrom.is_editable(request.user):
                    Connection.objects.filter(id=connid).delete()
                    counter += 1
                else:
                    return False, "Not authorized to remove Connection."
            else:
                return False, "Invalid Connection id."
        return True, ""
    
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














