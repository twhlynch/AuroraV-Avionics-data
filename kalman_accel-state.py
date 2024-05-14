from bayes_opt import BayesianOptimization
from sklearn.metrics import root_mean_squared_error
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = pd.read_csv("./csv/A1/data_highres.csv")
data_br = pd.read_csv('./csv/A1/data_raven_highres.csv')
data_br_l = pd.read_csv('./csv/A1/data_raven_lowres.csv')

# Constants and data preparation
data_count = len(data['sync'])
dt = 0.004  # Time interval between measurements
gyro_sens = 13.375
accel_sens = 0.031

t = [x * dt for x in range(data_count)]
t_br = data_br['Flight_Time_(s)']
t_br_l = data_br_l['Flight_Time_(s)']


accel = [
    [9.81 * x * accel_sens for x in data['accel_x']],
    [9.81 * x * accel_sens for x in data['accel_y']],
    [9.81 * x * accel_sens for x in data['accel_z']]
]
accel_br = [
    [9.81 * x for x in data_br['Accel_X']],
    [9.81 * x for x in data_br['Accel_Y']],
    [9.81 * x for x in data_br['Accel_Z']]
]

baro = [x for x in data_br_l["Baro_Altitude_AGL_(feet)"]]
baro = np.repeat(baro[100:], 5)

vel_br = list(np.repeat(data_br_l["Velocity_Up"][100:], 5)[0:data_count])

# Lists to store estimated states and covariances
x_est_list = []
P_est_list = []


def kalman_filter(q0, q1, q2, r0, r1, flag=False):
    x_est_list = []
    P_est_list = []

    # Process noise covariance matrix (model uncertainty)
    Q = np.diag([q0, q1, q2])
    # Measurement noise covariance matrix (sensor noise)
    R = np.diag([r0, r1])
    # Initial state (altitude, velocity, acceleration)
    x = np.array([[0.0], [73.2], [9.81]])
    # Initial covariance matrix (uncertainty in initial state)
    P = np.diag([0.01, 10.0, 0.01])

    # State transition matrix (constant acceleration model)
    F = np.array([
        [1, dt, 0.5 * dt**2],
        [0, 1, dt],
        [0, 0, 1]])

    # Measurement matrix (maps state to measurements)
    H = np.array([
        [1, 0, 0],
        [0, 0, 1]
    ])

    # Kalman filter loop
    try:
        for i in range(data_count):
            # Prediction step
            x_pred = F @ x
            P_pred = F @ P @ F.T + Q

            # Measurement update
            # Altitude and acceleration measurements
            z = np.array([[baro[i]], [accel[0][i]+9.81]])
            y = z - H @ x_pred
            S = H @ P_pred @ H.T + R
            K = P_pred @ H.T @ np.linalg.inv(S)
            x = x_pred + K @ y
            P = (np.eye(3) - K @ H) @ P_pred

            # Store estimates
            x_est_list.append(x.copy())
            P_est_list.append(P.copy())

        if flag:
            return x_est_list
        return -root_mean_squared_error(vel_br[0:2400], [x[1][0] for x in x_est_list[0:2400]])
    except:
        return -1000


pbounds = {
    'q0': (0, 1000), 'q1': (0, 1000), 'q2': (0, 1000),
    'r0': (0, 1000), 'r1': (0, 1000)
}

optimizer = BayesianOptimization(
    f=kalman_filter,
    pbounds=pbounds,
    random_state=1,
)
optimizer.maximize(
    init_points=5,
    n_iter=10,
)
p = optimizer.max['params']

x_est_list = kalman_filter(
    p['q0'], p['q1'], p['q2'], p['r0'], p['r1'], flag=True)

estimated_altitudes = [x[0][0] for x in x_est_list]
estimated_velocities = [x[1][0] for x in x_est_list]
estimated_accelerations = [x[2][0] for x in x_est_list]

# Truncate filter parameters for plot text
for k, v in p.items():
    p[k] = round(v, 2)

plt.plot(t, estimated_velocities)
plt.plot(t, vel_br)
plt.xlabel("Time (s)")
plt.ylabel("Velocity (m/s)")
plt.legend(["Calculated estimate", "BR ground truth"])
plt.title("Global vertical velocity")
plt.figtext(0, 0.95, f"\nFilter parameters {
            p=}", horizontalalignment="left", wrap=True)
plt.savefig("./plot/state/Velocity_X.png")
plt.show()

print("Saved figure to plot/state/")
