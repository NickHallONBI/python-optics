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

src = (0.,0.)
bs = (fobj - lobj, 0.)
objl = (fobj, 0)
obj = (objl[0]+dobj, objl[1])
img = (bs[0], bs[1] + dimg - dobj)
refl = (bs[0], bs[1] - lref)
ref = (refl[0], refl[1] - dref)

