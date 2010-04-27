#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from pymongo import Connection
connection = Connection("192.168.0.20", 27017)

db = connection["jgpos"]
inventar = db["inventar"]
produkte = db["produkte"]

class MainWindow:
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Inventar")
        self.produkteWindow = ProdukteWindow()
        self.bestandHinzufuegenWindow = BestandHinzufuegenWindow(self.holeDaten)
    
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)

        self.view = gtk.TreeView(model=None)
        col1 = gtk.TreeViewColumn("POS", gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=1)
        col3 = gtk.TreeViewColumn("Anzahl", gtk.CellRendererText(), text=2)
        col4 = gtk.TreeViewColumn("Ort", gtk.CellRendererText(), text=3)
        col1.set_min_width(100)
        col2.set_min_width(200)
        col3.set_min_width(50)
        col4.set_min_width(100)
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.view.append_column(col1)
        self.view.append_column(col2)
        self.view.append_column(col3)
        self.view.append_column(col4)

        self.holeDaten()
        
        self.view.set_model(self.model)
    
        self.produkteButton = gtk.Button("Produkte")
        self.neuButton = gtk.Button("Hinzufügen")
    
        self.produkteButton.connect("clicked", self.zeigeProdukte, None)
        self.neuButton.connect("clicked", self.bestandHinzufuegen, None)

        self.layout = gtk.VBox()
        self.buttonBox = gtk.HBox()
        self.window.add(self.layout)
        
        self.layout.add(self.view)
        self.layout.add(self.buttonBox)
        self.buttonBox.add(self.produkteButton)
        self.buttonBox.add(self.neuButton)

        self.layout.show()
        self.buttonBox.show()
        self.produkteButton.show()
        self.neuButton.show()
        self.view.show()
        self.window.show()

    def holeDaten(self):
        self.model.clear()
        for i in inventar.find():
            p = produkte.find_one({"_id": i["produkt"]})
            self.model.append((p["pos"], p["name"], i["anzahl"], i["ort"]))
    
    def zeigeProdukte(self, widget, data=None):
        self.produkteWindow.window.show()
        self.produkteWindow.holeDaten()

    def bestandHinzufuegen(self, widget, data=None):
        self.bestandHinzufuegenWindow.window.show()
        self.bestandHinzufuegenWindow.holeDaten()
    
    def main(self):
        gtk.main()

class ProdukteWindow:
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        return True

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Produkte")
    
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)

        self.view = gtk.TreeView(model=None)
        col1 = gtk.TreeViewColumn("POS", gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=1)
        col1.set_min_width(100)
        col2.set_min_width(200)
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.view.append_column(col1)
        self.view.append_column(col2)
        
        self.view.set_model(self.model)
        self.view.show()

        self.neuButton = gtk.Button("Hinzufügen")

        self.layout = gtk.VBox()
        self.buttonBox = gtk.HBox()
        self.window.add(self.layout)
        
        self.layout.add(self.view)
        self.layout.add(self.buttonBox)
        self.buttonBox.add(self.neuButton)

        self.layout.show()
        self.buttonBox.show()
        self.neuButton.show()

    def holeDaten(self):
        self.model.clear()
        for p in produkte.find():
            self.model.append((p["pos"], p["name"]))

class BestandHinzufuegenWindow:
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        return True

    def __init__(self, fertig):
        self.fertig = fertig
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Bestand Hinzufügen")
    
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)

        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.produkt = gtk.ComboBox(self.model)
        cell = gtk.CellRendererText()
        self.produkt.pack_start(cell, True)
        self.produkt.add_attribute(cell, 'text', 1)

        
        self.anzahl = gtk.Entry()
        self.ort = gtk.Entry()

        self.layout = gtk.Table(4, 2)

        self.label1 = gtk.Label("Produkt")
        self.label2 = gtk.Label("Anzahl")
        self.label3 = gtk.Label("Ort")

        self.speichern = gtk.Button("Speichern")
        self.speichern.connect("clicked", self.datenSpeichern, None)
        
        self.layout.attach(self.label1,  0, 1, 0, 1)
        self.layout.attach(self.label2,  0, 1, 1, 2)
        self.layout.attach(self.label3,  0, 1, 2, 3)
        self.layout.attach(self.produkt, 1, 2, 0, 1)
        self.layout.attach(self.anzahl,  1, 2, 1, 2)
        self.layout.attach(self.ort,     1, 2, 2, 3)
        self.layout.attach(self.speichern, 1, 2, 3, 4)

        self.window.add(self.layout)
        
        self.produkt.show()
        self.anzahl.show()
        self.ort.show()
        self.label1.show()
        self.label2.show()
        self.label3.show()
        self.speichern.show()
        self.layout.show()

    def holeDaten(self):
        self.model.clear()
        for p in produkte.find():
            self.model.append((p["pos"], p["name"]))

    def datenSpeichern(self, widget, data=None):
        p = produkte.find_one({"pos": self.model.get_value(self.produkt.get_active_iter(), 0)})
        inventar.insert({"produkt": p["_id"], "anzahl": self.anzahl.get_text(), "ort": self.ort.get_text()})
        self.window.hide()
        self.fertig()

if __name__ == "__main__":
    mainWindow = MainWindow()
    mainWindow.main()

