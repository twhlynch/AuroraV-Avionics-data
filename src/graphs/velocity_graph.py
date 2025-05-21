from ..graph_tab import GraphTab


class VelocityGraph(GraphTab):
    def setup(self):
        self.title = "Velocity"

    def graph(self):
        data = self.data[1]

        # Plot the results
        self.ax.plot(data["time"], data["vel_x"], label="velocity x")
        self.ax.plot(data["time"], data["acc_x"], label="acceleration x")
        # self.ax.plot(data["time"], data["vel_y"], label="vel y")
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('X-Axis Velocity (g)')
        self.ax.set_title('X-Axis Velocity from Accelerometer Data')
        self.fig.tight_layout()
