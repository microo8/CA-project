#!/usr/bin/env python3

from gi.repository import Gtk
from gtklib import ObjGetter
import numpy as np
import os, pickle

BONE_LENGTH = 30

class Particle:
    def __init__(self, parrent, position, mass):
        self.position = position
        self.velocity = np.array([0,0,0])
        self.mass = mass
        self.parrent = parrent
        if self.parrent is not None:
            self.parrent.descendants.append(self)
        self.descendants = []

class System:
    def __init__(self, alloc, filename=None):
        if filename is None:
            head = Particle(None, np.array([alloc.width/2, alloc.height/4,0]), 1)
            child = Particle(head, np.array([alloc.width/2, alloc.height/4+BONE_LENGTH,0]), 1)
            self.particles = [head, child]
        else:
            with open(filename) as f:
                self.particles = pickle.load(f)

    def __iter__(self):
        for part in self.particles:
            yield part

class DrawArea:
    def __init__(self):
        self.sys = None
        self.width = 1
        self.height = 1

    def set_drawarea(self, drawarea):
        self.drawarea = drawarea
        self.width = self.drawarea.get_allocation().width
        self.height = self.drawarea.get_allocation().height
        self.tra = np.eye(3)
        self.sys = System(self.drawarea.get_allocation())

    def draw(self, drawarea, cr):
        cr.set_source_rgb (0, 0, 0)
        if self.sys is not None:
            cr.set_line_width(2)
            for part in self.sys:
                if part.parrent is not None:
                    x, y = self.tra.dot(part.position)[:2]
                    cr.move_to(x, y)
                    x, y = self.tra.dot(part.parrent.position)[:2]
                    cr.line_to(x, y)
                    cr.close_path()
            cr.stroke()
            cr.set_source_rgb (0.8, 0, 0)
            for part in self.sys:
                x, y = self.tra.dot(part.position)[:2]
                cr.move_to(x,y)
                cr.arc(x, y, 5, 0, 2*np.pi);
            cr.fill()
    
    def resize(self, widget, allocation):
        self.tra = np.array([[allocation.width/self.width, 0, 0],
                             [0, allocation.height/self.height, 0],
                             [0, 0, 1]])


class MainWindow(ObjGetter):
    def __init__(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.glade')
        self.darea = DrawArea()
        ObjGetter.__init__(self, path, self.get_signals())
        self.window.show()
        self.darea.set_drawarea(self.drawarea)

    def get_signals(self):
        signals = {"destroy" : Gtk.main_quit,
                   "forward" : self.forward,
                   "draw" : self.darea.draw,
                   "resize" : self.darea.resize,
                   "about" : self.about}
        return signals

    def about(self, item):
        resp = self.aboutdialog.run()
        if resp == Gtk.ResponseType.DELETE_EVENT or resp == Gtk.ResponseType.CANCEL:
            self.aboutdialog.hide()

    def forward(self, button=None):
        #TODO
        pass


if __name__ == '__main__':
    win = MainWindow()
    Gtk.main()
