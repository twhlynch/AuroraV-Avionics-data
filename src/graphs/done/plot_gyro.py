import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define sensor data file (replace with your actual file path)
df = pd.read_csv('./csv/A1/data_highres.csv')
df_br = pd.read_csv('./csv/A1/data_raven_highres.csv')

sensitivity = 13.375  # LSB/degree

total_time = 50
dt = 0.004  # Time step (seconds)
dt_br = 0.002  # Time step (seconds)

t = [dt*x for x in range(int(total_time / dt))]
t_br = df_br["Flight_Time_(s)"][0:int(total_time / dt_br)]

# Extract and scale sensor data
gyro = np.array([
    [d['gyro_x'] / sensitivity,
     d['gyro_y'] / sensitivity,
     d['gyro_z'] / sensitivity]
    for (_, d) in df.iterrows()
])

gyro_br = np.array([
    [d['Gyro_X'],
     -d['Gyro_Z'],
     d['Gyro_Y']]
    for (_, d) in df_br.iterrows()
])

plt.plot(t, gyro[0:int(total_time / dt), 0])
plt.plot(t_br, gyro_br[0:int(total_time / dt_br), 0])
plt.xlabel('Time (s)')
plt.ylabel('X-axis rotational velocity (m/s)')
plt.legend(["A1 Avionics", "Blue Raven"])
# plt.savefig("./plot/gyro/Gyro_X.png")

plt.show()
plt.figure()
plt.plot(t, gyro[0:int(total_time / dt), 1])
plt.plot(t_br, gyro_br[0:int(total_time / dt_br), 1])
plt.xlabel('Time (s)')
plt.ylabel('Y-axis rotational velocity (m/s)')
plt.legend(["A1 Avionics", "Blue Raven"])
# plt.savefig("./plot/gyro/Gyro_Y.png")

plt.figure()
plt.plot(t, gyro[0:int(total_time / dt), 2])
plt.plot(t_br, gyro_br[0:int(total_time / dt_br), 2])
plt.xlabel('Time (s)')
plt.ylabel('Z-axis rotational velocity (m/s)')
plt.legend(["A1 Avionics", "Blue Raven"])
# plt.savefig("./plot/gyro/Gyro_Z.png")

plt.show()
print("Figures saved to /plot/gyro/")
