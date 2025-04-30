import numpy as np
import matplotlib.pyplot as plt

from ..graph_tab import GraphTab


class AccelerationGraph(GraphTab):
    def setup(self):
        self.title = "Acceleration"

    def graph(self):
        data = self.data[0]
        data_br = self.data[1]
        
        sensitivity = 0.031  # mG/LSB (converted to g)
        total_time = 50
        dt = 0.004  # Time step (seconds)
        dt_br = 0.002  # Time step (seconds)
        g = 9.81

        t = [dt*x for x in range(int(total_time / dt))]
        t_br = [dt_br*x-2 for x in range(int(total_time / dt_br))]

        # Extract and scale sensor data
        accel = np.array([
            [d['Accel_Y'] * d['Tilt_Cosine'] * sensitivity * g,
            d['Accel_Z'] * d['Tilt_Cosine'] * sensitivity * g,
            d['Accel_X'] * d['Tilt_Cosine'] * sensitivity * g]
            for (_, d) in data.iterrows()
        ])
        accel_br = np.array([
            [d['Accel_Z'] * -g,
            d['Accel_Y'] * g,
            d['Accel_X'] * g]
            for (_, d) in data_br.iterrows()
        ])

        self.ax.plot(t, accel[0:int(total_time / dt), 0], label="A1 Avionics")
        self.ax.plot(t_br, accel_br[0:int(total_time / dt_br), 0], label="Blue Raven")
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Acceleration (m/s^2)')
        self.ax.legend()
        self.fig.tight_layout()
