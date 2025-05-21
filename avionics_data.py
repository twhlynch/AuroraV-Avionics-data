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
from src.graphs.raw_graph import RawGraph
from src.parse_data import parse_data
from src.read_data import read_data, main as read_write_data

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
    read_write_data(args["data"])

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
			RawGraph(self.notebook, data, args),
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
	parser = argparse.ArgumentParser(description="Avionics Data Visualisation and CSV Generation")
	parser.add_argument('--csv', action='store_true',
		help="Generate CSV files from data")
	parser.add_argument('data', type=str,
		help='Path to the binary file to extract data from')
	args = vars(parser.parse_args())

	args = {
		"csv": args["csv"],
		"data": args["data"],

		# these two are hardcoded for now
		"axis": "xyz[1,1,1]",
		"time": "0:-1",
	}

	if args['csv']:
		generate(args)
	else:
		visualise(args)


if __name__ == "__main__":
	main()