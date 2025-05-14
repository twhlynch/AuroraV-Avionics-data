import matplotlib
matplotlib.use('TkAgg') # Explicitly set backend BEFORE other imports

import argparse
import pandas as pd
import tkinter as tk
from tkinter import ttk
import os

from src.graphs.acceleration_graph import AccelerationGraph
from src.graphs.velocity_graph import VelocityGraph
from src.graphs.tilt_graph import TiltGraph
from src.graphs.gyro_graph import GyroGraph
from src.graphs.gyro_state_graph import GyroStateGraph
from src.graphs.rotation_graph import RotationGraph
from src.graphs.kalman_graph import KalmanGraph
from src.graphs.done.plot_attitude_updated import PlotAttitudeUpdated
from src.parse_data import parse_data


def get_data(args: dict):
	"""
	Get data from binary files

	Returns:
		A DataFrame of the combined data
	"""
	script_dir = os.path.dirname(os.path.abspath(__file__))
	data_csv_dir = os.path.join(script_dir, 'data_csv')

	# Debugging: Check if the directory and files are seen by the script
	print(f"[Debug] Script directory resolved to: {script_dir}")
	print(f"[Debug] Expecting data_csv directory at: {data_csv_dir}")

	if not os.path.isdir(data_csv_dir):
		print(f"[Debug] Error: Directory {data_csv_dir} not found from script's perspective.")
		# This will likely cause read_csv to fail, which is the current behavior.
	else:
		print(f"[Debug] Directory {data_csv_dir} found.")
		try:
			print(f"[Debug] Contents of {data_csv_dir}: {os.listdir(data_csv_dir)}")
		except Exception as e:
			print(f"[Debug] Error listing contents of {data_csv_dir}: {e}")
		
		target_files_to_check = [
			'data_highres.csv',
			'data_raven_highres.csv',
			'data_lowres.csv',
			'data_raven_lowres.csv',
			'data_highres_2.csv'
		]
		for f_name in target_files_to_check:
			file_path = os.path.join(data_csv_dir, f_name)
			if not os.path.isfile(file_path):
				print(f"[Debug] Error: File {file_path} not found from script's perspective.")
			else:
				print(f"[Debug] Success: File {file_path} found.")

	# TODO: currently will just read from csv
	data = [
		pd.read_csv(os.path.join(data_csv_dir, 'data_highres.csv')),
		pd.read_csv(os.path.join(data_csv_dir, 'data_raven_highres.csv')),
		pd.read_csv(os.path.join(data_csv_dir, 'data_lowres.csv')),
		pd.read_csv(os.path.join(data_csv_dir, 'data_raven_lowres.csv')),
		pd.read_csv(os.path.join(data_csv_dir, 'data_highres_2.csv'))
	]

	parse_data(data, args)

	return data

# CLI
def generate(args):
    data = get_data(args)

    # Ensure the output directory exists
    output_dir = './data_csv'
    os.makedirs(output_dir, exist_ok=True)

    # Save files to the correct directory
    data[0].to_csv(os.path.join(output_dir, "data_highres.csv"), index=False)
    data[1].to_csv(os.path.join(output_dir, "data_raven_highres.csv"), index=False)
    data[2].to_csv(os.path.join(output_dir, "data_lowres.csv"), index=False)
    data[3].to_csv(os.path.join(output_dir, "data_raven_lowres.csv"), index=False)
    data[4].to_csv(os.path.join(output_dir, "data_highres_2.csv"), index=False)
    data[5].to_csv(os.path.join(output_dir, "quaternion_estimate_AV.csv"), index=False)
    data[6].to_csv(os.path.join(output_dir, "quaternion_estimate_BR.csv"), index=False)
    print(f"CSV files generated in {output_dir}")

