from .lib.math import Quaternion, Vector3
import pandas as pd

def parse_data(data: list, args: dict):
    """
    general data parsing for data used in multiple places
    """

    # MARK: quaternions (rotation and tilt)

    data_AV = data[0]
    data_BR = data[1]

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
    ax_AV = args['axisAV'][:3]
    scale = Vector3.with_array(list(map(
        float, args['axisAV'][4:-1].split(',')
    )))
    sens = 13.375
    gyro_AV = [
        [scale.x * x / sens for x in data_AV[f'Gyro_{str(ax_AV[0]).upper()}']],
        [scale.y * y / sens for y in data_AV[f'Gyro_{str(ax_AV[1]).upper()}']],
        [scale.z * z / sens for z in data_AV[f'Gyro_{str(ax_AV[2]).upper()}']],
    ]

    # Rotate BR data to global frame
    ax_BR = args['axisBR'][:3]
    scale = Vector3.with_array(list(map(
        float, args['axisBR'][4:-1].split(',')
    )))

    gyro_BR = [
        [scale.x * x for x in data_BR[f'Gyro_{str(ax_BR[0]).upper()}']],
        [scale.y * y for y in data_BR[f'Gyro_{str(ax_BR[1]).upper()}']],
        [scale.z * z for z in data_BR[f'Gyro_{str(ax_BR[2]).upper()}']]
    ]

    # estimates
    freq = int(args['freq'].split(':')[1])
    dt = 1/freq
    quats_BR = list(map(Quaternion.as_array, calculate_quat(gyro_BR, dt)))
    
    freq = int(args['freq'].split(':')[0])
    dt = 1/freq
    quats_AV = list(map(Quaternion.as_array, calculate_quat(gyro_AV, dt)))

    df_quats_AV = pd.DataFrame(quats_AV, columns=["x", "y", "z", "w"])
    df_quats_BR = pd.DataFrame(quats_BR, columns=["x", "y", "z", "w"])

    data.append(df_quats_AV)
    data.append(df_quats_BR)