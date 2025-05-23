from bayes_opt import BayesianOptimization
from sklearn.metrics import root_mean_squared_error
import numpy as np

from ..graph_tab import GraphTab


class KalmanGraph(GraphTab):
    def setup(self):
        self.title = "Kalman"

    def graph(self):
        data = self.data[4]
        data_br = self.data[1]
        data_br_l = self.data[3]

        # Constants and data preparation
        data_count = len(data['sync'])
        dt = 0.004 # Time interval between measurements
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

        cosines = data["Tilt_Cosine"]

        baro = [x for x in data_br_l["Baro_Altitude_AGL_(feet)"]]
        baro = np.repeat(baro[100:], 5)

        vel_br = list(np.repeat(data_br_l["Velocity_Up"], 5)[0:data_count])

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
            x = np.array([[0.0], [0.0], [0.0]])
            # Initial covariance matrix (uncertainty in initial state)
            P = np.diag([1, 0.1, 100])

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
                    x = F @ x  # State prediction
                    P = F @ P @ F.T + Q  # Covariance prediction

                    # Measurement update step
                    # Altitude and acceleration measurements
                    z = np.array(
                        [[baro[i]], [3.28*(cosines[i] * accel[0][i]-9.81)]]
                    )
                    
                    y = z - H @ x  
                    S = H @ P @ H.T + R
                    K = P @ H.T @ np.linalg.inv(S)
                    x = x + K @ y
                    P = (np.eye(len(P)) - K @ H) @ P

                    # Store estimates
                    x_est_list.append(x.copy())
                    P_est_list.append(P.copy())

                if flag:
                    return x_est_list
                
                return -root_mean_squared_error(vel_br[2890:], [x[1][0] for x in x_est_list[2890:]])
            except:
                return -1000
            
        p_bounds = {
            'q0': (0.001, 100), 'q1': (0.001, 100), 'q2': (0.001, 100),
            'r0': (0.001, 100), 'r1': (0.001, 100)
        }

        optimizer = BayesianOptimization(
            f=kalman_filter,
            pbounds=p_bounds,
            random_state=1,
        )
        optimizer.maximize(init_points=5, n_iter=10)
        p = optimizer.max['params']

        x_est_list = kalman_filter(
            p['q0'], p['q1'], p['q2'],
            p['r0'], p['r1'],
            flag=True
        )

        estimated_altitudes = [x[0][0] for x in x_est_list]
        estimated_velocities = [x[1][0] for x in x_est_list]
        estimated_accelerations = [x[2][0] for x in x_est_list]

        # Truncate filter parameters for plot text
        for k, v in p.items():
            p[k] = round(v, 3)

        self.ax.clear()
        self.ax.set_title("Global vertical velocity")
        self.ax.plot(t, estimated_velocities)
        self.ax.plot(t_br_l, data_br_l["Velocity_Up"])
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Velocity (m/s)")
        self.ax.legend(["Calculated estimate", "BR ground truth"])
        # self.ax.text(0.5, 0.5, str(p), fontsize=12, ha='center', va='center')
        self.fig.tight_layout()
