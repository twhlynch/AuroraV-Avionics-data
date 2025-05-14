import numpy as np

from ..graph_tab import GraphTab


class AccelerationGraph(GraphTab):
    def setup(self):
        self.title = "Acceleration"

    def graph(self):
        data = self.data[1]
        
        sensitivity = 0.031  # mG/LSB (converted to g)
        total_time = 50
        dt = 0.004  # Time step (seconds)
        dt_br = 0.002  # Time step (seconds)
        g = 9.81

        t = [dt*x for x in range(int(total_time / dt))]
        t_br = [dt_br*x-2 for x in range(int(total_time / dt_br))]

        # Extract and scale sensor data
        accel = np.array([
            [d['acc_y'] * d['tilt_cos'] * sensitivity * g,
            d['acc_z'] * d['tilt_cos'] * sensitivity * g,
            d['acc_x'] * d['tilt_cos'] * sensitivity * g]
            for (_, d) in data.iterrows()
        ])

        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_title("")

        ax1, ax2, ax3 = self.fig.subplots(3, 1)      

        ax1.plot(t, accel[0:int(total_time / dt), 0], label="A1 Avionics")
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Acceleration (m/s^2)')
        ax1.legend()
        
        ax2.plot(t, accel[0:int(total_time / dt), 0], label="A1 Avionics")
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Acceleration (m/s^2)')
        ax2.legend()
        
        ax3.plot(t, accel[0:int(total_time / dt), 0], label="A1 Avionics")
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Acceleration (m/s^2)')
        ax3.legend()
        
        self.fig.tight_layout()
