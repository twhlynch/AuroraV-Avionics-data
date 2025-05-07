import matplotlib.gridspec as gridspec

from ..lib.math import Quaternion, Vector3
from ..graph_tab import GraphTab


class GyroStateGraph(GraphTab):
    def setup(self):
        self.title = "Gyro State"

    def graph(self):
        data_br = self.data[1]

        data_count = len(data_br['Flight_Time_(s)'])
        dt = 0.002
        
        t_br = data_br['Flight_Time_(s)']
        gyro_br = [
            [x for x in data_br['Gyro_X']],
            [x for x in data_br['Gyro_Y']],
            [x for x in data_br['Gyro_Z']]
        ]


        x_est_list = [[0, 0, 0]]
        for i in range(data_count):
            gyro_x = gyro_br[0][i] - (-0.12)
            gyro_y = gyro_br[2][i] - (0.61)
            gyro_z = gyro_br[1][i] - (-0.59)
            x_est_list.append([
                x_est_list[i][0] + dt*gyro_x,
                x_est_list[i][1] + dt*gyro_y,
                x_est_list[i][2] + dt*gyro_z
            ])

        quat = [
            Quaternion.with_half_euler(x, y, z)
            for (x, y, z) in x_est_list[1:]
        ]
        quat_br = list(zip(
            data_br["Quat_1"],
            data_br["Quat_2"],
            data_br["Quat_3"],
            data_br["Quat_4"],
        ))
        euler = [
            Quaternion.with_array(quat).as_euler().as_array()
            for quat in quat_br
        ]

        estimated_roll = [x[0] for x in x_est_list[1:]]
        estimated_pitch = [x[1] for x in x_est_list[1:]]
        estimated_yaw = [x[2] for x in x_est_list[1:]]


        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.set_title("")

        gs = gridspec.GridSpec(2, 2, figure=self.fig)
        ax1 = self.fig.add_subplot(gs[0, 0])
        ax2 = self.fig.add_subplot(gs[0, 1])
        ax3 = self.fig.add_subplot(gs[1, 0])
        ax4 = self.fig.add_subplot(gs[1, 1])

        # ax1.plot(t_br, estimated_roll)
        # ax1.plot(t_br, estimated_pitch)
        # ax1.plot(t_br, estimated_yaw)
        # ax1.xlabel("Time (s)")
        # ax1.ylabel("Angle (degrees)")
        # ax1.title("Euler angle estimates")
        # ax1.legend(["Roll", "Pitch", "Yaw"], loc="upper left")

        ax1.plot(t_br[0:int(12/dt)], [x[3] for x in quat[0:int(12/dt)]])
        ax1.plot(t_br[0:int(12/dt)], [x[0] for x in quat_br[0:int(12/dt)]])
        ax1.set_xlabel("Time (s)")
        ax1.set_title("Quaternion w")
        ax1.legend(["Estimated", "Ground truth"], loc="lower left")

        ax2.plot(t_br[0:int(12/dt)], [x[0] for x in quat[0:int(12/dt)]])
        ax2.plot(t_br[0:int(12/dt)], [x[1] for x in quat_br[0:int(12/dt)]])
        ax2.set_xlabel("Time (s)")
        ax2.set_title("Quaternion x")
        ax2.legend(["Estimated", "Ground truth"], loc="lower left")

        ax3.plot(t_br[0:int(12/dt)], [x[2] for x in quat[0:int(12/dt)]])
        ax3.plot(t_br[0:int(12/dt)], [x[2] for x in quat_br[0:int(12/dt)]])
        ax3.set_xlabel("Time (s)")
        ax3.set_title("Quaternion y")
        ax3.legend(["Estimated", "Ground truth"], loc="lower left")

        ax4.plot(t_br[0:int(12/dt)], [x[1] for x in quat[0:int(12/dt)]])
        ax4.plot(t_br[0:int(12/dt)], [x[3] for x in quat_br[0:int(12/dt)]])
        ax4.set_xlabel("Time (s)")
        ax4.set_title("Quaternion z")
        ax4.legend(["Estimated", "Ground truth"], loc="lower left")

        self.fig.tight_layout()
        self.fig.canvas.draw_idle()