import argparse
import struct


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
            dig_T1, = struct.unpack('<H', file.read(2))
            dig_T2, = struct.unpack('<h', file.read(2))
            dig_T3, = struct.unpack('<h', file.read(2))
    except (FileNotFoundError) as e:
        print(f"Error: Could not open file: {e}")
        exit(1)
else:
    ...

###########################################################################
#                              CALCULATIONS                               #
###########################################################################

press, temp = [], []
with open(args.data_file, mode='rb') as file:
    while d := file.read(6):
        # Read in data as little endian unsigned 16-bit values
        temp.append(struct.unpack('<H', d[:2])[0])      # First two bytes are temp
        press.append(struct.unpack('<H', d[2:4])[0])    # Second two are pressure

# Calculate temperature from ADC readings and temperature coefficients
for adc_T in temp:
    var1 = ((((adc_T >> 3) - (dig_T1 << 1))) * (dig_T2)) >> 11
    var2 = (((((adc_T >> 4) - (dig_T1)) * ((adc_T >> 4) - (dig_T1)))
            >> 12) * (dig_T3)) >> 14
    T = round(0.01 * (((var1 + var2) * 5 + 128) >> 8), 2)
    print(T)
