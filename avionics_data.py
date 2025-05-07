import sys
import os
import pandas as pd
import tkinter as tk
from tkinter import ttk
from pandas import DataFrame

from src.graphs.acceleration_graph import AccelerationGraph
from src.graphs.velocity_graph import VelocityGraph
from src.graphs.tilt_graph import TiltGraph
from src.graphs.gyro_graph import GyroGraph
from src.graphs.rotation_graph import RotationGraph
from src.graphs.kalman_graph import KalmanGraph

def get_data():
	"""
	Get data from binary files

	Returns:
		A DataFrame of the combined data
	"""

	# TODO: currently will just read from csv
	return [
		pd.read_csv('./data_csv/data_highres.csv'),
		pd.read_csv('./data_csv/data_raven_highres.csv'),
		pd.read_csv('./data_csv/data_lowres.csv'),
		pd.read_csv('./data_csv/data_raven_lowres.csv'),
		pd.read_csv('./data_csv/quaternion_estimate_AV.csv'),
		pd.read_csv('./data_csv/quaternion_estimate_BR.csv'),
		pd.read_csv('./data_csv/data_highres_2.csv')
	]


# CLI
def generate():
    data = get_data()

    data[0].to_csv("data_highres.csv", index=False)
    data[1].to_csv("data_raven_highres.csv", index=False)
    data[2].to_csv("data_lowres.csv", index=False)
    data[3].to_csv("data_raven_lowres.csv", index=False)
    data[4].to_csv("quaternion_estimate_AV.csv", index=False)
    data[5].to_csv("quaternion_estimate_BR.csv", index=False)
    data[6].to_csv("data_highres_2.csv", index=False)

# UI
class App(tk.Tk):
	def __init__(self):
		super().__init__()

		self.title("Data Visualisation")
		self.protocol("WM_DELETE_WINDOW", self.on_close)
		self.notebook = ttk.Notebook(self)
		self.notebook.pack(fill=tk.BOTH, expand=1)

		data = get_data()

		self.tab_acceleration = AccelerationGraph(self.notebook, data)
		self.tab_velocity = VelocityGraph(self.notebook, data)
		self.tab_tilt = TiltGraph(self.notebook, data)
		self.tab_gyro = GyroGraph(self.notebook, data)
		self.tab_rotation = RotationGraph(self.notebook, data)
		self.tab_kalman = KalmanGraph(self.notebook, data)

	def on_close(self):
		self.destroy()
		self.quit()

def visualise():
	app = App()
	app.mainloop()


def main():
	if '--csv' in sys.argv:
		generate()
	else:
		visualise()


if __name__ == "__main__":
	main()