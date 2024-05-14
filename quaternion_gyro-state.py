from scipy.spatial.transform import Rotation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

###########################################################################
#                            INITILISATION                                #
###########################################################################

data = pd.read_csv('./csv/A1/data_highres.csv')
data_br = pd.read_csv('./csv/A1/data_raven_highres.csv')

# Constants and data preparation
data_count = len(data['sync'])
dt = 0.004  # Time interval between measurements
sens = 13.375

t = [x*dt for x in range(data_count)]
t_br = data_br['Flight_Time_(s)']

gyro = [
    [x / sens for x in data['gyro_x']],
    [y / sens for y in data['gyro_y']],
    [z / sens for z in data['gyro_z']],
]
gyro_br = [
    [x for x in data_br['Gyro_X']],
    [x for x in data_br['Gyro_Y']],
    [x for x in data_br['Gyro_Z']]
]

###########################################################################
#                       QUATERNION METHODS                                #
###########################################################################

# Yoinked from:
# https://www.rocketryforum.com/threads/gyros-tilt-and-quaternions-are-not-your-friend.164151/


class Quaternion:
    def __init__(self, x=0.0, y=0.0, z=0.0, r=1.0):
        self.r = r
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        r, x, y, z = self.r, self.x, self.y, self.z
        return f"({r=},{x=},{y=},{z=})"

    def as_list(self):
        return [self.r, self.x, self.y, self.z]


def quaternion_normalize(quaternion):
    """
    Normalizes a quaternion.

    Args:
        quaternion: The input quaternion.
    Returns:
        The normalized quaternion.
    """

    p = quaternion
    test_p = (p.r * p.r) + (p.x * p.x) + (p.y * p.y) + (p.z * p.z)
    if test_p > 1.0:
        p.r *= 1.0 / math.sqrt(test_p)
        p.x *= 1.0 / math.sqrt(test_p)
        p.y *= 1.0 / math.sqrt(test_p)
        p.z *= 1.0 / math.sqrt(test_p)
    return p


def quaternion_multiply(quaternion1, quaternion2):
    """
    Multiplies two quaternions.

    Args:
        quaternion1: The first quaternion.
        quaternion2: The second quaternion.
    Returns:
        The resulting quaternion from the multiplication.
    """
    p = quaternion1
    t = quaternion2
    result = Quaternion()
    result.r = (p.r * t.r) + (-p.x * t.x) + (-p.y * t.y) + (-p.z * t.z)
    result.x = (p.r * t.x) + (p.x * t.r) + (p.y * t.z) + (-p.z * t.y)
    result.y = (p.r * t.y) + (-p.x * t.z) + (p.y * t.r) + (p.z * t.x)
    result.z = (p.r * t.z) + (p.x * t.y) + (-p.y * t.x) + (p.z * t.r)
    return result


def quaternion_init_half_euler(g_roll, g_pitch, g_yaw):
    """
    Initializes a quaternion from half Euler angles.

    Args:
        g_roll: Roll angle in degrees.
        g_pitch: Pitch angle in degrees.
        g_yaw: Yaw angle in degrees.
    Returns:
        The initialized quaternion.
    """
    x = (g_roll / 2.0) * math.pi / \
        180.0  # Half the degree and convert it to radians
    y = (g_pitch / 2.0) * math.pi / 180.0
    z = (g_yaw / 2.0) * math.pi / 180.0

    s_x = math.sin(x)
    c_x = math.cos(x)
    s_y = math.sin(y)
    c_y = math.cos(y)
    s_z = math.sin(z)
    c_z = math.cos(z)

    result = Quaternion()
    result.r = c_x * c_y * c_z + s_x * s_y * s_z
    result.x = s_x * c_y * c_z - c_x * s_y * s_z
    result.y = c_x * s_y * c_z + s_x * c_y * s_z
    result.z = c_x * c_y * s_z - s_x * s_y * c_z
    return result


###########################################################################
#                             CALCULATIONS                                #
###########################################################################

# Integrate gyroscope data with bias
quats = [Quaternion(0, 0, 0, 1)]
for i in range(data_count):
    gyro_x = gyro[0][i]
    gyro_y = gyro[1][i]
    gyro_z = gyro[2][i]

    q_dot = quaternion_init_half_euler(
        dt * (gyro_x),
        dt * (gyro_y),
        dt * (gyro_z)
    )

    q_w = quaternion_multiply(quats[i], q_dot)
    quats.append(quaternion_normalize(q_w))

quat_br = list(zip(
    data_br["Quat_1"],
    data_br["Quat_2"],
    [-x for x in data_br["Quat_4"]],
    data_br["Quat_3"],
))
np.savetxt('./csv/quaternion_estimate.csv', [
    (q.x, q.y, q.z, q.r) for q in quats
], delimiter=',', header="x,y,z,w")

###########################################################################
#                            VISUALISATION                                #
###########################################################################

# ESTIMATES
# ----------------------------------------------------------------
# Some components are swapped compared to raven ground truth, why?
# For estimate->ground truth:
#   w->x
#   x->-w
#   y->z
#   z->-y
start_time = 0
duration = 11

plt.figure()
plt.plot(t[int(start_time/dt):int(duration/dt)],
         [q.r for q in quats[int(start_time/dt):int(duration/dt)]])
plt.plot(t[int(start_time/dt):int(duration/dt)],
         [q.x for q in quats[int(start_time/dt):int(duration/dt)]])
plt.plot(t[int(start_time/dt):int(duration/dt)],
         [q.y for q in quats[int(start_time/dt):int(duration/dt)]])
plt.plot(t[int(start_time/dt):int(duration/dt)],
         [q.z for q in quats[int(start_time/dt):int(duration/dt)]])
plt.xlabel("Time (s)")
plt.title("Quaternion estimates")
plt.legend(["w", "x", "y", "z"], loc="upper left")
plt.savefig("./plot/state/attitude/quat_estimate.png")

# EULER ANGLE
plt.figure()
plt.plot(t[int(start_time/dt):int(duration/dt)],
         [
    Rotation.from_quat(q.as_list()).as_euler("xyz", degrees=True)
    for q in quats[int(start_time/dt):int(duration/dt)]
])
plt.xlabel("Time (s)")
plt.ylabel("Angle (degrees)")
plt.title("Euler angle estimates")
plt.legend(["Roll", "Pitch", "Yaw"], loc="lower right")
plt.savefig("./plot/state/attitude/euler_estimate.png")

# GROUND TRUTH
# ----------------------------------------------------------------
start_time = 2
duration += start_time
dt = 0.002

plt.figure()
plt.plot(t_br[int(start_time/dt):int(duration/dt)],
         quat_br[int(start_time/dt):int(duration/dt)])
plt.xlabel("Time (s)")
plt.title("Quaternion ground truth")
plt.legend(["w", "x", "y", "z"], loc="upper left")
plt.savefig("./plot/state/attitude/quat_truth.png")

# EULER ANGLE
plt.figure()
plt.plot(t_br[int(start_time/dt):int(duration/dt)],
         [
    Rotation.from_quat(q).as_euler("xyz", degrees=True)
    for q in quat_br[int(start_time/dt):int(duration/dt)]
])
plt.xlabel("Time (s)")
plt.ylabel("Angle (degrees)")
plt.title("Euler angle estimates")
plt.legend(["Roll", "Pitch", "Yaw"], loc="lower right")
plt.savefig("./plot/state/attitude/euler_truth.png")

plt.show()
