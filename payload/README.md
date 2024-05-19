## Requirements
- Python 3.x
- matplotlib

## Usage

```
python interpret_data.py [options] data_file

Options:
  --coeff-temp [T1,T2,T3]
                        Calibration coefficients for temperature as a comma-separated
                        list (e.g., '1234,-567,890')
  --coeff-file COEFF_BIN
                        Binary file containing calibration coefficients
  data_file             Binary file containing raw data from sensor
```

**Example:**

To process temperature data from `data.bin` using calibration coefficients from `coeffs.bin`:

```
python bme280_temp.py --coeff-file coeffs.bin data.bin
```

To process data using coefficients provided directly:

```
python bme280_temp.py --coeff-temp 1234,-567,890 data.bin
```

## Input Data Format

- `data_file`: This binary file should contain raw sensor data where each 6-byte chunk represents a single reading. Chunks are split into three unsigned 16-bit ADC outputs in little-endian format.
    - The first 2 bytes of each chunk contain the temperature reading.
    - The next 2 bytes contain the pressure reading.
    - The last 2 bytes contain the humidity reading.

- `coeff_file` (optional): If provided, this file should contain the calibration coefficients (`dig_T1`, `dig_T2`, `dig_T3`) in the following format:
    - `dig_T1`: 2 bytes, unsigned short (little-endian)
    - `dig_T2`: 2 bytes, signed short (little-endian)
    - `dig_T3`: 2 bytes, signed short (little-endian)


## Notes

- The calculation of compensated temperature is based on the formulas provided in the BME280 datasheet.
- Make sure the shared library (`BME280_comp.so`) is in the same directory as the script or in a location specified by your system's library path.


