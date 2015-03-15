from collections import namedtuple
from numpy import tan, pi

Point = namedtuple('Point', 'x, z, tanTheta')


def zImage(rayA, rayB):
    a = rayA.points[-1]
    b = rayB.points[-1]
    
    if a.z != b.z:
        return None
    else:
        try: 
            z = a.z + (b.x - a.x) / (a.tanTheta - b.tanTheta)
        except ZeroDivisionError:
            z = None
        except:
            raise
        return z


class Surface(object):
    def __init__(self, dz):
        self.dz = dz


class Lens(Surface):
    def __init__(self, dz, f):
        super(Lens, self).__init__(dz)
        self.f = f


class Pupil(Surface):
    def __init__(self, dz, r):
        super(Pupil, self).__init__(dz)
        self.r = r


class Ray(object):
    def __init__(self, x0, tan0, col=None):
        self.points = [ Point(float(x0), 0., float(tan0))]
        self.redraw = [ True ]
        if col:
            self.colour = col
        elif x0 == 0:
            self.colour = 'b'
        else:
            self.colour = 'r'


    def propogate(self, surfaces, start=0):
        #start = 0
        if start >= len(self.points):
            start = len(self.points) - 1
        else:
            self.points = self.points[0:start + 1]

        for i, surface in enumerate(surfaces[start:], start):
            prevPoint = self.points[i]
            z = prevPoint.z + surface.dz
            x = prevPoint.x + (surface.dz * prevPoint.tanTheta)
            
            if type(surface) is Lens:
                # Lenses bend rays.
                tanTheta = prevPoint.tanTheta - x / surface.f
            else:
                tanTheta = prevPoint.tanTheta
            
            self.points.append(Point(x, z, tanTheta))
            
            if type(surface) is Pupil:
                if abs(x) > surface.r:
                    return

        if i+1 == len(surfaces):
            if type(surface) is Lens:
                zFinal = z + 2. * surface.f
            else:
                zFinal = z + 0.1 * surface.dz
            self.points.append(Point(x + (zFinal - z) * tanTheta, zFinal, tanTheta))
