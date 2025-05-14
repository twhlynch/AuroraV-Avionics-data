from math import cos, acos, pi
import numpy as np

from ..lib.math import Quaternion, Vector3
from ..graph_tab import GraphTab


class TiltGraph(GraphTab):
    def setup(self):
        self.title = "Tilt"

    def graph(self):
        quat = self.data[1]

        tilt = quat["tilt"]
        tilt_cosine = quat["tilt_cos"]

        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_title("Aurora I body-axis tilt")

        time = [t * 0.002 for t in range(len(tilt))]

        ax1, ax2 = self.fig.subplots(2, 1)        
        ax1.plot(time, tilt, label="Tilt (degrees)", linewidth=0.4)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Tilt (degrees)")
        ax1.legend(loc="upper left")

        # Create a secondary y-axis for tilt cosine
        ax2.plot(time, tilt_cosine, color="orange", label="Tilt Cosine", linewidth=0.4)
        ax2.set_ylabel("Tilt Cosine")
        ax2.legend(loc="upper right")
        
        self.fig.tight_layout()