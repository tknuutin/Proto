'''
Created on 15.7.2012

@author: Tarmo
'''

items = {"a" : False, "b" : True, "c" : False}
keys = items.keys()
logic_words = ["or", "and", "not"]

def check_proposition(key1, connector, key2, inverse1=False, inverse2=False):
    if connector == "AND":
        if inverse: return not (items[key1] and items[key2])
        else: return (items[key1] and items[key2])
    else:
        if inverse: return not (items[key1] or items[key2])
        else: return (items[key1] or items[key2])
        
def check_all(words):
    position = 0
    key1 = ""
    key2 = ""
    inverse1 = False
    inverse2 = False
    connector = ""
    word1 = words[position]
    
    while word == "not":
        inverse = not inverse
        position += 1
    
    key = words[position]

def check_order_of_words(words):
    if words[0] not in keys + ["not"]:
        return False
    
    lastword = ""
    for word in words:
        if word == "or" or word == "and":
            if lastword == "or" or lastword == "and":
                return False
        lastword = word
    if lastword in keys: return True
    else: return False

def check_false_words(words):
    false_words = [x for x in words if x not in (keys + logic_words)]
    if false_words:
        print false_words
        return False
    else:
        return True

def parse_logic(line):
    words = line.lower().split()
    if not check_false_words(words):
        return False
    if not check_order_of_words(words):
        return False
    
    return True

def main():
    line = ""
    while line is not "q":
        print "Giev prop logic"
        line = raw_input()
        if parse_logic(line) == False:
            print "you dun fucked up"
        else:
            print "all clear"
    print "quitting dis shit"

if __name__ == '__main__':
    main()
