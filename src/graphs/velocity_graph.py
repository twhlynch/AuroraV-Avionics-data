from ..graph_tab import GraphTab


class VelocityGraph(GraphTab):
    def setup(self):
        self.title = "Velocity"

    def graph(self):
        data = self.data[0]
        data_br = self.data[3]

        cosines = data["Tilt_Cosine"]
        accel_x = data["Accel_X"]

        sensitivity = 31 / 1000   # mG/LSB (converted to g)
        dt = 0.004                # Time step (seconds)
        t = [t*dt for t in range(len(accel_x))]

        # Extract and scale accelerometer data
        accel_data = [x * sensitivity * 9.81 for x in accel_x]
        velocity_x = []
        vel = 0

        # Perform numerical integration to calculate x-axis velocity
        for i in range(len(accel_x)):
            if i >= 11.57/0.004:
                vel += (accel_data[i] * cosines[i]) * 3.28 * dt
            else:
                vel += (accel_data[i] * cosines[i] - 9.81) * 3.28 * dt
            velocity_x.append(vel)

        # Plot the results
        self.ax.plot(t, velocity_x)  # Plot time on x-axis
        self.ax.plot(data_br["Flight_Time_(s)"], data_br["Velocity_Up"])
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('X-Axis Velocity (g)')
        self.ax.set_title('X-Axis Velocity from Accelerometer Data')
        self.fig.tight_layout()
