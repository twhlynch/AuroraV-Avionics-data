import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse
from lib.math import Quaternion, Vector3


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

        q_dot = Quaternion.with_half_euler(
            dt * (gyro_x),
            dt * (gyro_y),
            dt * (gyro_z)
        )

        q_w = quats[i].multiply(q_dot)
        quats.append(q_w.normalise())

    return quats


###########################################################################
#                            VISUALISATION                                #
###########################################################################

def visualise(quats, start_time, duration, dt, typestr):

    t = [dt*i-start_time for i in range(len(quats))]
    split = typestr.split(' ')

    plt.figure()
    plt.plot(t[int(start_time/dt):int(duration/dt)],quats[int(start_time/dt):int(duration/dt)])
    plt.xlabel("Time (s)")
    plt.title(f"Quaternion {typestr}")
    plt.legend(["x", "y", "z", "w"], loc="upper left")
    # plt.savefig(f"./plot/state/attitude/quat_{split[0]}.png")

    # EULER ANGLE
    angles = [
        q.as_euler(degrees=True).__array__() for q in quats[int(start_time/dt):int(duration/dt)]
    ]
    plt.figure()
    plt.plot(t[int(start_time/dt):int(duration/dt)], [a[0] for a in angles])
    plt.plot(t[int(start_time/dt):int(duration/dt)], [a[1] for a in angles])
    plt.plot(t[int(start_time/dt):int(duration/dt)], [a[2] for a in angles])
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (degrees)")
    plt.title(f"Euler angle {typestr}")
    plt.legend(["Roll", "Pitch", "Yaw"], loc="lower right")
    # plt.savefig(f"./plot/state/attitude/euler_{split[0]}.png")
    plt.show()


###########################################################################
#                            INITILISATION                                #
###########################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--freq',
        metavar='freqAV:freqBR',
        type=str,
        help='Frequency range in the format freq1:freq2',
        required=True
    )
    parser.add_argument(
        '-t', '--time',
        metavar='{AV/BR}:start:duration',
        type=str, nargs=2,
        help='Time ranges for AV and BR (e.g., AV:0:5 BR:10:15)',
        required=True
    )
    parser.add_argument(
        '--axisAV',
        metavar='axes[scalars,]',
        type=str,
        help='Axis adjustments for AV measurements',
        default='xyz[1,1,1]'
    )
    parser.add_argument(
        '--axisBR',
        metavar='axes[scalars,]',
        type=str,
        help='Axis adjustments for BR measurements',
        default='xyz[1,1,1]'
    )
    parser.add_argument(
        'directory',
        metavar='directory',
        type=str,
        help='Path to the directory to extract CSV data from'
    )
    args = parser.parse_args()

    # Extract CSV data from relevant directory
    directory = args.directory
    data_AV = pd.read_csv(f'{directory}/data_highres.csv')
    data_BR = pd.read_csv(f'{directory}/data_raven_highres.csv')

    # Axis adjustments
    # -----------------------------------------------------------------
    # This is an absolutely devilish and disgusting hacky workaround to
    # adjusting the axes and their scaling

    # Rotate AV data to global frame
    ax_AV = args.axisAV[:3]
    scale = Vector3.with_array(list(map(
        float, args.axisAV[4:-1].split(',')
    )))
    sens = 13.375
    gyro_AV = [
        [scale.x * x / sens for x in data_AV[f'Gyro_{str(ax_AV[0]).upper()}']],
        [scale.y * y / sens for y in data_AV[f'Gyro_{str(ax_AV[1]).upper()}']],
        [scale.z * z / sens for z in data_AV[f'Gyro_{str(ax_AV[2]).upper()}']],
    ]

    # Rotate BR data to global frame
    ax_BR = args.axisBR[:3]
    scale = Vector3.with_array(list(map(
        float, args.axisBR[4:-1].split(',')
    )))
    print(scale)
    print(ax_BR)

    gyro_BR = [
        [scale.x * x for x in data_BR[f'Gyro_{str(ax_BR[0]).upper()}']],
        [scale.y * y for y in data_BR[f'Gyro_{str(ax_BR[1]).upper()}']],
        [scale.z * z for z in data_BR[f'Gyro_{str(ax_BR[2]).upper()}']]
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
    # -----------------------------------------------------------
    start_AV, duration_AV = time_ranges['AV']
    freq = int(args.freq.split(':')[0])
    dt = 1/freq

    quats_AV = list(map(Quaternion.__array__, calculate_quat(gyro_AV, dt)))
    np.savetxt(
        f'{directory}/quaternion_estimate_AV.csv',
        quats_AV, delimiter=',', header="x,y,z,w", comments=""
    )
    visualise(quats_AV, start_AV, duration_AV, dt, "AV estimates")

    # Visualise BR estimates
    # -----------------------------------------------------------
    start_BR, duration_BR = time_ranges['BR']
    freq = int(args.freq.split(':')[1])
    dt = 1/freq

    quats_BR = list(map(Quaternion.__array__, calculate_quat(gyro_BR, dt)))
    np.savetxt(
        f'{directory}/quaternion_estimate_BR.csv',
        quats_BR, delimiter=',', header="x,y,z,w", comments=""
    )
    visualise(quats_BR, start_BR, duration_BR, dt, "BR estimates")

    # Visualise BR truth
    # -----------------------------------------------------------
    # Manually rotating BR truth quaternions to global frame (ew)
    quats_truth = list(zip(
        [-x for x in data_BR['Quat_4']],
        [y for y in data_BR['Quat_3']],
        [z for z in data_BR['Quat_2']],
        [w for w in data_BR['Quat_1']],
    ))
    visualise(quats_truth, start_BR, duration_BR, dt, "truth")
