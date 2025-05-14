import matplotlib.animation as animation
import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation
import os

from ..graph_tab import GraphTab

class AttitudeGraph(GraphTab):
    def setup(self):
        self.title = f"Attitude ({self.data_source})"

    def __init__(self, master, data, args, data_source='BR', save_animation_on_start=False):
        self.data_source = data_source
        self.data = data
        self.title = f"Attitude ({self.data_source})"

        self.quaternions = []
        self.rotations = []
        self.start_point = np.array([0, 0, 0])
        self.interval_ms = 2 if self.data_source == 'BR' else 4
        self.xaxis_q = None
        self.yaxis_q = None
        self.zaxis_q = None
        self.time_label = None
        self.ani = None

        self._load_attitude_data()
        if self.quaternions:
            self._calculate_rotations()

        super().__init__(master, data, args)

        # self.output_dir = args.get('attitude_output_dir', os.path.join('.', 'data_csv', 'animations'))
        # os.makedirs(self.output_dir, exist_ok=True)

        # if save_animation_on_start and self.ani:
        #     self.save_animation_to_file()
        # elif save_animation_on_start:
        #     print(f"Warning: Animation for {self.data_source} not created during init, cannot save on start.")

    def _load_attitude_data(self):
        """
        Loads quaternion data from the main data object (self.data)
        Expects data[5] for AV and data[6] for BR from parse_data.
        """
        df_quats = None
        source_index = -1

        if self.data_source == 'AV':
            source_index = 1
        elif self.data_source == 'BR':
            source_index = 1
        else:
            print(f"Warning: Unknown data source '{self.data_source}' for attitude data.")
            self.quaternions = []
            return

        if len(self.data) > source_index and isinstance(self.data[source_index], pd.DataFrame):
            df_quats = self.data[source_index]
        else:
            print(f"Warning: Quaternion data for {self.data_source} (expected at data[{source_index}]) not found or not a DataFrame.")
            self.quaternions = []
            return
        
        if not all(col in df_quats.columns for col in ['quat_x', 'quat_y', 'quat_z', 'quat_w']):
            print(f"Warning: Quaternion DataFrame for {self.data_source} is missing x,y,z, or w columns.")
            self.quaternions = []
            return

        loaded_quats = list(zip(
            df_quats['quat_x'], df_quats['quat_y'], df_quats['quat_z'], df_quats['quat_w']
        ))

        if self.data_source == 'AV':
            print(f"[DEBUG AV Load] Trying to load AV quaternions from self.data[{source_index}].")
            if df_quats is not None:
                print(f"[DEBUG AV Load] AV DataFrame head:\n{df_quats.head()}")
            else:
                print(f"[DEBUG AV Load] AV DataFrame (df_quats) is None.")

        # Apply 1000 sample offset for BR data to match original plot_attitude.py behavior
        # This assumes parse_data.py provides the full BR quaternion dataset.
        if self.data_source == 'BR':
            if len(loaded_quats) > 1000:
                print(f"[Debug] Applying 1000 sample offset to BR quaternion data for attitude plot. Original length: {len(loaded_quats)}")
                self.quaternions = loaded_quats[1000:]
                print(f"[Debug] New length for BR: {len(self.quaternions)}")
            else:
                print(f"Warning: BR quaternion data for {self.data_source} has less than 1000 samples ({len(loaded_quats)}), cannot apply offset.")
                self.quaternions = loaded_quats # Use as is
        else:
            self.quaternions = loaded_quats
        
        if self.data_source == 'AV':
            print(f"[DEBUG AV Load] Loaded {len(self.quaternions)} quaternions for AV.")
            if len(self.quaternions) > 0:
                print(f"[DEBUG AV Load] First 3 AV quaternions: {self.quaternions[:3]}")
        
        if not self.quaternions:
            print(f"Warning: No quaternion data loaded for {self.data_source}.")


    def _calculate_rotations(self):
        """Calculates rotation matrices for each quaternion."""
        rotations_list = []
        xyz_basis = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        if not self.quaternions:
            print(f"Cannot calculate rotations: No quaternions for {self.data_source}")
            self.rotations = []
            return

        for i, q_tuple in enumerate(self.quaternions):
            x, y, z, w = q_tuple
            if not all(np.isfinite([x, y, z, w])):
                print(f"Warning: Non-finite value in quaternion {q_tuple} at index {i} for {self.data_source}. Using identity.")
                rotations_list.append(np.identity(3))
                continue
            try:
                # Scipy's Rotation expects (x, y, z, w) for from_quat
                rotation_matrix = Rotation.from_quat([x, y, z, w]).apply(xyz_basis)
                rotations_list.append(rotation_matrix)
            except ValueError as e:
                print(f"Error processing quaternion {q_tuple} for {self.data_source}: {e}. Using identity.")
                rotations_list.append(np.identity(3))
        
        self.rotations = rotations_list
        if self.data_source == 'AV' and len(self.rotations) > 2:
            print(f"[DEBUG AV Calc] First 3 AV rotation matrices:\n{self.rotations[0]}\n{self.rotations[1]}\n{self.rotations[2]}")
        
        if not self.rotations:
            print(f"Warning: No rotations could be calculated for {self.data_source}.")


    def graph(self):
        self.fig.clear() 
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.ax.set_title(f"Body-Axis Rotation ({self.data_source})")
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_zlim(-1.5, 1.5)
        self.ax.set_xlabel('X Axis')
        self.ax.set_ylabel('Y Axis')
        self.ax.set_zlabel('Z Axis')

        if not self.quaternions or not self.rotations:
            self.ax.text2D(0.5, 0.5, f"No data/rotations for {self.data_source}", transform=self.ax.transAxes, ha="center", va="center")
            return

        initial_rotation = self.rotations[0]
        self.xaxis_q = self.ax.quiver(*self.start_point, *initial_rotation[0,:], color="r", label='X')
        self.yaxis_q = self.ax.quiver(*self.start_point, *initial_rotation[1,:], color="g", label='Y')
        self.zaxis_q = self.ax.quiver(*self.start_point, *initial_rotation[2,:], color="b", label='Z')
        self.time_label = self.ax.text2D(0.05, 0.95, "t=0.000s (0%)", transform=self.ax.transAxes)
        self.ax.legend(loc='upper right')

        self.ani = animation.FuncAnimation(
            fig=self.fig, func=self._animate, frames=len(self.quaternions),
            interval=self.interval_ms, blit=False, repeat=True 
        )


    def _quiver_data_to_segments(self, X, Y, Z, u, v, w, length=1):
        # Ensure inputs are finite, replace NaNs/infs if necessary
        u, v, w = np.nan_to_num(u), np.nan_to_num(v), np.nan_to_num(w)
        # Segments format for quiver.set_segments:
        # [[[x, y, z], [x+u, y+v, z+w]], ...]
        # Our u,v,w are already the direction vectors relative to origin (X,Y,Z)
        # and scaled by apply(xyz_basis)
        return [[[X, Y, Z], [X + u * length, Y + v * length, Z + w * length]]]

    def _animate(self, i):
        if i >= len(self.rotations): # Should not happen with FuncAnimation if frames is correct
            return (self.xaxis_q, self.yaxis_q, self.zaxis_q, self.time_label)

        current_rotation = self.rotations[i]
        if not np.all(np.isfinite(current_rotation)):
            # Skip update for this frame if data is bad, or use previous
            print(f"Warning: Non-finite rotation data at frame {i} for {self.data_source}.")
            return (self.xaxis_q, self.yaxis_q, self.zaxis_q, self.time_label)

        # Update X axis
        segments_x = self._quiver_data_to_segments(*self.start_point, *current_rotation[0,:])
        self.xaxis_q.set_segments(segments_x)

        # Update Y axis
        segments_y = self._quiver_data_to_segments(*self.start_point, *current_rotation[1,:])
        self.yaxis_q.set_segments(segments_y)

        # Update Z axis
        segments_z = self._quiver_data_to_segments(*self.start_point, *current_rotation[2,:])
        self.zaxis_q.set_segments(segments_z)
        
        time_sec = i * (self.interval_ms / 1000.0)
        progress_pct = (100.0 * i / len(self.quaternions)) if self.quaternions else 0
        self.time_label.set_text(f"t={time_sec:.3f}s ({progress_pct:.0f}%)")

        return (self.xaxis_q, self.yaxis_q, self.zaxis_q, self.time_label)

    # def save_animation_to_file(self):
    #     if not self.ani:
    #         print(f"Animation (self.ani) not initialized for {self.data_source}. Cannot save.")
    #         return
    #     if not self.quaternions or not self.rotations:
    #         print(f"No data to animate for {self.data_source}. Cannot save animation.")
    #         return

    #     output_filename = f"attitude_animation_{self.data_source}.mp4"
    #     output_path = os.path.join(self.output_dir, output_filename)
        
    #     print(f"Attempting to save animation for {self.data_source} to {output_path}...")
    #     try:
    #         # Ensure ffmpeg is installed and in PATH.
    #         # Adjust dpi or fps (frames per second via 1000/interval_ms) if needed.
    #         writer = animation.writers['ffmpeg'](fps=1000/self.interval_ms, bitrate=1800)
    #         self.ani.save(output_path, writer=writer, dpi=150, progress_callback=lambda i, n: print(f'Saving frame {i+1}/{n} for {self.data_source}', end="\r"))
    #         print(f"\nAnimation for {self.data_source} saved successfully to {output_path}")
    #     except Exception as e:
    #         print(f"\nError saving animation for {self.data_source}: {e}")
    #         print("Please ensure ffmpeg is installed and accessible in your system's PATH.")