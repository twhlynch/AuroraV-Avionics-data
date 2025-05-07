from math import cos, acos, pi
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ..lib.math import Quaternion, Vector3

from ..graph_tab import GraphTab


class TiltGraph(GraphTab):
    def setup(self):
        self.title = "Tilt"

    def graph(self):
        quat = self.data[5]

        quats = list(zip(
            quat["x"],
            quat["y"],
            quat["z"],
            quat["w"],
        ))
        rotations = [Quaternion.with_array(q) for q in quats]

        z = Vector3(0, 0, 1)
        tilt = []
        tilt_cosine = []

        for rotation in rotations:
            result = rotation.apply(z)
            dot = np.dot(result.__array__(), z.__array__())
            dot = min(max(dot, -1.0), 1.0)  # Clamp the value for acos
            theta = acos(dot)*180/pi

            tilt.append(theta)
            tilt_cosine.append(cos(theta*pi/180))

        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_title("Aurora I body-axis tilt")

        time = [t * 0.002 for t in range(len(rotations))]

        ax1, ax2 = self.fig.subplots(2, 1)        
        ax1.plot(time, tilt, label="Tilt (degrees)")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Tilt (degrees)")
        ax1.legend(loc="upper left")

        # Create a secondary y-axis for tilt cosine
        ax2.plot(time, tilt_cosine, color="orange", label="Tilt Cosine")
        ax2.set_ylabel("Tilt Cosine")
        ax2.legend(loc="upper right")