#!/usr/bin/env python3

from gi.repository import Gtk
from gtklib import ObjGetter
import numpy as np
import os

class Particle:
    def __init__(self, position, velocity, force, mass):
        self.position = position
        self.velocity = velocity
        self.force = force
        self.mass = mass


class DrawArea:
    def __init__(self, drawarea):
        self.drawarea = drawarea
        self.width = self.drawarea.get_allocation().get_width()
        self.height = self.drawarea.get_allocation().get_height()

    def draw(self, drawarea, cr):
        #TODO vykreslit kazdu strunu medzi casticami
        pass
    
    def resize(self, widget, allocation):
        tra = np.array([[self.width/allocation.get_width(), 0, 0],
                        [0, self.height/allocation.get_height(), 0],
                        [0, 0, 1]])
        #TODO presunut kazdu casticu a jej rychlost


class MainWindow(ObjGetter):
    def __init__(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.glade')
        ObjGetter.__init__(self, path, self.get_signals())
        self.darea = DrawArea(self.drawarea)
        self.window.show()

    def get_signals(self):
        signals = {"destroy" : Gtk.main_quit,
                   "forward" : self.forward,
                   "draw" : self.darea.draw,
                   "resize" : self.darea.resize}
        return signals

    def forward(self, button=None):
        #TODO
        pass


if __name__ == '__main__':
    win = MainWindow()
    Gtk.main()
