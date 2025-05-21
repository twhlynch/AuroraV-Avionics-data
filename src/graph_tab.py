import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from pandas import DataFrame


class GraphTab(ttk.Frame):
	data: list[DataFrame]
	args: dict
	fig: plt.Figure
	ax: plt.Axes
	canvas: FigureCanvasTkAgg
	toolbar: NavigationToolbar2Tk

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
		self.fig, self.ax = plt.subplots(figsize=(6, 5), dpi=100)

		self.graph()

		self.canvas = FigureCanvasTkAgg(self.fig, master=self)
		self.toolbar = NavigationToolbar2Tk(self.canvas, self)
		self.toolbar.update()

		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

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