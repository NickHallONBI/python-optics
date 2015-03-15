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
lenses = [Lens(100, 50), Pupil(100, 20), Lens(150, 50)]


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

    label = QLabel('f', inputs)
    inputsGrid.addWidget(label, 0, 0)
    label = QLabel('dz', inputs)
    inputsGrid.addWidget(label, 0, 1)

    for i, lens in enumerate(lenses):
      # focal length control
      fInput = QSpinBox(inputs)
      fInput.setRange(lens.f / 10, 9999)
      fInput.setValue(lens.f)
      # position control
      zInput = QSpinBox(inputs)
      zInput.setRange(lens.dz / 10, 9999)
      zInput.setValue(lens.dz)
      # Use partial to call as ((self, target index, target parameter), new value)
      fInput.valueChanged[int].connect(partial(self.set_model_parameter, i, 'f'))
      zInput.valueChanged[int].connect(partial(self.set_model_parameter, i, 'dz'))
      # Use partial to call as ((self, row number), new value)
      fInput.valueChanged.connect(partial(self.replot_model, i))
      zInput.valueChanged.connect(partial(self.replot_model, i))
      # Add widgets to layout.
      inputsGrid.addWidget(fInput, i+1, 0)
      inputsGrid.addWidget(zInput, i+1, 1)

    # This stops elements been stretched over all available space. 
    inputsGrid.setRowStretch(i + 2, 1)
    inputsGrid.setColumnStretch(2, 1)

    dock.setWidget (inputs)
    #self.plot ()


  def set_model_parameter(self, index, parameter, value):
      setattr(lenses[index], parameter, value)

  def replot_model(self, n, value):
    if not self.rays or n == 0:
      numRays = 5
      height = 10.
      tanThetas = numpy.arange(-height/lenses[0].dz, 0.01, (height/lenses[0].dz) / numRays)
      self.rays = [Ray(height, tanTheta) for tanTheta in tanThetas]
      self.rays.extend([Ray(0, tanTheta) for tanTheta in tanThetas])

    self.drawing.cla()
    self.drawing.hold(True)
    # Redraw model from lens n
    max_radius = 0
    
    for ray in self.rays:
      ray.propogate(lenses, start=n)
      ps = [(p.z, p.x) for p in ray.points]
      xs, ys = zip(*ps)
      self.drawing.plot(xs, ys, ray.colour)
      max_radius = max(max_radius, max(ys))

    z = 0.
    r = max_radius
    for lens in lenses:
      z += lens.dz
      f = lens.f
      self.drawing.plot([z, z], [-r, r], 'k', linewidth=2)
      self.drawing.plot([z-f, z-f], [-r, r], 'k', linewidth=1)
      self.drawing.plot([z+f, z+f], [-r, r], 'k', linewidth=1)

    zImg = zImage(*self.rays[0:2])
    print zImg

    self.drawing.plot([zImg, zImg], [-r, r], 'r-')

    self.drawing.set_ylim(-r * 1.2, r * 1.2)
    self.canvas.draw ()


if __name__ == "__main__":
  app = QApplication (sys.argv)
  main = MainWindow ()
  main.show ()
  sys.exit (app.exec_ ())