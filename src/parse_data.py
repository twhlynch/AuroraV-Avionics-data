import pandas as pd
import numpy as np
from math import acos, cos, pi

from .lib.math import Quaternion, Vector3, GRAVITY
from .read_data import HIGHRES_HZ


def parse_data(data: list, args: dict):
    """
    general data parsing for data used in multiple places
    """

    # MARK: quaternions (rotation and tilt)

    data_highres = data[1]

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

    # Rotate AV data to global frame
    axis = args['axis'][:3]
    scale = Vector3.with_array(list(map(
        float, args['axis'][4:-1].split(',')
    )))
    sens = 13.375
    gyro = [
        [scale.x * x / sens for x in data_highres[f'gyro_{str(axis[0]).lower()}']],
        [scale.y * y / sens for y in data_highres[f'gyro_{str(axis[1]).lower()}']],
        [scale.z * z / sens for z in data_highres[f'gyro_{str(axis[2]).lower()}']],
    ]

    # estimates
    dt = 1/HIGHRES_HZ
    quats = list(map(Quaternion.as_array, calculate_quat(gyro, dt)))
    
    df_quats = pd.DataFrame(quats, columns=["x", "y", "z", "w"])
    print(df_quats)
    data[1]["quat_x"] = [quat for quat in df_quats["x"][1:]]
    data[1]["quat_y"] = [quat for quat in df_quats["y"][1:]]
    data[1]["quat_z"] = [quat for quat in df_quats["z"][1:]]
    data[1]["quat_w"] = [quat for quat in df_quats["w"][1:]]


    # MARK: tilt
    quats = list(zip(
        df_quats["x"],
        df_quats["y"],
        df_quats["z"],
        df_quats["w"],
    ))
    rotations = [Quaternion.with_array(q) for q in quats]

    z = Vector3(0, 0, 1)
    tilt = []
    tilt_cosine = []

    for rotation in rotations:
        result = rotation.apply(z)
        dot = np.dot(result.as_array(), z.as_array())
        dot = min(max(dot, -1.0), 1.0)  # Clamp the value for acos
        theta = acos(dot)*180/pi

        tilt.append(theta)
        tilt_cosine.append(cos(theta*pi/180))
    
    data[1]["tilt"] = tilt[1:]
    data[1]["tilt_cos"] = tilt_cosine[1:]