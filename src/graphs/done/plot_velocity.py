import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Read sensor data from CSV file
data_file = "./csv/A1/data_highres.csv"
data_file_BR = "./csv/A1/data_raven_lowres.csv"
df = pd.read_csv(data_file)
df_BR = pd.read_csv(data_file_BR)
cosines = df["Tilt_Cosine"]
accel_x = df["Accel_X"]

sensitivity = 31 / 1000   # mG/LSB (converted to g)
dt = 0.004                # Time step (seconds)
t = [t*dt for t in range(len(accel_x))]

# Extract and scale accelerometer data
accel_data = [x * sensitivity * 9.81 for x in accel_x]
velocity_x = []
vel = 0

# Perform numerical integration to calculate x-axis velocity
for i in range(len(accel_x)):
    if i >= 11.57/0.004:
        vel += (accel_data[i] * cosines[i]) * 3.28 * dt
    else:
        vel += (accel_data[i] * cosines[i] - 9.81) * 3.28 * dt
    velocity_x.append(vel)

# Plot the results
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
ax.plot(t, velocity_x)  # Plot time on x-axis
ax.plot(df_BR["Flight_Time_(s)"], df_BR["Velocity_Up"])
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('X-Axis Velocity (g)')
ax.set_title('X-Axis Velocity from Accelerometer Data')

plt.tight_layout()
plt.show()
