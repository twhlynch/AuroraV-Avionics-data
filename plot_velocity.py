import numpy as np
import matplotlib.pyplot as plt
import csv

data_file = "./csv/A1/data_highres.csv"
accel_sensitivity = 31 / 1000   # mG/LSB (converted to g)
dt = 0.004                      # Time step (seconds)

# Read sensor data from CSV file
data = []
with open(data_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header row
    for row in reader:
        data.append([float(val) for val in row])

# Extract and scale accelerometer data
num_steps = len(data)
accel_data = np.array([[(d[1] * accel_sensitivity)*9.81-9.81, d[2]
                      * accel_sensitivity, d[3] * accel_sensitivity] for d in data])

# Initialize variables
velocity_x = np.zeros(num_steps)  # Initialize array to store x-axis velocity

# Perform numerical integration to calculate x-axis velocity
for i in range(1, num_steps):
    velocity_x[i] = velocity_x[i-1] + accel_data[i, 0] * dt

# Plot the results
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
ax.plot(np.arange(num_steps) * dt, velocity_x)  # Plot time on x-axis
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('X-Axis Velocity (g)')
ax.set_title('X-Axis Velocity from Accelerometer Data')

plt.tight_layout()
plt.show()
