from __future__ import division
import logging
logger = logging.getLogger(__name__)
import ctypes

import pyglet
from pyglet.gl import *

import views.galaxy.map.stars
import utilities
import meshes
from globals import g
import models
import star

class Orbitals(object):
    def __init__(self, star_system_view):
        self.star_system_view = star_system_view
        self.all = []
        for orbit in range(0, 5):
            self.all.append(Orbital(self.star_system_view))

        self.light_amb = [0.1, 0.1, 0.1, 1.0]
        self.light_dif = [1.0, 1.0, 1.0, 1.0]

    def prepare(self, display_box):
        #logger.debug('display_box: %s'%self.display_box)
        self.orbital_width = int( (display_box['right'] - display_box['left']) / 5 )
        self.height = display_box['top'] - display_box['bottom']

        # adjust lighting based on star color
        star_type = self.star_system_view.model_star.type
        star_diffuse = star.Star.diffuse_light[star_type]
        self.light_dif = [star_diffuse[0], star_diffuse[1],
                star_diffuse[2], 0.1]

        model_orbitals = self.star_system_view.model_star.orbits
        for orbital_index in range(0, len(self.all)):
            orbital = self.all[orbital_index]
            model_orbital = model_orbitals[orbital_index]
            orbital_display_box = {
                'top':display_box['top'],
                'right':display_box['left'] + ((orbital_index + 1) * self.orbital_width),
                'bottom':display_box['bottom'],
                'left':display_box['left'] + (orbital_index * self.orbital_width),
            }
            orbital.prepare(model_orbital, orbital_display_box)

    def draw(self):
        glLoadIdentity()
        gluPerspective(self.star_system_view.persp[0],
            float(self.orbital_width)/self.height,
            self.star_system_view.persp[1],
            self.star_system_view.persp[2])

        for orbital in self.all:
            orbital.draw(self.light_amb, self.light_dif)

    def hide(self):
        for orbital in self.all:
            orbital.hide()

class Orbital(object):
    planet_z_depth = {
            'tiny': -225,
            'small': -175,
            'medium': -125,
            'large': -100,
            'huge': -75
    }

    def __init__(self, star_system_view):
        self.star_system_view = star_system_view
        self.model = None

        self.showing = False
        self.lightfv = ctypes.c_float * 4
        self.light_pos = [10, 0, 3, 0]
        self.look = [0, 0, -100]
        self.rotate_x = 0
        self.rotate_y = 0
        self.rotate_z = 0

        self.planet = meshes.Sphere()

        self.animated = False

    def animate(self, dt):
        self.rotate_y += (dt*self.model.orbit_speed)
        self.rotate_y %= 360

    def remove_animation(self):
        if self.animated is False: return
        pyglet.clock.unschedule(self.animate)
        self.animated = False

    def schedule_animation(self):
        if self.animated is True: return
        pyglet.clock.schedule_interval(self.animate, 1/60)
        self.animated = True

    def prepare(self, model_orbital, display_box):
        self.model = model_orbital
        if type(self.model) == models.galaxy.orbitals.Planet:
            self.showing = True
            self.look = [0, 0, Orbital.planet_z_depth[self.model.size]]
            self.planet.set_texture('%s.png'%self.model.type)
            self.rotate_z = self.model.orbit_inclination
        else:
            self.showing = False
            self.remove_animation()
            return

        self.display_box = display_box
        self.port_height = display_box['top'] - display_box['bottom']
        self.port_width = display_box['right'] - display_box['left']

        self.schedule_animation()

    def draw(self, light_amb, light_dif):
        if self.showing is False: return

        glViewport(
            self.display_box['left'],
            self.display_box['bottom'],
            self.port_width,
            self.port_height)

        glPushAttrib(GL_MODELVIEW)
        glMatrixMode(GL_MODELVIEW)

        glPushAttrib(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, self.lightfv(self.light_pos[0],
            self.light_pos[1], self.light_pos[2], self.light_pos[3]))
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.lightfv(light_amb[0],
            light_amb[1], light_amb[2], light_amb[3]))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.lightfv(light_dif[0],
            light_dif[1], light_dif[2], light_dif[3]))
        glEnable(GL_LIGHT0)
        glPopAttrib(GL_LIGHT0)

        glLoadIdentity()

        glPushMatrix()
        glTranslated(self.look[0], self.look[1], self.look[2])
        glRotatef(self.rotate_z, 0, 0, 1)
        glRotatef(self.rotate_y, 0, 1, 0)
        glRotatef(self.rotate_x, 1, 0, 0)

        self.planet.draw()
        glPopMatrix()

        glPopAttrib(GL_MODELVIEW)

    def hide(self):
        self.remove_animation()
