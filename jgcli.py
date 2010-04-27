from pymongo import Connection
connection = Connection("192.168.0.20", 27017)

db = connection["jgpos"]
produkte = db["produkte"]
inventar = db["inventar"]

def handle(inp):
    if inp == "q":
        return False
    elif inp == "add_produkt":
        name = raw_input("Name: ")
        pos = raw_input("POS: ")
        ok = raw_input("insert? ")
        if ok == "" or ok == "y" or ok == "yes":
            produkte.insert({"name":name, "pos":pos})
    elif inp == "list_produkte":
        print "+----------+------------------------------+"
        for p in produkte.find():
            print "|%(pos)-10s|%(name)-30s|" % p
        print "+----------+------------------------------+"
    elif inp == "del_produkt":
        pos = raw_input("POS: ")
        ok = raw_input("del? ")
        if ok == "" or ok == "y" or ok == "yes":
            produkte.remove({"pos":pos})
    elif inp == "add_inventar":
        pos = raw_input("POS: ")
        p = produkte.find_one({"pos": pos})
        if not p:
            print "POS not in list"
            return True
        count = raw_input("Count: ")
        location = raw_input("Location: ")
        ok = raw_input("insert? ")
        if ok == "" or ok == "y" or ok == "yes":
            inventar.insert({"produkt":p["_id"], "anzahl":count, "ort":location})
    elif inp == "list_inventar":
        print "+----------+------------------------------+-----+--------------------+"
        for i in inventar.find():
            p = produkte.find_one({"_id": i["produkt"]})
            i["name"] = p["name"]
            i["pos"] = p["pos"]
            print "|%(pos)-10s|%(name)-30s|%(anzahl)-5s|%(ort)-20s|" % i
        print "+----------+------------------------------+-----+--------------------+"
    return True

exit = False

import sys
try:
    handle(sys.argv[1])
    exit = True
except:
    pass

while not exit:
    i = raw_input("> ")
    exit = not handle(i)
