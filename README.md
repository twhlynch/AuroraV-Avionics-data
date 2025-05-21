# Avionics Data Visualisation

Something something data blah

# Setup

## Prerequisites
- Python 3.13 or higher

## Setup Environment

### On macOS/Linux
1. Create a virtual environment:
	```bash
	python3 -m venv .venv
	```
2. Activate the virtual environment:
	```bash
	source .venv/bin/activate
	```
3. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
4. Install `tkinter` if needed on macOS:
	```bash
	brew install python-tk
	```

### On Windows
> Note: your `python` executable may be `py`, `py3`, or `python3`
1. Create a virtual environment:
	```cmd
	python -m venv .venv
	```
2. Activate the virtual environment:
	```cmd
	.venv\Scripts\activate
	```
3. Install dependencies:
	```cmd
	pip install -r requirements.txt
	```

## Usage

### GUI
Run the Graphical Interface for visualising data and optionally exporting as CSV.
```bash
python avionics_data.py
```

### CLI
Generate the CSV on the command line or with a script.
```bash
python avionics_data.py --csv
```