from scipy.spatial.transform import Rotation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import argparse


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
    # Half the degree and convert it to radians
    x = (g_roll / 2.0) * math.pi / 180.0
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
def calculate_quat(gyro, dt):
    quats = [Quaternion(0, 0, 0, 1)]
    for i in range(len(gyro[0])):
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

    quats = [(q.x, q.y, q.z, q.r) for q in quats]
    np.savetxt(
        './csv/quaternion_estimate.csv',
        quats, delimiter=',', header="x,y,z,w"
    )
    return quats


###########################################################################
#                            VISUALISATION                                #
###########################################################################

def visualise(quats, start_time, duration, dt, typestr):

    t = [dt*i-start_time for i in range(len(quats))]

    plt.figure()
    plt.plot(t[int(start_time/dt):int(duration/dt)],
             quats[int(start_time/dt):int(duration/dt)])
    plt.xlabel("Time (s)")
    plt.title(f"Quaternion {typestr}")
    plt.legend(["x", "y", "z", "w"], loc="upper left")
    plt.savefig(f"./plot/state/attitude/quat_{typestr}.png")

    # EULER ANGLE
    plt.figure()
    plt.plot(t[int(start_time/dt):int(duration/dt)],
             [
        Rotation.from_quat(q).as_euler("xyz", degrees=True)
        for q in quats[int(start_time/dt):int(duration/dt)]
    ])
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (degrees)")
    plt.title(f"Euler angle {typestr}")
    plt.legend(["Roll", "Pitch", "Yaw"], loc="lower right")
    plt.savefig(f"./plot/state/attitude/euler_{typestr}.png")
    plt.show()


if __name__ == '__main__':

    ###########################################################################
    #                            INITILISATION                                #
    ###########################################################################

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--freq',
                        metavar='freqAV:freqBR',
                        type=str,
                        help='Frequency range in the format freq1:freq2',
                        required=True)

    parser.add_argument('-t', '--time',
                        metavar='{AV/BR}:start:duration',
                        type=str, nargs=2,
                        help='Time ranges for AV and BR (e.g., AV:0:5 BR:10:15)',
                        required=True)

    parser.add_argument('--axisAV',
                        metavar='axes[scalars,]',
                        type=str,
                        help='Axis adjustments for AV measurements',
                        default='xyz[1,1,1]')

    parser.add_argument('--axisBR',
                        metavar='axes[scalars,]',
                        type=str,
                        help='Axis adjustments for BR measurements',
                        default='xyz[1,1,1]')

    parser.add_argument('directory',
                        metavar='directory',
                        type=str,
                        help='Path to the directory to extract CSV data from')
    args = parser.parse_args()

    # Extract CSV data from relevant directory
    directory = args.directory
    data_AV = pd.read_csv(f'./csv/{directory}/data_highres.csv')
    data_BR = pd.read_csv(f'./csv/{directory}/data_raven_highres.csv')

    # Axis adjustments
    # -----------------------------------------------------------------
    # This is an absolutely devilish and disgusting hacky workaround to
    # adjusting the axes and their scaling

    # Rotate AV data to global frame
    ax_AV = args.axisAV[:3]
    scale_x, scale_y, scale_z = map(
        float, args.axisAV[4:-1].split(','))    # I want to vomit

    sens = 13.375
    gyro_AV = [
        [scale_x * x / sens for x in data_AV[f'gyro_{ax_AV[0]}']],
        [scale_y * y / sens for y in data_AV[f'gyro_{ax_AV[1]}']],
        [scale_z * z / sens for z in data_AV[f'gyro_{ax_AV[2]}']],
    ]

    # Rotate BR data to global frame
    ax_BR = args.axisBR[:3]
    scale_x, scale_y, scale_z = map(
        float, args.axisBR[4:-1].split(','))    # Yuck

    gyro_BR = [
        [scale_x * x for x in data_BR[f'Gyro_{ax_BR[0]}']],
        [scale_y * y for y in data_BR[f'Gyro_{ax_BR[1]}']],
        [scale_z * z for z in data_BR[f'Gyro_{ax_BR[2]}']]
    ]

    # Time parsing
    # -------------------------------------------------------
    time_ranges = {}
    for time_str in args.time:
        source, start, duration = time_str.split(':')
        time_ranges[source] = (float(start), float(duration))

    ###########################################################################
    #                              EXECUTION                                  #
    ###########################################################################

    # Visualise AV estimates
    start_AV, duration_AV = time_ranges['AV']
    freq = int(args.freq.split(':')[0])
    dt = 1/freq
    visualise(calculate_quat(gyro_AV, dt), start_AV,
              duration_AV, dt, "AV estimates")

    # Visualise BR estimates
    start_BR, duration_BR = time_ranges['BR']
    freq = int(args.freq.split(':')[1])
    dt = 1/freq
    visualise(calculate_quat(gyro_BR, dt), start_BR,
              duration_BR, dt, "BR estimates")

    # Manually rotating BR truth quaternions to global frame (ew)
    quats_truth = list(zip(
        [-x for x in data_BR['Quat_4']],
        [y for y in data_BR['Quat_3']],
        [z for z in data_BR['Quat_2']],
        [w for w in data_BR['Quat_1']],
    ))
    # Visualise BR truth
    visualise(quats_truth, start_BR, duration_BR, dt, "truth")
