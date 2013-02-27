'''
Created on Dec 16, 2012

@author: TarmoK
'''
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from proto import models

class Condition(object):
    """ Game condition, basically an if-clause in the game script. """
    LARGER = 0
    SMALLER = 1
    LARGER_OR_EQUAL = 2
    SMALLER_OR_EQUAL = 3
    EQUAL = 4
    
    def __init__(self, variable, mode, other=None, number=None):
        self.variable = variable
        self.mode = mode
        self.other = other
        self.number = number
        
    def has_visited(self):
        """ Checks if the condition is a 'Location visited' type condition and if so, checks if the condition is true. """
        prefix = "HAS_VISITED_"
        if self.variable.startswith(prefix):
            locvisited = self.variable[:len(prefix)]
            hasvisited = models.LocationVisited.objects.filter(location=locvisited).exists()
            if hasvisited and self.mode == self.EQUAL and self.number == 1:
                return True
            elif not hasvisited and self.mode == self.EQUAL and self.number == 0:
                return True
        return False
        
    def passes(self, game):
        """ Checks whether condition passes. """
        if self.has_visited():
            return True
        elif game.has_variable(self.variable):
            value = game.get_variable(self.variable)
            if self.other and game.has_variable(self.other):
                other = game.get_variable(self.other)
            elif self.number != None:
                other = self.number
            else:
                return False
                
            if self.mode == self.LARGER:
                return value > other
            elif self.mode == self.SMALLER:
                return value < other
            elif self.mode == self.LARGER_OR_EQUAL:
                return value >= other
            elif self.mode == self.SMALLER_OR_EQUAL:
                return value <= other
            elif self.mode == self.EQUAL:
                return value == other
        else:
            return False

class Event(object):
    """ A generic game event. """
    MODE_NEW = 0
    MODE_ADD = 1
    MODE_SUBS = 2
    MODE_MULTI = 3
    
    def __init__(self, dbid, desc=None, condition=None, variable=None, new_variable_hidden=True, amount=None, mode=0, failevent=None):
        self.desc = desc
        self.variable = variable
        self.amount = amount
        self.mode = mode
        self.condition = condition
        self.new_variable_hidden = new_variable_hidden
        self.dbid = dbid
        self.failevent = failevent
        
    def has_triggered(self, session):
        """ Checks whether this Event has triggered for this game Session yet. """
        try:
            models.EventTriggered.objects.get(session__id=session.id, event__id=self.dbid)
            return True
        except ObjectDoesNotExist:
            return False
        
    def trigger(self, game):
        """ Trigger the effects of the Event to the Game object. """
        if self.has_triggered(game.session):
            return True
        elif not self.condition or self.condition.passes(game):
            if self.desc:
                game.send_text(self.desc)
            if self.variable:
                if self.mode == self.MODE_NEW:
                    game.set_variable(self.variable, self.amount, self.new_variable_hidden)
                elif self.mode == self.MODE_ADD:
                    game.add_to_variable(self.variable, self.amount)
                elif self.mode == self.MODE_SUBS:
                    game.subtract_from_variable(self.variable, self.amount)
                elif self.mode == self.MODE_MULTI:
                    game.multiply_variable(self.variable, self.amount)
            
            models.EventTriggered(session=game.session, event=models.DBEvent.objects.get(id=self.dbid)).save()
            return True
        else:
            if self.failevent: self.failevent.trigger()
            return False

class Feature(object):
    """ An object, item, or other attribute of a location or Feature. """
    def __init__(self, name):
        self.name = name
        self.events = []
        
    def set_description(self, desc):
        self.description = desc
        return self
    
    def add_event(self, event):
        self.events.append(event)
        return self
    
    def trigger(self, game, show_description=True):
        """ Trigger the effects of the feature. """
        if show_description:
            game.send_text(self.description)
        
        passed = []
        for event in self.events:
            if event.trigger(game): 
                passed.append(event)
        for event in passed:
            self.events.remove(event)

class Location(Feature):
    """ A location in game. """
    def __init__(self, name, dbid):
        Feature.__init__(self, name)
        self.features = {}
        self.connections = {}
        self.ftdesc = None
        self.dbid = dbid
        
    def add_ftdesc(self, desc):
        self.ftdesc = desc
        return self
        
    def add_connection(self, name, uid):
        self.connections[name.lower()] = uid
        return self
        
    def add_feature(self, feature):
        self.features[feature.name.lower()] = feature
        return self
        
    def trigger_location(self, game):
        """ Trigger location, for example when entering the area or loading game to area. """
        game.send_text("You are in " + self.name.upper() + ".")
        
        if models.LocationVisited.objects.filter(session__id=game.session.id, location__id=self.dbid).exists():
            self.trigger(game)
        else:
            game.send_text(self.ftdesc)
            models.LocationVisited(session=game.session, location=models.DBLocation.objects.get(id=self.dbid)).save()
            self.trigger(game, show_description=False)
        
        connectionnames = [connection.upper() for connection in self.connections.iterkeys()]
        if len(connectionnames) == 1:
            game.send_text("You can go to %s." % (connectionnames[0]))
        elif len(connectionnames) > 1:
            game.send_text("You can go to %s or %s." % (", ".join(connectionnames[:(len(connectionnames)-1)]), connectionnames[-1]))

