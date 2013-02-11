'''
Created on 2.7.2012

@author: Tarmo

'''

def validate_email(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

#Bunch of old convenience functions here!

def replaceBadToken(string):
    return string.replace("]]>", "BAD TOKEN")

def wrapTagsWithInnerData(tagname, innertext):
    return "<" + tagname + ">" + str(innertext) + "</" + tagname + ">"

def wrapTags(tagname, text):
    return "<" + tagname + "><![CDATA[" + replaceBadToken(str(text)) + "]]></" + tagname + ">"

class DummyU(object):
    id = "0"
    name = "none"
class DummyA(object):
    id = "0"
    created_by = DummyU()
    
def convertSingleElement(key, value):
    level = ""
    if type(value).__name__ == "dict":
        level += dictToXml(key, value)
    elif type(value).__name__ == "list":
        for x in value:
            level += convertSingleElement(key, x)
    else:
        level += wrapTags(key, value)
    return level
    
def dictToXml(topnode, d):
    level = ""
    for key, value in d.items():
        level += convertSingleElement(key, value)
        
    return wrapTagsWithInnerData(topnode, level)
    
def parseBool(bool_str):
    if bool_str.lower() == "true": return True
    else: return False
    

if __name__ == '__main__':
    pass
