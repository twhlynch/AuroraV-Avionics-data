# For AV binary:
# 0x54 - High resolution identifier
# 0x8A - Low resolution identifier

# High resolution data:
# [0] identifier
# [7:1] Big endian 16 bit - [acc_x1, acc_x2, acc_y1, acc_y2, acc_z1, acc_z2]
# [13:8] Big endian 16 bit - [gyro_x1, gyro_x2, gyro_y1, gyro_y2, gyro_z1, gyro_z2]

# Low resolution data:
# [0] identifier
# [3:1] Big endian 24 bit - [press_1, press_2, press_3]
# [6:4] Big endian 24 bit - [temp_1, temp_2, temp_3]

# Expected values:
# acc: +-16
# gyro: +-280 (+-20)
# press: +-2^32/64 (~101)
# temp: 0-50 (~40)

import sys
from pandas import DataFrame

LOWRES_HZ = 50
HIGHRES_HZ = 500

SENSITIVITY = {
    'acc': 1 / 2048,
    'gyro': 0.00875,
    'press': 1 / 64, # FIXME: something wrong
    'temp': 1 / 2**16,
}

def read_frame(data_bytes):
    HIGHRES_ID = 0x54
    LOWRES_ID = 0x8A

    if len(data_bytes) < 2:
        return None

    frame_header = data_bytes[0]
    frame_length = data_bytes[0] & 0x0F

    if frame_header == HIGHRES_ID:
        frame_length = 13
        frame_data = data_bytes[1:frame_length]

        return {
            'frame_id': 'highres',
            'frame_length': frame_length,

            'acc_x': int.from_bytes(frame_data[0:2], byteorder='big', signed=True) * SENSITIVITY["acc"],
            'acc_y': int.from_bytes(frame_data[2:4], byteorder='big', signed=True) * SENSITIVITY["acc"],
            'acc_z': int.from_bytes(frame_data[4:6], byteorder='big', signed=True) * SENSITIVITY["acc"],

            'gyro_x': int.from_bytes(frame_data[6:8], byteorder='big', signed=True) * SENSITIVITY["gyro"],
            'gyro_y': int.from_bytes(frame_data[8:10], byteorder='big', signed=True) * SENSITIVITY["gyro"],
            'gyro_z': int.from_bytes(frame_data[10:12], byteorder='big', signed=True) * SENSITIVITY["gyro"],
        }

    elif frame_header == LOWRES_ID:
        frame_length = 7
        frame_data = data_bytes[1:frame_length]

        return {
            'frame_id': 'lowres',
            'frame_length': frame_length,
            'press': int.from_bytes(frame_data[0:3], byteorder='big', signed=True) * SENSITIVITY["press"],
            'temp': int.from_bytes(frame_data[3:6], byteorder='big', signed=True) * SENSITIVITY["temp"]
        }


def read_data(filepath: str) -> tuple[DataFrame, DataFrame]:
    LOWRES_HEADER = ["press", "temp", "time"]
    HIGHRES_HEADER = ["acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z", "time"]

    lowres_data = []
    highres_data = []

    lowres_caluculated_data = {
        'time': 0.0,
    }
    highres_caluculated_data = {
        'time': 0.0,
    }

    with open(filepath, "rb") as file:
        data_bytes = bytearray(file.read())

    while len(data_bytes) > 0:
        print(len(data_bytes))
        frame = read_frame(data_bytes)
        if frame is not None:

            if frame['frame_id'] == 'highres':
                
                frame_data = [
                    frame['acc_x'],
                    frame['acc_y'],
                    frame['acc_z'],
                    frame['gyro_x'],
                    frame['gyro_y'],
                    frame['gyro_z'],
                    highres_caluculated_data["time"]
                ]

                highres_data.append(frame_data)
                highres_caluculated_data["time"] += 1 / HIGHRES_HZ

            elif frame['frame_id'] == 'lowres':
                frame_data = [
                    frame['press'],
                    frame['temp'],
                    lowres_caluculated_data['time']
                ]

                lowres_data.append(frame_data)
                lowres_caluculated_data['time'] += 1 / LOWRES_HZ

            data_bytes = data_bytes[frame['frame_length']:]

        else:
            data_bytes = data_bytes[1:]

    lowres_csv = DataFrame(lowres_data, columns=LOWRES_HEADER)
    highres_csv = DataFrame(highres_data, columns=HIGHRES_HEADER)

    return lowres_csv, highres_csv


if __name__ == "__main__":
    filename = sys.argv[1]
    lowres, highres = read_data(filename)
    lowres.to_csv(f"{filename}_lowres.csv")
    highres.to_csv(f"{filename}_highres.csv")