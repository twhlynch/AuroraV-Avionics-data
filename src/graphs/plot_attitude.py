from scipy.spatial.transform import Rotation
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np


###########################################################################
#                              VISUALISATION                              #
###########################################################################

def visualize_rotation(quaternions, interval, label_prefix):
    """
    Visualizes the rotational motion based on a list of quaternions.

    Args:
        quaternions     (list): A list of tuples, where each tuple represents a quaternion 
                                (x, y, z, w).
        interval        (int):  The time interval between quaternion samples in milliseconds.
        label_prefix    (str):  The prefix for the time label in the animation.

    Returns:
        None: The function displays the animation.
    """

    rotations = []
    x1, y1, z1 = (0, 0, 0)  # Starting point coordinates
    x2, y2, z2 = (1, 0, 0)  # X axis vector
    x3, y3, z3 = (0, 1, 0)  # Y axis vector
    x4, y4, z4 = (0, 0, 1)  # Z axis vector

    start_point = np.array([x1, y1, z1])
    _x = np.array([x2, y2, z2])
    _y = np.array([x3, y3, z3])
    _z = np.array([x4, y4, z4])
    xyz = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])

    # Calculate rotations for vector from each attitude quaternion
    for i in range(len(quaternions)):
        q = quaternions[i]
        x, y, z, w = q[0], q[1], q[2], q[3]
        XYZ = Rotation.from_quat([x, y, z, w]).apply(xyz)
        rotations.append(XYZ)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(f"Aurora I body-axis rotation ({label_prefix} estimate)")
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_zlim(-3, 3)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    # Set initial objects on axes
    # -------------------------------------------------
    xaxis = ax.quiver(
        start_point[0], start_point[1], start_point[2],
        rotations[0][0][0],
        rotations[0][0][1],
        rotations[0][0][2],
        color="red", linewidths=(2.5,)
    )
    yaxis = ax.quiver(
        start_point[0], start_point[1], start_point[2],
        rotations[0][1][0],
        rotations[0][1][1],
        rotations[0][1][2],
        color="green", linewidths=(2.5,)
    )
    zaxis = ax.quiver(
        start_point[0], start_point[1], start_point[2],
        rotations[0][2][0],
        rotations[0][2][1],
        rotations[0][2][2],
        color="blue", linewidths=(2.5,)
    )
    label = ax.text2D(
        0.5, 0.95, "t=0 0% of recorded flight data",
        transform=ax.transAxes
    )

    # Calculate new quivers from rotations and plot
    # -------------------------------------------------
    def quiver_data_to_segments(X, Y, Z, u, v, w, length=1):
        segments = (X, Y, Z, X+v*length, Y+u*length, Z+w*length)
        segments = np.array(segments).reshape(6, -1)
        return [[[x, y, z], [u, v, w]] for x, y, z, u, v, w in zip(*list(segments))]

    def animate(i):
        xsegments = quiver_data_to_segments(
            start_point[0], start_point[1], start_point[2],
            rotations[i][0][0],
            rotations[i][0][1],
            rotations[i][0][2],
            length=1
        )
        xaxis.set_segments(xsegments)
        ysegments = quiver_data_to_segments(
            start_point[0], start_point[1], start_point[2],
            rotations[i][1][0],
            rotations[i][1][1],
            rotations[i][1][2],
            length=1
        )
        yaxis.set_segments(ysegments)
        zsegments = quiver_data_to_segments(
            start_point[0], start_point[1], start_point[2],
            rotations[i][2][0],
            rotations[i][2][1],
            rotations[i][2][2],
            length=1
        )
        zaxis.set_segments(zsegments)
        label.set_text(
            f"t={(i*(interval/1000)):.3f} {(100*i/len(quaternions))
                  :.0f}% of recorded flight data"
        )
        return (xaxis, yaxis, zaxis, label)

    # Display animation and save
    # -------------------------------------------------
    ani = animation.FuncAnimation(
        fig=fig, func=animate, frames=len(quaternions), interval=interval
    )
    plt.show()
    ani.save(f"./plot/state/attitude/animation/attitude_{label_prefix}.mp4", writer="ffmpeg",
             progress_callback=lambda i, n: print(f'Saving frame {i}/{n}', end="\r"))


###########################################################################
#                            CONFIGURATION                                #
###########################################################################

data_AV = pd.read_csv('./csv/A1/quaternion_estimate_AV.csv')
data_BR = pd.read_csv('./csv/A1/quaternion_estimate_BR.csv')

quat_AV = list(zip(
    [x for x in data_AV['x']],
    [y for y in data_AV['y']],
    [z for z in data_AV['z']],
    [w for w in data_AV['w']],
))
quat_BR = list(zip(
    [x for x in data_BR['x']],
    [y for y in data_BR['y']],
    [z for z in data_BR['z']],
    [w for w in data_BR['w']],
))[1000:]

###########################################################################
#                                 EXECUTE                                 #
###########################################################################

# Choose the data source and set appropriate parameters
if __name__ == "__main__":
    use_quat_br = True  # Set to True to use quat_br, False to use quat

    if use_quat_br:
        quaternions = quat_BR
        interval = 2  # milliseconds
        label_prefix = "BR"
    else:
        quaternions = quat_AV
        interval = 4  # milliseconds
        label_prefix = "AV"

    visualize_rotation(quaternions, interval, label_prefix)
