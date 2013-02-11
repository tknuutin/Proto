'''
Created on 8.4.2012

@author: Tarmo
'''

from itertools import chain
from lxml import etree
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from picklefield.fields import PickledObjectField
from django.utils.safestring import mark_safe

def validate_xml(xml):
    pass

def validate_requirement(xml):
    pass

def validate_outcome(xml):
    pass

def is_complex_desc(self, desc):
    if etree.fromstring(str(desc)).find("type").text == "complex": 
        return True
    else: 
        return False
def is_simple_desc(self, desc):
    if etree.fromstring(str(desc)).find("type").text == "simple": 
        return True
    else: 
        return False

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
    explorer_score = models.IntegerField(default=0, blank=False)
    designer_score = models.IntegerField(default=0, blank=False)

class DBGame(models.Model):
    creator = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=256)
    verify_creator_only = models.BooleanField(default=False)
    publish_creator_only = models.BooleanField(default=False)
    notes = models.TextField()

class DBGameModule(models.Model):
    game = models.ForeignKey(DBGame, blank=True, null=True)
    creator = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now=True)
    design_status = models.CharField(max_length=2, choices=EDIT_STATUS_CHOICES, default="OW")
    play_status = models.CharField(max_length=2, choices=PLAY_STATUS_CHOICES, default="UN")
    randomizable = models.BooleanField(default=False)
    dependencies = models.ManyToManyField("self", blank=True)
    notes = models.TextField()
    hidden = models.BooleanField(default=False)
    players_count = models.IntegerField(default=0, blank=False)
    
    def is_editable(self, user):
        if (self.design_status == "AL" \
            or (self.design_status == "OW" \
                and user.id == self.creator.id)) \
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

class Addition(models.Model):
    added_by = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now=True)
    order_num = models.IntegerField(blank=True, null=True)
    
class DBRequirement(DBGameModule):
    name = models.CharField(max_length=128)
    req_xml = models.TextField()
    
class DBOutcome(DBGameModule):
    name = models.CharField(max_length=128)
    outcome_reqs = models.ManyToManyField(DBRequirement, blank=True)
    outcome_xml = models.TextField()

class OutcomeAddition(Addition):
    added_to = models.ForeignKey(DBGameModule)
    a_outcome = models.ForeignKey(DBOutcome, related_name="added_outcomes")
    
class DBEvent(DBGameModule):
    name = models.CharField(max_length=128)
    singular = models.BooleanField(default=False)
    
class DBTransEvent(DBGameModule):
    area = models.ForeignKey("DBArea", related_name="trans_events", blank=True)
    type = models.CharField(max_length=5, choices=(("ENTER", "Event launched on entering an area"), ("EXIT", "Event launched on exiting an area")))
    exclusive = models.BooleanField(default=False)
    area_req = models.ForeignKey("DBArea", blank=True)
    chance = models.IntegerField()
    event = models.ForeignKey(DBEvent)
    
class DBCommand(DBGameModule):
    name = models.CharField(max_length=512)
    singular = models.BooleanField(default=False)
    type = models.CharField(max_length=128)
    list_reqs = models.ManyToManyField(DBRequirement, blank=True)
    randomize_outcome = models.BooleanField(default=False)
    
    def is_move_command(self):
        return False

#TODO: add shit here
class DBFeature(DBGameModule):
    name = models.CharField(max_length=512)
    randomize_outcome = models.BooleanField(default=False)
    ftype = models.CharField(max_length=8, choices=(("SIMPLE", "Simple description on examine"), ("COMPLEX", "Complex description on examine")))
    simple = models.TextField()
    
    def has_simple_desc(self):
        return True
    def get_simple_desc(self):
        return "Abadabadoo"
    def has_complex_desc(self):
        return False
    
    
class DBEntity(DBGameModule):
    pass

class DBDamageType(models.Model):
    owner = models.ForeignKey(DBGameModule)
    type = models.CharField(max_length=128)

class DBAttack(DBGameModule):
    damage = models.IntegerField()
    hits = models.IntegerField(default=1)
    hit_interval = models.IntegerField()
    
class DBNpcActivity(DBGameModule):
    angryOnly = models.BooleanField(default=False)
    interval = models.IntegerField()
    desc = models.CharField(max_length=128)
    activity_reqs = models.ManyToManyField(DBRequirement, blank=True)
    event = models.ForeignKey(DBEvent, blank=True)
    chance = models.IntegerField()
    
