from ..lib.math import Quaternion
from ..graph_tab import GraphTab


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
        time_ranges = {}
        for time_str in self.args['time']:
            source, start, duration = time_str.split(':')
            time_ranges[source] = (float(start), float(duration))

        # axis grid
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_title("")
        ax1, ax2, ax3 = self.fig.subplots(3, 1)

        # Visualise AV estimates
        # -----------------------------------------------------------
        start_AV, duration_AV = time_ranges['AV']
        freq = int(self.args['freq'].split(':')[0])
        dt = 1/freq

        quats_AV = list(zip(
            self.data[1]["quat_x"],
            self.data[1]["quat_y"],
            self.data[1]["quat_z"],
            self.data[1]["quat_w"]
        ))
        visualise(quats_AV, start_AV, duration_AV, dt, "AV estimates", ax1)

        # Visualise BR estimates
        # -----------------------------------------------------------
        start_BR, duration_BR = time_ranges['BR']
        freq = int(self.args['freq'].split(':')[1])
        dt = 1/freq

        quats_BR = list(zip(
            self.data[1]["quat_x"],
            self.data[1]["quat_y"],
            self.data[1]["quat_z"],
            self.data[1]["quat_w"]
        ))
        visualise(quats_BR, start_BR, duration_BR, dt, "BR estimates", ax2)

        quats_truth = list(zip(
            [-x for x in data['quat_x']],
            [y for y in data['quat_y']],
            [z for z in data['quat_z']],
            [w for w in data['quat_w']],
        ))
        visualise(quats_truth, start_BR, duration_BR, dt, "truth", ax3)


        self.fig.tight_layout()