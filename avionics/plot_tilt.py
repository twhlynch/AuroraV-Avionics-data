from scipy.spatial.transform import Rotation
from math import cos, acos, pi
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = pd.read_csv("csv/A1/data_raven_highres.csv")

quat = pd.read_csv("csv/A1/quaternion_estimate_BR.csv")
quats = list(zip(
    quat["x"],
    quat["y"],
    quat["z"],
    quat["w"],
))
rotations = [Rotation.from_quat(q) for q in quats]

z = np.array([0, 0, 1])
tilt = []
tilt_cosine = []

for rotation in rotations:
    result = rotation.apply(z)
    dot = np.dot(result, z)
    print(dot)
    try:
        theta = acos(dot)*180/pi
    except ValueError as e:
        theta = acos(1)*180/pi

    tilt.append(theta)
    tilt_cosine.append(cos(theta*pi/180))

plt.subplot(2, 1, 1)
plt.plot([t*0.002 for t in range(len(rotations))], tilt)
plt.xlabel("Time(s)")
plt.ylabel("tilt (degrees)")
plt.title("Aurora I body-axis tilt")
data["Tilt_(degrees)"] = tilt[1:]

plt.subplot(2, 1, 2)
plt.plot([t*0.002 for t in range(len(rotations))], tilt_cosine)
plt.xlabel("Time(s)")
plt.ylabel("tilt cosine")
data["Tilt_Cosine"] = tilt_cosine[1:]

data.to_csv("csv/A1/data_highres.csv")
plt.show()
