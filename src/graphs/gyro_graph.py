import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ..graph_tab import GraphTab


class GyroGraph(GraphTab):
    def setup(self):
        self.title = "Gyro"

    def graph(self):
        df = self.data[0]
        df_br = self.data[1]

        sensitivity = 13.375  # LSB/degree

        total_time = 50
        dt = 0.004  # Time step (seconds)
        dt_br = 0.002  # Time step (seconds)

        t = [dt*x for x in range(int(total_time / dt))]
        t_br = df_br["Flight_Time_(s)"][0:int(total_time / dt_br)]

        # Extract and scale sensor data
        gyro = np.array([
            [d['Gyro_X'] / sensitivity,
            d['Gyro_Z'] / sensitivity,
            d['Gyro_Y'] / sensitivity]
            for (_, d) in df.iterrows()
        ])

        gyro_br = np.array([
            [d['Gyro_X'],
            -d['Gyro_Z'],
            d['Gyro_Y']]
            for (_, d) in df_br.iterrows()
        ])

        self.ax.plot(t, gyro[0:int(total_time / dt), 0], label="A1 Avionics")
        self.ax.plot(t_br, gyro_br[0:int(total_time / dt_br), 0], label="Blue Raven")
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('X-axis rotational velocity (m/s)')
        self.ax.legend()

        self.fig.tight_layout()
        self.fig.canvas.draw_idle()

        # plt.plot(t, gyro[0:int(total_time / dt), 0])
        # plt.plot(t_br, gyro_br[0:int(total_time / dt_br), 0])
        # plt.xlabel('Time (s)')
        # plt.ylabel('X-axis rotational velocity (m/s)')
        # plt.legend(["A1 Avionics", "Blue Raven"])
        # # plt.savefig("./plot/gyro/Gyro_X.png")

        # plt.show()
        # plt.figure()
        # plt.plot(t, gyro[0:int(total_time / dt), 1])
        # plt.plot(t_br, gyro_br[0:int(total_time / dt_br), 1])
        # plt.xlabel('Time (s)')
        # plt.ylabel('Y-axis rotational velocity (m/s)')
        # plt.legend(["A1 Avionics", "Blue Raven"])
        # # plt.savefig("./plot/gyro/Gyro_Y.png")

        # plt.figure()
        # plt.plot(t, gyro[0:int(total_time / dt), 2])
        # plt.plot(t_br, gyro_br[0:int(total_time / dt_br), 2])
        # plt.xlabel('Time (s)')
        # plt.ylabel('Z-axis rotational velocity (m/s)')
        # plt.legend(["A1 Avionics", "Blue Raven"])
        # # plt.savefig("./plot/gyro/Gyro_Z.png")

        # plt.show()
        # print("Figures saved to /plot/gyro/")
