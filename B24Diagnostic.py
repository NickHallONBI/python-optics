#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from functools import partial
## namespace organization changed in PyQt5 but the class name was kept.
## importing this way makes it easier to change to PyQt5 later
from PyQt4.QtGui import (QMainWindow, QApplication, QDockWidget, QWidget,
                         QGridLayout, QSpinBox, QVBoxLayout, QLabel)
from PyQt4.QtCore import Qt

import numpy
import matplotlib.pyplot
import matplotlib.backends.backend_qt4agg

from geomopt import Lens, Pupil, Ray, zImage
surfs = [Lens(200, 125), Pupil(125, 5), Lens(100, 50)]


class MainWindow (QMainWindow):
  def __init__ (self):
    QMainWindow.__init__ (self)

    self.rays = None

    self.figure  = matplotlib.pyplot.figure ()
    self.drawing = self.figure.add_subplot (111)
    matplotlib.pyplot.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)
    self.drawing.margins(0., 0.)
    self.canvas  = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg (self.figure)

    self.setCentralWidget (self.canvas)

    dock = QDockWidget ("Values")
    self.addDockWidget (Qt.RightDockWidgetArea, dock)

    inputs = QWidget()
    inputsGrid = QGridLayout(inputs)
    inputsGrid.setSpacing(5)

    for i, surf in enumerate(surfs):
      if type(surf) is Lens:
        pLabel = QLabel('f', inputs)
        # focal length control
        pInput = QSpinBox(inputs)
        pInput.setRange(-10000, 10000)
        pInput.setValue(surf.f)
        # Use partial to call as ((self, target index, target parameter), new value)
        pInput.valueChanged[int].connect(partial(self.set_model_parameter, i, 'f'))
      elif type(surf) is Pupil:
        pLabel = QLabel('r', inputs)
        # radius control
        pInput = QSpinBox(inputs)
        pInput.setRange(1, 100)
        pInput.setValue(surf.r)
        # Use partial to call as ((self, target index, target parameter), new value)
        pInput.valueChanged[int].connect(partial(self.set_model_parameter, i, 'r'))
      else:
        next
        
      # position control
      zLabel = QLabel('dz', inputs)
      zInput = QSpinBox(inputs)
      zInput.setRange(surf.dz / 10, 9999)
      zInput.setValue(surf.dz)
      # Use partial to call as ((self, target index, target parameter), new value)
      zInput.valueChanged[int].connect(partial(self.set_model_parameter, i, 'dz'))
      
      # Use partial to call as ((self, row number), new value)
      pInput.valueChanged.connect(partial(self.replot_model, i))
      zInput.valueChanged.connect(partial(self.replot_model, i))

      # Add widgets to layout.
      inputsGrid.addWidget(pLabel, i, 0)
      inputsGrid.addWidget(pInput, i, 1)
      inputsGrid.addWidget(zLabel, i, 2)
      inputsGrid.addWidget(zInput, i, 3)

    # This stops elements been stretched over all available space. 
    inputsGrid.setRowStretch(i + 1, 1)
    inputsGrid.setColumnStretch(4, 1)

    dock.setWidget (inputs)
    self.replot_model()


  def set_model_parameter(self, index, parameter, value):
      setattr(surfs[index], parameter, value)

  def replot_model(self, n=0, value=None):
    if not self.rays or n == 0:
      numRays = 5
      height = 1.
      tanThetas = numpy.arange(-height/surfs[0].dz, 0.01, (height/surfs[0].dz) / numRays)
      self.rays = [Ray(height, tanTheta) for tanTheta in tanThetas]
      self.rays.extend([Ray(0, tanTheta + 0.5 * height/surfs[0].dz) for tanTheta in tanThetas])

    self.drawing.cla()
    self.drawing.hold(True)
    # Redraw model from lens n
    max_radius = 0
    
    for ray in self.rays:
      ray.propogate(surfs, start=n)
      ps = [(p.z, p.x) for p in ray.points]
      us, vs = zip(*ps)
      self.drawing.plot(us, vs, ray.colour)
      max_radius = max(max_radius, max(vs))

    z = 0.
    r = max_radius
    vText = 1.1 * r
    lens_style = dict(head_width=max(us)/100.,
                      head_length=r/10.,
                      fc='k',
                      ec='k')
    for surf in surfs:
      z += surf.dz
      if type(surf) is Lens:
        f = surf.f
        self.drawing.arrow(z, 0, 0, 1.01*r, **lens_style)
        self.drawing.arrow(z, 0, 0, -1.01*r, **lens_style)
        #self.drawing.plot([z, z], [-r, r], 'k', linewidth=2)
        self.drawing.plot([z+f, z+f], [-r/3., r/3.], 'k', linewidth=1)
        if z - f > 0:
            self.drawing.plot([z-f, z-f], [-r/3., r/3.], 'k', linewidth=1)
        self.drawing.text(z, -vText, '%.1f' % z, ha='center', va='top')
      elif type(surf) is Pupil:
        min_radius = surf.r
        self.drawing.plot([z, z], [r, min_radius], 'k', linewidth=4)
        self.drawing.plot([z, z], [-r, -min_radius], 'k', linewidth=4)
        self.drawing.text(z, vText, '%.1f' % z, ha='center')

    zImg = zImage(*self.rays[-2:])
    if zImg:
        self.drawing.plot([zImg, zImg], [-r, r], 'r-')
        if type(surfs[-1] is Lens):
          offsetImg = zImg - (z + surfs[-1].f)
        else:
          offsetImg = zImg - z
        self.drawing.text(zImg, vText, '%.1f' % offsetImg, ha='center')

    self.drawing.set_ylim(-r * 1.2, r * 1.2)
    self.canvas.draw ()


if __name__ == "__main__":
  app = QApplication (sys.argv)
  main = MainWindow ()
  main.show ()
  sys.exit (app.exec_ ())