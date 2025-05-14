import matplotlib
matplotlib.use('TkAgg')

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
from src.graphs.attitude_graph import AttitudeGraph
from src.parse_data import parse_data
from src.read_data import read_data

def get_data(args: dict):
	"""
	Get data from binary files

	Returns:
		A DataFrame of the combined data
	"""

	data_lowres, data_highres = read_data(args["data"])

	data = [
		data_lowres,
		data_highres,
	]

	parse_data(data, args)

	return data

# CLI
def generate(args):
    data = get_data(args)

    output_dir = './csv_data'
    os.makedirs(output_dir, exist_ok=True)

    data[0].to_csv(os.path.join(output_dir, "data_lowres.csv"), index=False)
    data[1].to_csv(os.path.join(output_dir, "data_highres.csv"), index=False)

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
			AttitudeGraph(self.notebook, data, args, data_source='AV'),
			AttitudeGraph(self.notebook, data, args, data_source='BR'),
		]

	def on_close(self):
		self.destroy()
		self.quit()

def visualise(args: dict):
	app = App(args)
	app.mainloop()


def main():
	if False: # currently using test input
		parser = argparse.ArgumentParser(description="Avionics Data Visualisation and CSV Generation")
		parser.add_argument('--csv', action='store_true',
			help="Generate CSV files from data")
		parser.add_argument('data', type=str,
			help='Path to the binary file to extract data from')
		args = vars(parser.parse_args())
	else:
		args = {
			"csv": False,
			"data": "bin_data/20250504_AV",

			# rotation
			"axisAV": "xyz[1,1,1]",
			"axisBR": "xyz[1,1,1]",
			"time": ["AV:0:-1","BR:10:-1"],
			"freq": "1:1",
		}

	if args['csv']:
		generate(args)
	else:
		visualise(args)


if __name__ == "__main__":
	main()