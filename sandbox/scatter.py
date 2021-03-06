import numpy as np
import matplotlib.pyplot as pl

from fisheye import fisheye

# generate random points in [0,1]^2
N = 10000
pos = np.random.random((N,2))

# initialize fisheye with radius R = 0.4 and focus in the center
F = fisheye(R=0.4,d=3)
F.set_focus([0.5,0.5])

fig, axs = pl.subplots(1,4,figsize=(10,3))

for iax, ax in enumerate(axs):
    
    # iterate through different fisheye modi
    if iax == 0:
        ax.set_title('original')
    elif iax == 1:
        ax.set_title('default fisheye')
        F.set_mode('default')
    elif iax == 2:
        ax.set_title('Sarkar-Brown')
        F.set_mode('Sarkar')
    elif iax == 3:
        ax.set_title('root')
        F.set_mode('root')

    if iax == 0:
        _pos = pos
    else:
        # fisheye transform
        _pos = F.radial_2D(pos) 

    ax.plot(_pos[:,0],_pos[:,1],'.k',markersize=1)
    ax.axis('square')
    ax.axis('off')

fig.tight_layout()
fig.savefig('scatter.png')

pl.show()
