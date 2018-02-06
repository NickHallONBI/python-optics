from math import pi
import numpy as np

def rsum(*args):
    """Return harmonic sum of reciprocals of args."""
    return reduce(lambda x, y: x + 1./y, args, 0.)

fobj = 75.
fref = 200.

dobj = 150.
dref = 50.

lobj = 25.
lref = 25.

dimg = 1 / rsum(fobj, -dobj)
mag = - dimg / dobj

dapp = fref - 2. * dref
drsrc = 1 / rsum(fref, -dapp)

# Objects: x,y,r,theta, colour
src = (0., 0., 2.5, pi/2, 'red')
bs = (fobj - lobj, 0., 1.414*12.5, -pi/4, 'cyan')
objl = (fobj, 0, 12.5, pi/2, 'green')
obj = (objl[0]+dobj, objl[1], 12.5, pi/2, 'green')
img = (bs[0], bs[1] - (dimg - lobj), 12.5, 0., 'black')
refl = (bs[0], bs[1] + lref, 12.5, 0., 'red')
ref = (refl[0], refl[1] + dref, 12.5, 0., 'red')

drefim1 = 1 / rsum(fref, -(img[1] - refl[1]))
drefim2 = 1 / rsum(fref, -(2 * dref - drefim1))

refim1a = (refl[0], refl[1]+drefim1, 12.5, 0, 'red')
refim1b = (refl[0], refl[1]-(drefim1-2*dref), 12.5, 0, 'red')
refim2a = (refl[0], refl[1]+drefim2, 12.5, 0, 'red')

lenses = (refl, objl)
mirrors = (bs, ref, obj)
imgplanes = (img, refim1a, refim1b, refim2a)

# UI
from tkinter import *
s = 1.
width = 500

root=Tk()
w = Canvas(root, width=width, height=width)
w.pack()

scale = np.array([[s, 0, -bs[0]+s*width/2], [0, s, -bs[1]+s*width/2.], [0, 0, 1.]])

def draw(obj, **kwargs):
    x0, y0, r, theta, col = obj
    theta += pi/4
    rotate = np.array([[np.cos(theta), np.sin(theta), 0], 
                         [-np.sin(theta), np.cos(theta), 0],
                         [0, 0, 1]])
    dx, dy, null= np.dot(rotate, [r, r, 1])

    p0 = np.dot(scale, [x0-dx, y0-dy, 1])
    p1 = np.dot(scale, [x0+dx, y0+dy, 1])
    w.create_line(p0[0], p0[1], p1[0], p1[1], fill=col, **kwargs)

draw(src)
[draw(obj, arrow='both') for obj in lenses]
[draw(obj, width=2.0) for obj in mirrors]
[draw(obj, dash=(2,2)) for obj in imgplanes]


root.mainloop()