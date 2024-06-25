from ctypes import CDLL, c_double
import matplotlib.pyplot as plt
import argparse
import struct

BME280_comp = CDLL("./BME280_comp.so")
BME280_comp.compensate_T.restype = c_double
BME280_comp.compensate_P.restype = c_double
BME280_comp.compensate_H.restype = c_double

###########################################################################
#                               CLI ARGS                                  #
###########################################################################

parser = argparse.ArgumentParser(
    description="Calculate temperature from raw sensor data.")

# Create a mutually exclusive group for coefficient input methods
coeff_group = parser.add_mutually_exclusive_group(required=True)
coeff_group.add_argument(
    "--coeff-temp",
    metavar="[T1,T2,T3]",
    type=str,
    help="Calibration coefficients for temperature as a comma-separated list (e.g., '1234,-567,890')",
)
coeff_group.add_argument(
    "--coeff-file",
    metavar="COEFF_BIN",
    type=str,
    help="Binary file containing calibration coefficients",
)
parser.add_argument(
    "data_file",
    metavar="DATA_BIN",
    type=str,
    help="Binary file containing raw data from sensor"
)
args = parser.parse_args()

# Get temperature calibration coefficients
if args.coeff_temp:
    # Extract from command-line argument
    try:
        dig_T1, dig_T2, dig_T3 = map(int, args.coeff_temp.split(","))
    except ValueError:
        print("Error: Invalid format for --coeff-temp. Use a comma-separated list of integers.")
        exit(1)
elif args.coeff_file:
    # Extract from raw coefficient binary
    try:
        with open(args.coeff_file, mode='rb') as file:
            # Temperature coefficients
            dig_T1, dig_T2, dig_T3 = struct.unpack('<hHH', file.read(6))
            # Pressure coefficients
            dig_P1, dig_P2, dig_P3 = struct.unpack('<HHH', file.read(6))
            dig_P4, dig_P5, dig_P6 = struct.unpack('<HHH', file.read(6))
            dig_P7, dig_P8, dig_P9 = struct.unpack('<HHH', file.read(6))
            # Humidity coefficients
            dig_H1 = struct.unpack('<B', file.read(1))[0]
            dig_H2 = struct.unpack('<H', file.read(2))[0]
            dig_H3 = struct.unpack('<B', file.read(1))[0]

            reg_E4E5 = struct.unpack('<H', file.read(2))[0]

            # Shift to 12-bit
            # TODO: UGGGGHHHHHH
            dig_H4 = (reg_E4E5 >> 4) | (reg_E4E5 | 0x0F)
            dig_H5 = 0x00

            dig_H6 = struct.unpack('<b', file.read(1))[0]
    except (FileNotFoundError) as e:
        print(f"Error: Could not open file: {e}")
        exit(1)
else:
    ...

print(f"python coeff\t{dig_T1} {dig_T2} {dig_T3}")

###########################################################################
#                              CALCULATIONS                               #
###########################################################################

press, temp, humid = [], [], []
with open(args.data_file, mode='rb') as file:
    while d := file.read(6):
        # Read in data as little endian unsigned 16-bit values
        # First two bytes are pressure
        try:
            press.append(struct.unpack('<H', d[0:2])[0])
            # Second two are temperature
            temp.append(struct.unpack('<H', d[2:4])[0])
            # Last two are humidity
            humid.append(struct.unpack('<H', d[4:6])[0])
        except:
            ...

# Calculate temperature from ADC readings and temperature coefficients
press_comp, temp_comp, humid_comp = [], [], []
for adc_T, adc_P, adc_H in list(zip(temp, press, humid)):
    T = BME280_comp.compensate_T(adc_T, dig_T1, dig_T2, dig_T3)
    P = BME280_comp.compensate_P(
        adc_P,
        dig_P1, dig_P2, dig_P3,
        dig_P4, dig_P5, dig_P6,
        dig_P7, dig_P8, dig_P9
    )/100
    H = BME280_comp.compensate_H(
        adc_H,
        dig_H1, dig_H2, dig_H3,
        dig_H4, dig_H5, dig_H6
    )
    temp_comp.append(round(T, 3))
    press_comp.append(round(P, 3))
    humid_comp.append(round(H, 3))

plt.plot(temp_comp)
plt.title("BME280 measured temperature")
plt.xlabel("Sample No.")
plt.ylabel("Temperature (c)")

plt.figure()
plt.plot(press_comp)
plt.title("BME280 measured pressure")
plt.xlabel("Sample No.")
plt.ylabel("Pressure (hPa)")
plt.ylim([1005, 1010])

# plt.figure()
# plt.plot(humid_comp)

plt.show()
