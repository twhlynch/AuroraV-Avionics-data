import numpy as np
import matplotlib.gridspec as gridspec

from ..graph_tab import GraphTab


class RawGraph(GraphTab):
    def setup(self):
        self.title = "Raw Data"

    def graph(self):
        lowres = self.data[0]
        highres = self.data[1]

        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_title("")

        gs = gridspec.GridSpec(2, 2, figure=self.fig, wspace=0.15, hspace=0.2, bottom=0.05, left=0.05)
        ax1 = self.fig.add_subplot(gs[0, 0])
        ax2 = self.fig.add_subplot(gs[0, 1])
        ax3 = self.fig.add_subplot(gs[1, 0])
        ax4 = self.fig.add_subplot(gs[1, 1])

        ax1.plot(highres['time'], highres["acc_x"], label="x")
        ax1.plot(highres['time'], highres["acc_y"], label="y")
        ax1.plot(highres['time'], highres["acc_z"], label="z")
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Acceleration')
        ax1.legend()

        ax2.plot(highres['time'], highres["gyro_x"], label="x")
        ax2.plot(highres['time'], highres["gyro_y"], label="y")
        ax2.plot(highres['time'], highres["gyro_z"], label="z")
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Gyroscope')
        ax2.legend()

        ax3.plot(lowres['time'], lowres["press"])
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Pressure')

        ax4.plot(lowres['time'], lowres["temp"])
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Temperature')

        self.fig.tight_layout()
        self.fig.canvas.draw_idle()