from ..lib.math import Quaternion
from ..graph_tab import GraphTab
from ..read_data import HIGHRES_HZ


class RotationGraph(GraphTab):
    def setup(self):
        self.title = "Rotation"

    def graph(self):
        
        def visualise(quats: list[list], start_time, duration, dt, typestr, ax):
            t = [dt*i-start_time for i in range(len(quats))]

            # EULER ANGLE
            angles = [
                Quaternion.with_array(q).as_euler(degrees=True).as_array() for q in quats[int(start_time/dt):int(duration/dt)]
            ]
            ax.plot(t[int(start_time/dt):int(duration/dt)], [a[0] for a in angles])
            ax.plot(t[int(start_time/dt):int(duration/dt)], [a[1] for a in angles])
            ax.plot(t[int(start_time/dt):int(duration/dt)], [a[2] for a in angles])
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Angle (degrees)")
            ax.set_title(f"Euler angle {typestr}")
            ax.legend(["Roll", "Pitch", "Yaw"], loc="lower right")

        data = self.data[1]

        # Time parsing
        # -------------------------------------------------------
        time_range = self.args['time'].split(":")
        time_range = (float(time_range[0]), float(time_range[1]))

        # Visualise estimates
        # -----------------------------------------------------------
        start, duration = time_range
        dt = 1/HIGHRES_HZ

        quats = list(zip(
            data["quat_x"],
            data["quat_y"],
            data["quat_z"],
            data["quat_w"]
        ))

        quats_truth = list(zip(
            [-x for x in data['quat_x']],
            [y for y in data['quat_y']],
            [z for z in data['quat_z']],
            [w for w in data['quat_w']],
        ))

        # axis grid
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_title("")
        ax1, ax2 = self.fig.subplots(2, 1)

        visualise(quats, start, duration, dt, "estimates", ax1)
        visualise(quats_truth, start, duration, dt, "truth", ax2)

        self.fig.tight_layout()