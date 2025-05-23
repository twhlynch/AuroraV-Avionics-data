import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class GraphTab(ttk.Frame):
	def __init__(self, parent: ttk.Notebook, data: list, args: dict):
		"""

		Args:
			parent (ttk.Notebook): The parent notebook
			data (list): a list of datasets to be used
		"""
		super().__init__(parent)
		self.title = "Undefined"
		self.data = data
		self.args = args

		self.setup()

		parent.add(self, text=self.title)
		plt.rcParams['font.size'] = 7
		self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=80)

		self.graph()

		canvas = FigureCanvasTkAgg(self.fig, master=self)
		toolbar = NavigationToolbar2Tk(canvas, self)
		toolbar.update()

		canvas.draw()
		canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		toolbar.pack(side=tk.BOTTOM, fill=tk.X)

	def setup(self):
		"""
		Should be used to set title and other metadata
		"""
		pass

	def graph(self):
		"""
		Should be used to plot data on self.fig
		"""
		pass