from scipy.spatial.transform import Rotation
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np

###########################################################################
#                            CONFIGURATION                                #
###########################################################################

data_br = pd.read_csv('./csv/A1/data_raven_highres.csv')
quat = pd.read_csv('./csv/A1/quaternion_estimate.csv')

quat = list(zip(
    [x for x in quat['x']],
    [-y for y in quat['y']],
    [z for z in quat['z']],
    [-w for w in quat['w']],
))
quat_br = list(zip(
    data_br["Quat_1"],
    data_br["Quat_2"],
    data_br["Quat_3"],
    data_br["Quat_4"],
))[1000:]

###########################################################################
#                              VISUALISATION                              #
###########################################################################


def visualize_rotation(quaternions, interval, euler_rot, axes, label_prefix):
    """
    Visualizes the rotational motion based on a list of quaternions.

    Args:
        quaternions     (list): A list of tuples, where each tuple represents a quaternion 
                                (x, y, z, w).
        interval        (int):  The time interval between quaternion samples in milliseconds.
        euler_rot       (list):
        axes            (list):
        label_prefix    (str):  The prefix for the time label in the animation.

    Returns:
        None: The function displays the animation.
    """

    rotations = []
    x1, y1, z1 = (0, 0, 0)     # Starting point coordinates
    x2, y2, z2 = (0.35, 0, 0)  # X axis vector
    x3, y3, z3 = (0, 0.35, 0)  # Y axis vector
    x4, y4, z4 = (0, 0, 0.35)  # Z axis vector
    start_point = np.array([x1, y1, z1])
    _x = np.array([x2, y2, z2])
    _y = np.array([x3, y3, z3])
    _z = np.array([x4, y4, z4])

    # Calculate rotations for vector from each attitude quaternion
    for i in range(len(quaternions)):
        q = quaternions[i]
        x, y, z, w = q[0], q[1], q[2], q[3]
        X = Rotation.from_quat([x, y, z, w]).apply(_x) - start_point
        X = Rotation.from_euler("xyz", euler_rot, degrees=True).apply(X)
        Y = Rotation.from_quat([x, y, z, w]).apply(_y) - start_point
        Y = Rotation.from_euler("xyz", euler_rot, degrees=True).apply(Y)
        Z = Rotation.from_quat([x, y, z, w]).apply(_z) - start_point
        Z = Rotation.from_euler("xyz", euler_rot, degrees=True).apply(Z)
        rotations.append((X, Y, Z))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(f"Aurora I body-axis rotation ({label_prefix} estimate)")
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    # Set initial objects on axes
    # -------------------------------------------------
    xaxis = ax.quiver(
        start_point[0], start_point[1], start_point[2],
        rotations[0][axes[0]][0],
        rotations[0][axes[0]][1],
        rotations[0][axes[0]][2],
        color="red", linewidths=(2.5,)
    )
    yaxis = ax.quiver(
        start_point[0], start_point[1], start_point[2],
        rotations[0][axes[1]][0],
        rotations[0][axes[1]][1],
        rotations[0][axes[1]][2],
        color="green", linewidths=(2.5,)
    )
    zaxis = ax.quiver(
        start_point[0], start_point[1], start_point[2],
        rotations[0][axes[2]][0],
        rotations[0][axes[2]][1],
        rotations[0][axes[2]][2],
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
            rotations[i][axes[0]][0],
            rotations[i][axes[0]][1],
            rotations[i][axes[0]][2],
            length=1
        )
        xaxis.set_segments(xsegments)
        ysegments = quiver_data_to_segments(
            start_point[0], start_point[1], start_point[2],
            rotations[i][axes[1]][0],
            rotations[i][axes[1]][1],
            rotations[i][axes[1]][2],
            length=1
        )
        yaxis.set_segments(ysegments)
        zsegments = quiver_data_to_segments(
            start_point[0], start_point[1], start_point[2],
            rotations[i][axes[2]][0],
            rotations[i][axes[2]][1],
            rotations[i][axes[2]][2],
            length=1
        )
        zaxis.set_segments(zsegments)
        label.set_text(
            f"{label_prefix}t={
                (i*(interval/1000)):.3f} {(100*i/len(quaternions)):.0f}% of recorded flight data"
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
#                                 EXECUTE                                 #
###########################################################################

# Choose the data source and set appropriate parameters
if __name__ == "__main__":
    use_quat_br = True  # Set to True to use quat_br, False to use quat

    if use_quat_br:
        quaternions = quat_br
        interval = 2  # milliseconds
        label_prefix = "BR"
        # Rotation from recorded frame to global frame
        euler_rot = [180, 0, 90]
        axes = [0, 1, 2]            # Axes relative to Blue Raven
    else:
        quaternions = quat
        interval = 4  # milliseconds
        label_prefix = "AV"
        # Rotation from recorded frame to global frame
        euler_rot = [0, -90, 0]
        axes = [2, 0, 1]            # Axes relative to Blue Raven

    visualize_rotation(quaternions, interval, euler_rot, axes, label_prefix)
