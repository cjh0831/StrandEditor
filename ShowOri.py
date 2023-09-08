import scipy.io as scio
import numpy as np
import matplotlib.pyplot as plt

ori = scio.loadmat("Ori3D_pred.mat")["Ori"]
occ = scio.loadmat("Occ3D_pred.mat")["Occ"]

print(ori.shape)
x = []
y = []
z = []
color = []
depth = ori.shape[2] // 3
for i in range(ori.shape[0]):
    for j in range(ori.shape[1]):
        for k in range(depth):
            if occ[i][j][k] > 0.5:
                x.append(i/100.)
                y.append(j/100.)
                z.append(k/100.)

                c = np.array([ori[i, j, k], ori[i, j, k+depth], ori[i, j, k+depth*2]])
                c = (c + 1) / 2
                c = np.clip(c, 0, 1)
                color.append(c)

x = np.array(x)
y = np.array(y)
z = np.array(z)
color = np.array(color)
fig = plt.figure()

ax = plt.axes(projection = "3d")

ax.scatter3D(y, z, -x, c = color, marker = "s")
plt.show()