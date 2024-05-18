import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define sensor data file (replace with your actual file path)
df = pd.read_csv('./csv/A1/data_highres.csv')
df_br = pd.read_csv('./csv/A1/data_raven_highres.csv')

sensitivity = 0.031  # mG/LSB (converted to g)

total_time = 50
dt = 0.004  # Time step (seconds)
dt_br = 0.002  # Time step (seconds)

t = [dt*x for x in range(int(total_time / dt))]
t_br = [dt_br*x-2 for x in range(int(total_time / dt_br))]

# Extract and scale sensor data
accel = np.array([
    [d['accel_y'] * d['Tilt_Cosine'] * sensitivity * 9.81,
     d['accel_z'] * d['Tilt_Cosine'] * sensitivity * 9.81,
     d['accel_x'] * d['Tilt_Cosine'] * sensitivity * 9.81]
    for (_, d) in df.iterrows()
])
accel_br = np.array([
    [d['Accel_Z'] * -9.81,
     d['Accel_Y'] * 9.81,
     d['Accel_X'] * 9.81]
    for (_, d) in df_br.iterrows()
])

plt.plot(t, accel[0:int(total_time / dt), 0])
plt.plot(t_br, accel_br[0:int(total_time / dt_br), 0])
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s^2)')
plt.legend(["A1 Avionics", "Blue Raven"])
plt.savefig("./plot/accel/Accel_X.png")

plt.figure()
plt.plot(t, accel[0:int(total_time / dt), 1])
plt.plot(t_br, accel_br[0:int(total_time / dt_br), 1])
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s^2)')
plt.legend(["A1 Avionics", "Blue Raven"])
plt.savefig("./plot/accel/Accel_Y.png")

plt.figure()
plt.plot(t, accel[0:int(total_time / dt), 2])
plt.plot(t_br, accel_br[0:int(total_time / dt_br), 2])
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s^2)')
plt.legend(["A1 Avionics", "Blue Raven"])
plt.savefig("./plot/accel/Accel_Z.png")
plt.show()
print("Figures saved to /plot/accel/")
