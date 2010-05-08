#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from pymongo import Connection

inventar = None
produkte = None

from time import sleep

class Main():
    def __init__(self):
        self.app = QApplication(sys.argv)

    def run(self):
        sys.exit(self.app.exec_())

    def setup(self):
        global inventar, produkte
        splash = QSplashScreen(QPixmap("lager.jpg"))
        splash.show()
        sleep(0.1)
        splash.showMessage("mit Datenbank verbinden...")
        self.app.processEvents()
        sleep(0.2)
        try:
            connection = Connection("192.168.0.20", 27017)
        except:
            splash.showMessage("Verbindung fehlgeschlagen!")
            self.app.processEvents()
            box = QMessageBox()
            box.setText("Verbindung fehlgeschlagen!")
            box.exec_()
            sys.exit()

        db = connection["jgpos"]
        inventar = db["inventar"]
        produkte = db["produkte"]
        self.w = MainWindow()
        self.w.show()
        splash.finish(self.w)

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Bestand")
        self.resize(850,500)

        self.setLayout(QGridLayout())
        layout = self.layout()

        self.inventar = Inventar(self)
        self.inventar.refresh()
        layout.addWidget(self.inventar, 0, 0, 1, 2)

        self.bestandAendern = InventarAendern(self)
        self.produkte = ProdukteWindow()
        
        self.addButton = QPushButton(u"Hinzufügen")
        self.addButton.connect(self.addButton, SIGNAL("clicked()"), self.bestandAendern.neu)
        
        self.produktButton = QPushButton("Produkte")
        self.produktButton.connect(self.produktButton, SIGNAL("clicked()"), self.produkte.show)
        
        layout.addWidget(self.addButton, 1, 0)
        layout.addWidget(self.produktButton, 1, 1)

    def closeEvent(self, event):
        self.bestandAendern.close()
        self.produkte.close()
        event.accept()

class Inventar(QTreeWidget):
    def __init__(self, main):
        QTreeWidget.__init__(self)
        self.main = main
        
        self.setColumnCount(4)
        self.setHeaderLabels(("POS", "Produkt", "Anzahl", "Ort"))
        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 200)
        self.setColumnWidth(2, 50)
        self.setColumnWidth(3, 100)

        self.connect(self, SIGNAL("itemDoubleClicked(QTreeWidgetItem *, int)"), self.doubleClicked)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"), self.context)
        self.contextMenu = QMenu()
        removeAction = QAction("Entfernen", self.contextMenu)
        self.contextMenu.addAction(removeAction)
        self.connect(removeAction, SIGNAL("triggered()"), self.remove)

    def refresh(self):
        self.clear()
        root = self.invisibleRootItem()
        for i in inventar.find():
            p = produkte.find_one({"_id": i["produkt"]})
            c = QTreeWidgetItem([p["pos"], p["name"], i["anzahl"], i["ort"]])
            c.setData(0, Qt.UserRole, QVariant(i["_id"]))
            root.addChild(c)
        self.sortItems(0, Qt.AscendingOrder)

    def doubleClicked(self, item, column):
        iid = item.data(0, Qt.UserRole).toPyObject()
        self.main.bestandAendern.edit(iid)

    def context(self, pos):
        globalPos = self.mapToGlobal(pos)
        i = self.itemAt(pos)
        if not i:
            return
        i.setSelected(True)
        self.contextMenu.exec_(globalPos)

    def remove(self):
        for item in self.selectedItems():
            iid = item.data(0, Qt.UserRole).toPyObject()
            inventar.remove({"_id": iid})
            self.refresh()

class ProduktAuswahl(QComboBox):
    def __init__(self):
        QComboBox.__init__(self)

    def refresh(self):
        self.clear()
        for p in produkte.find():
            self.addItem(p["name"], QVariant(p["pos"]))

    def setPOS(self, pos):
        index = self.findData(pos)
        self.setCurrentIndex(index)

