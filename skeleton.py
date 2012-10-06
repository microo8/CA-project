#!/usr/bin/env python3

from gi.repository import Gtk, Gdk
from gtklib import ObjGetter
import numpy as np
import os, pickle

BONE_LENGTH = 30
PARTICLE_SIZE = 5

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

    def rotate_particles(self, part, rot, center):
        tmp = part.position - center
        part.position = rot.dot(tmp) + center
        for desc in part.descendants:
            self.rotate_particles(desc, rot, center)


class DrawArea:
    def __init__(self):
        self.sys = None
        self.width = 1
        self.height = 1
        self.pressed1 = False
        self.pressed2 = False
        self.selected_particle = None
        self.selected_particle2 = None

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
            for part in self.sys:
                x, y = self.tra.dot(part.position)[:2]
                if part is self.selected_particle:
                    cr.set_source_rgb (0, 0.75, 0)
                    cr.move_to(x,y)
                    cr.arc(x, y, PARTICLE_SIZE+3, 0, 2*np.pi);
                    cr.fill()
                cr.set_source_rgb (0.75, 0, 0)
                cr.move_to(x,y)
                print(self.pressed2)
                cr.arc(x, y, PARTICLE_SIZE, 0, 2*np.pi);
                cr.fill()
    
    def resize(self, widget, allocation):
        self.tra = np.array([[allocation.width/self.width, 0, 0],
                             [0, allocation.height/self.height, 0],
                             [0, 0, 1]])

    def press(self, eventbox, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 3:
                self.pressed2 = True
            elif event.button == 1: 
                self.pressed1 = True
                if self.sys is not None:
                    pos = np.array([event.x, event.y, 0])
                    if self.selected_particle is None:
                        for part in self.sys:
                            if np.linalg.norm(self.tra.dot(part.position) - pos) <= PARTICLE_SIZE:
                                self.selected_particle = part
                                break
                    else:
                        for part in self.sys:
                            if np.linalg.norm(self.tra.dot(part.position) - pos) <= PARTICLE_SIZE and part in self.selected_particle.descendants:
                                self.selected_particle2 = part
                                break
                        else:
                            self.selected_particle = None
                            self.selected_particle2 = None
                self.drawarea.queue_draw()

    def release(self, eventbox, event):
        if event.type == Gdk.EventType.BUTTON_RELEASE:
            if event.button == 3:
                if self.pressed2 and self.selected_particle is not None:
                    inv_tra = np.linalg.inv(self.tra)
                    pos = inv_tra.dot(np.array([event.x, event.y, 0]))
                    pos -= self.selected_particle.position
                    pos /= np.linalg.norm(pos)
                    pos *= BONE_LENGTH
                    part = Particle(self.selected_particle, self.selected_particle.position + pos, 1)
                    self.sys.particles.append(part)
                    self.drawarea.queue_draw()
                self.pressed2 = False
            elif event.button == 1: 
                self.pressed1 = False
                self.selected_particle2 = None

    def motion(self, eventbox, event):
        if self.pressed1 and self.selected_particle is not None and self.selected_particle2 is not None:
            inv_tra = np.linalg.inv(self.tra)
            pos = inv_tra.dot(np.array([event.x, event.y, 0]))
            root_pos = self.selected_particle.position - pos
            root_part2 = self.selected_particle.position - self.selected_particle2.position
            root_pos /= np.linalg.norm(root_pos)
            root_part2 /= np.linalg.norm(root_part2)
            cos_phi = root_part2.dot(root_pos)
            sin_phi = np.sqrt(1-cos_phi**2)
            x1, y1, _ = root_part2
            x2, y2, _ = root_pos
            rot = None
            if (x2-x1)*(y2+y1) < 0:
                rot = np.array([[cos_phi, -sin_phi, 0],
                                [sin_phi, cos_phi,  0],
                                [0,0,1]])
            else:
                rot = np.array([[cos_phi, sin_phi, 0],
                                [-sin_phi, cos_phi,  0],
                                [0,0,1]])
            self.sys.rotate_particles(self.selected_particle2, rot, self.selected_particle.position)
            self.drawarea.queue_draw()

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
                   "about" : self.about,
                   "press" : self.darea.press, 
                   "release" : self.darea.release,
                   "motion" : self.darea.motion,
                   "save" : self.save,
                   "load" : self.load}
        return signals

    def about(self, item):
        resp = self.aboutdialog.run()
        if resp == Gtk.ResponseType.DELETE_EVENT or resp == Gtk.ResponseType.CANCEL:
            self.aboutdialog.hide()

    def load(self, item):
        dialog = Gtk.FileChooserDialog("Vyberte súbor",
                                        self.window,
                                        Gtk.FileChooserAction.OPEN,
                                        (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            dialog.destroy()
            with open(filename, 'rb') as f:
                self.darea.sys.particles = pickle.load(f)
            self.drawarea.queue_draw()
        else:
            dialog.destroy()
    def save(self, item):
        dialog = Gtk.FileChooserDialog("Vyberte súbor",
                                        self.window,
                                        Gtk.FileChooserAction.SAVE,
                                        (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        dialog.set_do_overwrite_confirmation(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            dialog.destroy()
            with open(filename, 'wb') as f:
                pickle.dump(self.darea.sys.particles, f)
        else:
            dialog.destroy()

    def forward(self, button=None):
        #TODO
        pass


if __name__ == '__main__':
    win = MainWindow()
    Gtk.main()