class DBNpc(DBEntity):
    name = models.CharField(max_length=128)
    desc = models.TextField()
    monster = models.BooleanField(default=False)
    angry_on_attack = models.BooleanField(default=False)
    health = models.IntegerField(default=25)
    corpse = models.ForeignKey("DBItem", blank=True)
    ondeath = models.ForeignKey(DBEvent, blank=True)
    
    #TODO: this
    def get_attributes(self):
        return "Lotsa attributes here"
    
class DBCondition(DBGameModule):
    name = models.CharField(max_length=128)
    visible = models.BooleanField()
    value_min = models.IntegerField()
    value_max = models.IntegerField()
    
class DBItem(DBEntity):
    name = models.CharField(max_length=128)
    size = models.IntegerField(default=15)
    desc = models.TextField()
    equip_type = models.CharField(max_length=128)
    throw_dmg = models.IntegerField()
    
    #TODO: this
    def get_attributes(self):
        return "Lotsa attributes here"
    
class DBThrowEffects(models.Model):
    item = models.ForeignKey(DBItem)
    damage = models.IntegerField()
    
class DBConsumeEffects(models.Model):
    item = models.ForeignKey(DBItem)
    heal = models.IntegerField()
    event = models.ForeignKey(DBEvent, blank=True)
    
class RequirementAddition(Addition):
    added_to = models.ForeignKey(DBGameModule)
    a_req = models.ForeignKey(DBRequirement, related_name="added_reqs")
    
class DBSpawn(DBGameModule):
    spawn_name = models.CharField(max_length=128)
    entity = models.ForeignKey(DBEntity)
    amount_min = models.IntegerField(default=1, null=True, blank=True)
    amount_max = models.IntegerField(default=1, null=True, blank=True)
    position = models.CharField(max_length=128, null=True, blank=True)
    
class FeatureAddition(Addition):
    a_area = models.ForeignKey("DBArea")
    a_feature = models.ForeignKey(DBFeature)

class CommandAddition(Addition):
    a_area = models.ForeignKey("DBArea")
    a_command = models.ForeignKey(DBCommand)
    
class SpawnAddition(Addition):
    a_area = models.ForeignKey("DBArea")
    type = models.CharField(max_length=2, choices=(("NP", "NPC"), ("IT", "Item")))
    a_spawn = models.ForeignKey(DBSpawn)
    
class DBArea(DBGameModule):
    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256, unique=True)
    fast_travel = models.BooleanField(default=False)
    first_desc_xml = models.TextField(null=True, blank=True)
    default_desc_xml = models.TextField()
    
    def item_spawns(self): return self.spawnaddition_set.filter(type="IT")
    def npc_spawns(self): return self.spawnaddition_set.filter(type="NP")
    def get_enter_events(self): return DBTransEvent.objects.filter(area=self, type="ENTER")
    def get_exit_events(self): return DBTransEvent.objects.filter(area=self, type="EXIT")
    
    #TODO: implement these
    def has_complex_ft_desc(self):
        return is_complex_desc(self.first_desc_xml)
    def has_simple_ft_desc(self):
        return is_simple_desc(self.first_desc_xml)
    def has_complex_def_desc(self):
        return is_complex_desc(self.default_desc_xml)
    def has_simple_def_desc(self):
        return is_simple_desc(self.default_desc_xml)
    
class DBAreaOverride(DBGameModule):
    area = models.ForeignKey(DBArea)
    override_requirement = models.OneToOneField(DBRequirement)
    
class DBCommandSequenceMember(models.Model):
    area = models.ForeignKey(DBArea)
    command = models.ForeignKey(DBCommand)
    next = models.ForeignKey("self", null=True, blank=True)

class NewsArticle(models.Model):
    text = models.TextField()
    title = models.CharField(max_length=512, unique=True)
    date = models.DateTimeField(auto_now=True)
    
    def get_article_html(self):
        return mark_safe(self.text)
    
class DBSavedGame(models.Model):
    user = models.ForeignKey(User)
    savename = models.CharField(max_length=128)
    playername = models.CharField(max_length=128)
    date = models.DateTimeField(auto_now=True)
    save_file = PickledObjectField()
    unverified = models.BooleanField()
    
    def __unicode__(self):
        return unicode(self.savename) + " : " + unicode(self.playername) + " : " + unicode(self.date)
    
    
    
