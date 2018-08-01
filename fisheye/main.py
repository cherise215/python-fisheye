from __future__ import print_function

import numpy as np
from scipy.spatial.distance import cdist

def is_iterable(obj):
    try:
        some_object_iterator = iter(obj)
        return True
    except TypeError as te:
        return False

class fisheye():

    def __init__(self,R,mode='default',d=4,xw=0.25):

        assert(d > 0)
        assert(xw >= 0.0 and xw<=1.0)

        self.R = R
        self.d = d

        if mode == 'Sarkar':
            self.xw = 0
        else:
            self.xw = xw

        if mode == 'sqrt':
            assert(d > 1)

        self.mode = mode

        self._compute_parameters()

    def _compute_parameters(self):
        d = self.d
        xw = self.xw

        if self.mode in ('default', 'Sarkar'):
            self.f2 = lambda x: (x+self.d*x) / (self.d*x + self.A2)
            self.f2_inverse = lambda x: self.A2 * x / (self.d * (1-x) + 1)
        elif self.mode == 'sqrt':
            self.f2 = lambda x: (self.d/self.A2*x)**(1./self.d)
            self.f2_inverse = lambda x: self.A2 / self.d * x**self.d

        self.f1 = lambda x: 1 - (-1./self.A1 + np.sqrt(1/self.A1**2 + 2*(1-x)/self.A1))
        self.f1_inverse = lambda x: x - self.A1/2 * (1-x)**2

        if xw == 0.0:
            self.A1 = 0
            if self.mode == 'sqrt':
                self.A2 = d
            else:
                self.A2 = 1
        elif xw == 1.0:
            self.A2 = 1
            self.A1 = 0
        else:

            if self.mode == 'default':
                X = np.array([[ xw**2/2., 1 - ((d+1)*xw / (d*xw+1)) ],
                              [ xw,         - (d+1) / (d*xw+1)**2   ]])
            elif self.mode == 'sqrt':
                X = np.array([[ xw**2/2, ((1-xw)**d)/d],
                              [xw, -(1-xw)**(d-1)]])

            b = -np.array([xw-1,1])
            self.A1, self.A2 = np.linalg.inv(X).dot(b)

        xc = self.A1/2 * xw**2 + xw
        self.xc = 1 - xc

        print(xw, self.A1, self.A2, xc)


    def set_magnification(self,d):
        assert(d > 0)
        if self.mode == 'sqrt':
            assert(d>=1)
        self.d = d
        self._compute_parameters()

    def set_demagnification_width(self,xw):
        assert(xw >= 0.0 and xw<=1.0)
        if self.mode == 'Sarkar':
            self.xw = 0
        else:
            self.xw = xw
        self._compute_parameters()

    def set_radius(self,R):
        self.R = R

    def set_mode(self,mode):
        self.mode = mode

        if self.mode == 'sqrt':
            assert(self.d>=1)

        self._compute_parameters()

    def set_focus(self,focus):

        if not is_iterable(focus):
            focus = np.array([focus])

        if not type(focus) == np.ndarray:
            focus = np.array(focus)

        self.focus = focus

    def radial(self,pos):

        is_scalar = not is_iterable(focus)

        if is_scalar:
            pos = np.array([[pos]])
        else:
            if len(pos.shape) == 1:
                pos = pos.reshape((len(pos.shape),1))

    def fisheye_raw(self,r):
        result = np.copy(r)
        if self.xc > 0 and self.xc < 1:
            result[r<=self.xc] = self.f2(r[r<=self.xc])
            ndcs = np.logical_and(r>self.xc, r<1)
            result[ndcs] = self.f1(r[ndcs])
        elif self.xc == 1:
            result[r<1] = self.f2(r[r<1])

        return result

    def fisheye_raw_inverse(self,r):
        result = np.copy(r)
        if self.xw > 0 and self.xw < 1:
            result[r<=1-self.xw] = self.f2_inverse(r[r<=1-self.xw])
            ndcs = np.logical_and(r>1-self.xw, r<1)
            result[ndcs] = self.f1_inverse(r[ndcs])
        elif self.xw == 0:
            result[r<1] = self.f2_inverse(r[r<1])

        return result

    def radial_2D(self,pos,inverse=False):

        if not type(pos) == np.ndarray:
            pos = np.array(pos)

        original_shape = pos.shape

        if len(pos.shape) == 1:
            pos = pos.reshape((1,pos.shape[0]))

        theta = np.arctan2(pos[:,1]-self.focus[1], pos[:,0]-self.focus[0])

        x = cdist(pos, self.focus.reshape(1,len(self.focus))).flatten() / self.R


        if not inverse:
            newx = self.fisheye_raw(x)
        else:
            newx = self.fisheye_raw_inverse(x)

        newpos = np.empty_like(pos)

        newpos[:,0] = self.focus[0] + np.cos(theta) * self.R * newx
        newpos[:,1] = self.focus[1] + np.sin(theta) * self.R * newx

        newpos = newpos.reshape(original_shape)

        return newpos

    def inverse_radial_2D(self,pos):
        return self.radial_2D(pos, inverse=True)

if __name__=="__main__":
    F = fisheye(0.5,mode='sqrt',xw=1.0,d=3)    
    
    F.set_focus([0.5,0.5])

    point = [0.99,0.5]
    print("original point =", point)
    transform = F.radial_2D(point)
    print("fisheye point =", transform)
    result = F.inverse_radial_2D(transform)
    print("inverse point =", result)
    
