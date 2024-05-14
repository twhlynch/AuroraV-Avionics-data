from scipy.spatial.transform import Rotation
import matplotlib.pyplot as plt
import pandas as pd

###########################################################################
#                            INITILISATION                                #
###########################################################################

data_br = pd.read_csv('./csv/A1/data_raven_highres.csv')

# Constants and data preparation
data_count = len(data_br['Flight_Time_(s)'])
dt = 0.002  # Time interval between measurements

t_br = data_br['Flight_Time_(s)']

gyro_br = [
    [x for x in data_br['Gyro_X']],
    [x for x in data_br['Gyro_Y']],
    [x for x in data_br['Gyro_Z']]
]

###########################################################################
#                             CALCULATIONS                                #
###########################################################################

# Integrate gyroscope data with bias
x_est_list = [[0, 0, 0]]
for i in range(data_count):
    gyro_x = gyro_br[0][i] - (-0.12)
    gyro_y = gyro_br[2][i] - (0.61)
    gyro_z = gyro_br[1][i] - (-0.59)
    x_est_list.append([
        x_est_list[i][0] + dt*gyro_x,
        x_est_list[i][1] + dt*gyro_y,
        x_est_list[i][2] + dt*gyro_z
    ])

quat = [
    Rotation.from_euler('xyz', [x, y, z], degrees=True).as_quat()
    for (x, y, z) in x_est_list[1:]
]
quat_br = list(zip(
    data_br["Quat_1"],
    data_br["Quat_2"],
    data_br["Quat_3"],
    data_br["Quat_4"],
))
euler = [
    Rotation.from_quat(quat).as_euler('xyz', degrees=True)
    for quat in quat_br
]

estimated_roll = [x[0] for x in x_est_list[1:]]
estimated_pitch = [x[1] for x in x_est_list[1:]]
estimated_yaw = [x[2] for x in x_est_list[1:]]

###########################################################################
#                            VISUALISATION                                #
###########################################################################

plt.figure()
plt.plot(t_br, estimated_roll)
plt.plot(t_br, estimated_pitch)
plt.plot(t_br, estimated_yaw)
plt.xlabel("Time (s)")
plt.ylabel("Angle (degrees)")
plt.title("Euler angle estimates")
plt.legend(["Roll", "Pitch", "Yaw"], loc="upper left")
plt.savefig("./plot/attitude/euler.png")


plt.figure()
plt.plot(t_br[0:int(12/dt)], [x[3] for x in quat[0:int(12/dt)]])
plt.plot(t_br[0:int(12/dt)], [x[0] for x in quat_br[0:int(12/dt)]])
plt.xlabel("Time (s)")
plt.title("Quaternion w")
plt.legend(["Estimated", "Ground truth"], loc="lower left")
plt.savefig("./plot/attitude/w.png")


plt.figure()
plt.plot(t_br[0:int(12/dt)], [x[0] for x in quat[0:int(12/dt)]])
plt.plot(t_br[0:int(12/dt)], [x[1] for x in quat_br[0:int(12/dt)]])
plt.xlabel("Time (s)")
plt.title("Quaternion x")
plt.legend(["Estimated", "Ground truth"], loc="lower left")
plt.savefig("./plot/attitude/x.png")

plt.figure()
plt.plot(t_br[0:int(12/dt)], [x[2] for x in quat[0:int(12/dt)]])
plt.plot(t_br[0:int(12/dt)], [x[2] for x in quat_br[0:int(12/dt)]])
plt.xlabel("Time (s)")
plt.title("Quaternion y")
plt.legend(["Estimated", "Ground truth"], loc="lower left")
plt.savefig("./plot/attitude/y.png")

plt.figure()
plt.plot(t_br[0:int(12/dt)], [x[1] for x in quat[0:int(12/dt)]])
plt.plot(t_br[0:int(12/dt)], [x[3] for x in quat_br[0:int(12/dt)]])
plt.xlabel("Time (s)")
plt.title("Quaternion z")
plt.legend(["Estimated", "Ground truth"], loc="lower left")
plt.savefig("./plot/attitude/z.png")

plt.show()