class DBInterface(object):
    """ Database interface controller. """
    def __init__(self, user=None):
        self.verified_only = (not bool(models.UserProfile.objects.get(user=user).filtermode)) if user else True
        self.user = user
        
    def filter_by_play_status(self, results):
        if self.verified_only: 
            results.filter(play_status__exact="VE")
        else:
            results.filter(Q(play_status__exact="VE") | Q(play_status__exact="PU"))
        return results
    
    def get_condition(self, uid=None, dbobject=None):
        dbcondition = dbobject or models.DBCondition.objects.get(id=uid)
        return Condition(dbcondition.variable, dbcondition.mode, other=dbcondition.other, number=dbcondition.number)
    
    def get_event(self, uid=None, dbobject=None):
        dbevent = dbobject or models.DBEvent.objects.get(id=uid)
        
        if dbevent.condition:
            cond = self.get_condition(dbobject=dbevent.condition)
        else:
            cond = None
        
        return Event(dbevent.id, failevent=dbevent.failevent, desc=dbevent.desc, variable=dbevent.variable, amount=dbevent.amount, mode=dbevent.mode, new_variable_hidden=dbevent.new_variable_hidden, condition=cond)
        
    def get_feature(self, uid=None, dbobject=None):
        dbfeat = dbobject or models.DBFeature.objects.get(id=uid)
        feat = Feature(dbfeat.name).set_description(dbfeat.desc)
        
        for dbevent in self.filter_by_play_status(models.DBEvent.objects.filter(module__id=dbfeat.id)):
            feat.add_event(self.get_event(dbobject=dbevent))
            
        return feat
        
    def get_location(self, uid=None, dbobject=None):
        dbloc = dbobject or models.DBLocation.objects.get(id=uid)
        loc = Location(dbloc.name, dbloc.id).set_description(dbloc.desc).add_ftdesc(dbloc.ftdesc)
        
        for dbevent in self.filter_by_play_status(models.DBEvent.objects.filter(featureowner__id=dbloc.id)):
            loc.add_event(self.get_event(dbobject=dbevent))
        
        dbconns = models.Connection.objects.filter(Q(locfrom__id=dbloc.id) | Q(locto__id=dbloc.id))
        if self.verified_only:
            dbconns = dbconns.filter(locfrom__play_status__exact="VE")
        else:
            dbconns = dbconns.filter(Q(locfrom__play_status__exact="VE") | Q(locfrom__play_status__exact="PU"))
        
        for dbconnection in dbconns:
            if dbloc.id == dbconnection.locfrom.id:
                loc.add_connection(dbconnection.locto.name, dbconnection.locto.id)
            else:
                loc.add_connection(dbconnection.locfrom.name, dbconnection.locfrom.id)
                
        for dbfeature in self.filter_by_play_status(models.DBFeature.objects.filter(featureowner__id=dbloc.id)):
            loc.add_feature(self.get_feature(dbobject=dbfeature))
            
        return loc
        
class Game(object):
    """ """
    def __init__(self, name, session, user=None):
        self.playername = name
        self.session = session
        self.user = user
        self.text_buffer = []
        self.variables = {}
        self.current_location = None
        self.db = DBInterface(user=user)
        
    def default_start(self):
        self.text_buffer.append("You decide your name is " + self.playername.upper() + ". A rather stupid name, but that's the one you chose. No point berating yourself about it a second after you come up with it.")
        self.text_buffer.append("You look around.")
        
        start = self.db.get_location(1)
        
        self.current_location = start
        self.current_location.trigger_location(self)
        return self.pop_buffer()
    
    def pop_buffer(self):
        #TODO: remove debug print
        #print "current variables: " + str(self.variables)
        returnable = self.text_buffer
        self.text_buffer = []   
        return returnable
    
    def examine(self, command):
        target = command.lower()[8:]
        if target.lower() in self.current_location.features:
            self.current_location.features[target].trigger(self)
        else:
            self.send_text("It is barely worth mentioning, so I won't waste anyone's time by describing it.")
    
    def move(self, command):
        goto = command.lower()[6:]
        if goto.lower() in self.current_location.connections:
            self.current_location = self.db.get_location(self.current_location.connections[goto])
            
            self.current_location.trigger_location(self)
        else:
            self.send_text("You can't go there.")
    
    def send_command(self, command):
        if command.lower().startswith("go to "):
            self.move(command)
        elif command.lower().startswith("examine "):
            self.examine(command)
        else:
            self.send_text("Doing that doesn't seem like a good idea to you.")
                
        return self.pop_buffer()
    
    def send_text(self, text):
        self.text_buffer.append(text)
        
    def set_variable(self, variable, value, hidden):
        if variable not in self.variables:
            self.variables[variable] = {"value" : value, "hidden" : hidden}
            if not hidden:
                self.send_text("You have gained the stat %s!" % variable.upper())
        else:
            self.variables[variable]["value"] = value
            
    def add_to_variable(self, variable, add):
        if variable in self.variables:
            self.variables[variable]["value"] = self.variables[variable] + add
            
    def subtract_from_variable(self, variable, subtract):
        if variable in self.variables:
            self.variables[variable]["value"] = self.variables[variable] - subtract
            
    def multiply_variable(self, variable, amount):
        if variable in self.variables:
            self.variables[variable]["value"] = self.variables[variable] * amount

class ConsoleView(object):
    """ Debug view for console interface. """
    def __init__(self, game):
        self.game = game
    def send_command(self, command):
        for line in self.game.send_command(command):
            print line
    def default_start(self):
        for line in self.game.default_start():
            print line

if __name__ == "__main__":
    
    game = Game(raw_input("What is thine name? > "))
    view = ConsoleView(game)
    view.default_start()
    
    while True:
        view.send_command(raw_input("Giev command > "))