class InventarAendern(QWidget):
    def __init__(self, main):
        QWidget.__init__(self)
        self.main = main
        self.iid = None
        
        self.setLayout(QGridLayout())
        layout = self.layout()

        self.auswahl = ProduktAuswahl()
        self.auswahl.refresh()

        self.anzahl = QSpinBox()

        self.ort = QLineEdit()
        
        layout.addWidget(QLabel("Produkt"), 0, 0)
        layout.addWidget(QLabel("Anzahl"), 1, 0)
        layout.addWidget(QLabel("Ort"), 2, 0)

        layout.addWidget(self.auswahl, 0, 1)
        layout.addWidget(self.anzahl, 1, 1)
        layout.addWidget(self.ort, 2, 1)

        self.speichern = QPushButton("Speichern")
        layout.addWidget(self.speichern, 3, 1)

    def neu(self):
        self.setWindowTitle(u"Bestand Hinzufügen")
        self.iid = None
        self.anzahl.setValue(1)
        #self.ort.setText("")
        self.auswahl.refresh()
        self.connect(self.speichern, SIGNAL("clicked()"), self.append)
        self.show()

    def edit(self, iid):
        self.setWindowTitle(u"Bestand Ändern")
        i = inventar.find_one({"_id": iid})
        self.anzahl.setValue(int(i["anzahl"]))
        self.ort.setText(i["ort"])
        self.auswahl.refresh()
        p = produkte.find_one({"_id": i["produkt"]})
        self.auswahl.setPOS(p["pos"])
        self.iid = iid
        self.connect(self.speichern, SIGNAL("clicked()"), self.save)
        self.show()

    def append(self):
        p = produkte.find_one({"pos": str(self.auswahl.itemData(self.auswahl.currentIndex()).toString())})
        inventar.insert({"produkt": p["_id"], "anzahl": str(self.anzahl.value()), "ort": str(self.ort.text())})
        self.main.inventar.refresh()
        self.disconnect(self.speichern, SIGNAL("clicked()"), self.append)
        self.neu()

    def save(self):
        p = produkte.find_one({"pos": str(self.auswahl.itemData(self.auswahl.currentIndex()).toString())})
        inventar.update({"_id": self.iid}, {"produkt": p["_id"], "anzahl": str(self.anzahl.value()), "ort": str(self.ort.text())})
        self.iid = None
        self.main.inventar.refresh()
        self.disconnect(self.speichern, SIGNAL("clicked()"), self.save)
        self.hide()

class ProdukteWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Produkte")
        self.resize(400,300)

        self.setLayout(QGridLayout())
        layout = self.layout()

        self.produkte = Produkte()
        self.produkte.refresh()
        layout.addWidget(self.produkte, 0, 0)

        self.produkteAendern = ProdukteAendern(self)
        
        self.addButton = QPushButton(u"Hinzufügen")
        self.addButton.connect(self.addButton, SIGNAL("clicked()"), self.produkteAendern.neu)
        
        layout.addWidget(self.addButton, 1, 0)

    def closeEvent(self, event):
        self.produkteAendern.close()
        event.accept()

class ProdukteAendern(QWidget):
    def __init__(self, main):
        QWidget.__init__(self)
        self.main = main
        self.pid = None
        
        self.setLayout(QGridLayout())
        layout = self.layout()

        self.pos = QLineEdit()
        self.name = QLineEdit()
        
        layout.addWidget(QLabel("POS"), 0, 0)
        layout.addWidget(QLabel("Name"), 1, 0)

        layout.addWidget(self.pos, 0, 1)
        layout.addWidget(self.name, 1, 1)

        self.speichern = QPushButton("Speichern")
        layout.addWidget(self.speichern, 2, 1)

    def neu(self):
        self.setWindowTitle(u"Produkt Hinzufügen")
        self.iid = None
        self.pos.setText("")
        self.name.setText("")
        self.connect(self.speichern, SIGNAL("clicked()"), self.append)
        self.show()

    def append(self):
        produkte.insert({"pos": str(self.pos.text()), "name": str(self.name.text())})
        self.main.produkte.refresh()
        self.disconnect(self.speichern, SIGNAL("clicked()"), self.append)
        self.neu()

    def edit(self, iid):
        self.setWindowTitle(u"Produkt Ändern")
        p = produkte.find_one({"_id": iid})
        self.pos.setText(p["pos"])
        self.name.setText(p["name"])
        self.pid = pid
        self.connect(self.speichern, SIGNAL("clicked()"), self.save)
        self.show()

    def save(self):
        produkte.insert({"_id": self.pid}, {"pos": str(self.pos.text()), "name": str(self.name.text())})
        self.iid = None
        self.main.produkte.refresh()
        self.disconnect(self.speichern, SIGNAL("clicked()"), self.save)
        self.hide()

class Produkte(QTreeWidget):
    def __init__(self):
        QTreeWidget.__init__(self)

        self.setColumnCount(2)
        self.setHeaderLabels(("POS", "Name"))
        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 200)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"), self.context)
        self.contextMenu = QMenu()
        removeAction = QAction("Entfernen", self.contextMenu)
        self.contextMenu.addAction(removeAction)
        self.connect(removeAction, SIGNAL("triggered()"), self.remove)

    def refresh(self):
        self.clear()
        root = self.invisibleRootItem()
        for p in produkte.find():
            c = QTreeWidgetItem([p["pos"], p["name"]])
            c.setData(0, Qt.UserRole, QVariant(p["_id"]))
            root.addChild(c)
        self.sortItems(0, Qt.AscendingOrder)

    def doubleClicked(self, item, column):
        pid = item.data(0, Qt.UserRole).toPyObject()
        self.main.produkteAendern.edit(pid)

    def context(self, pos):
        globalPos = self.mapToGlobal(pos)
        i = self.itemAt(pos)
        if not i:
            return
        i.setSelected(True)
        self.contextMenu.exec_(globalPos)

    def remove(self):
        for item in self.selectedItems():
            pid = item.data(0, Qt.UserRole).toPyObject()
            produkte.remove({"_id": pid})
            self.refresh()

if __name__ == "__main__":
    app = Main()
    app.setup()
    app.run()