# UI
class App(tk.Tk):
	def __init__(self, args: dict):
		super().__init__()

		self.title("Data Visualisation")
		self.protocol("WM_DELETE_WINDOW", self.on_close)
		self.notebook = ttk.Notebook(self)
		self.notebook.pack(fill=tk.BOTH, expand=1)

		data = get_data(args)

		self.tabs = [
			AccelerationGraph(self.notebook, data, args),
			VelocityGraph(self.notebook, data, args),
			TiltGraph(self.notebook, data, args),
			GyroGraph(self.notebook, data, args),
			GyroStateGraph(self.notebook, data, args),
			RotationGraph(self.notebook, data, args),
			KalmanGraph(self.notebook, data, args),
		]

		# Add Attitude Visualization Tabs based on args
		attitude_mode = args.get("attitude_visualization_mode", "None") # Default to "None"
		
		if attitude_mode == "AV" or attitude_mode == "Both":
			save_av_anim = args.get('attitude_save_av_animation', False)
			print(f"Initializing AV Attitude Tab (Save: {save_av_anim})")
			self.tabs.append(PlotAttitudeUpdated(self.notebook, data, args,
										 data_source='AV',
										 save_animation_on_start=save_av_anim))
		if attitude_mode == "BR" or attitude_mode == "Both":
			save_br_anim = args.get('attitude_save_br_animation', False)
			print(f"Initializing BR Attitude Tab (Save: {save_br_anim})")
			self.tabs.append(PlotAttitudeUpdated(self.notebook, data, args,
										 data_source='BR',
										 save_animation_on_start=save_br_anim))

	def on_close(self):
		self.destroy()
		self.quit()

def visualise(args: dict):
	# Removed the old standalone calls to PlotAttitudeUpdated
	# print("Running Attitude Visualization (AV)...")
	# attitude_viz_av = PlotAttitudeUpdated(data_source='AV', data_dir='./data_csv', output_dir='./data_csv')
	# attitude_viz_av.run_visualization(show=False, save=True)

	# print("\nRunning Attitude Visualization (BR)...")
	# attitude_viz_br = PlotAttitudeUpdated(data_source='BR', data_dir='./data_csv', output_dir='./data_csv')
	# attitude_viz_br.run_visualization(show=False, save=True)

	print("\nStarting GUI Application...")
	app = App(args)
	app.mainloop()


def main():
	if False: # currently using test input
		parser = argparse.ArgumentParser(description="Avionics Data Visualisation and CSV Generation")
		parser.add_argument('--csv', action='store_true',
			help="Generate CSV files from data (only generates, doesn't visualize)")
		parser.add_argument('data', type=str,
			help='Path to the binary file to extract data from')
		args = vars(parser.parse_args())
	else: # Using hardcoded args for testing
		args = {
			"csv": False,
			"data": "data.bin",

			# rotation
			"axisAV": "xyz[1,1,1]",
			"axisBR": "xyz[1,1,1]",
			"time": ["AV:0:-1","BR:10:-1"],
			"freq": "1:1",

			# Attitude Visualization Settings
			"attitude_visualization_mode": "Both",  # Options: "None", "AV", "BR", "Both"
			"attitude_save_av_animation": False,     # True to save AV animation on start
			"attitude_save_br_animation": False,    # True to save BR animation on start
			"attitude_output_dir": "./data_csv/animations" # Common output dir for animations
		}

	# Always generate/update data first unless specifically told *only* to generate CSV
	if not args['csv']:
		print("Ensuring data files are generated/updated...")
		try:
			generate(args)
			print("Data generation/update complete.")
			visualise(args)
		except FileNotFoundError as e:
			print(f"\nError during data generation: {e}")
			print("Could not find required input file (e.g., data.bin or initial CSVs for parse_data). Exiting.")
			exit(1)
		except Exception as e:
			print(f"\nAn unexpected error occurred during data generation or visualization: {e}")
			exit(1)
	else:
		# If --csv is specified, only generate the files
		print("Generating CSV files only...")
		try:
			generate(args)
		except FileNotFoundError as e:
			print(f"\nError during CSV generation: {e}")
			print("Could not find required input file (e.g., data.bin or initial CSVs for parse_data). Exiting.")
			exit(1)
		except Exception as e:
			print(f"\nAn unexpected error occurred during CSV generation: {e}")
			exit(1)


if __name__ == "__main__":
	main()