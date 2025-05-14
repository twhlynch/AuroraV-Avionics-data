import numpy as np
import matplotlib.gridspec as gridspec

from ..graph_tab import GraphTab


class GyroGraph(GraphTab):
    def setup(self):
        self.title = "Gyro"

    def graph(self):
        df = self.data[1]

        sensitivity = 13.375  # LSB/degree

        total_time = 50
        dt = 0.004  # Time step (seconds)

        t = [dt*x for x in range(int(total_time / dt))]

        # Extract and scale sensor data
        gyro = np.array([
            [d['gyro_x'] / sensitivity,
            d['gyro_z'] / sensitivity,
            d['gyro_y'] / sensitivity]
            for (_, d) in df.iterrows()
        ])

        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_title("")
        # ax1, ax2, ax3 = self.fig.subplots(1, 3)  
        gs = gridspec.GridSpec(2, 2, figure=self.fig)
        ax1 = self.fig.add_subplot(gs[0, :])
        ax2 = self.fig.add_subplot(gs[1, 0])
        ax3 = self.fig.add_subplot(gs[1, 1])

        ax1.plot(t, gyro[0:int(total_time / dt), 0], label="A1 Avionics")
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('X-axis rotational velocity (m/s)')
        ax1.legend()

        ax2.plot(t, gyro[0:int(total_time / dt), 1])
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Y-axis rotational velocity (m/s)')
        ax2.legend(["A1 Avionics"])

        ax3.plot(t, gyro[0:int(total_time / dt), 2])
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Z-axis rotational velocity (m/s)')
        ax3.legend(["A1 Avionics"])

        self.fig.tight_layout()
        self.fig.canvas.draw_idle()