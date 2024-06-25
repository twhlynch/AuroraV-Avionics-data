#include <stdint.h>
#include <stdio.h>

// Returns temperature in DegC, resolution is 0.01 DegC. Output value of “5123” equals 51.23 DegC.
// t_fine carries fine temperature as global value
int32_t t_fine;
double compensate_T(int32_t adc_T, uint16_t dig_T1, int16_t dig_T2, int16_t dig_T3) {
  double var1, var2, T;
  adc_T = adc_T << 4;
  var1 = (((double)adc_T)/16384.0 - ((double)dig_T1)/1024.0) * ((double)dig_T2);
  var2 = ((((double)adc_T)/131072.0 - ((double)dig_T1)/8192.0) * (((double)adc_T)/131072.0 - ((double) dig_T1)/8192.0)) * ((double)dig_T3);
  t_fine = (int32_t)(var1 + var2);
  T = (var1 + var2) / 5120.0;
  return T;
}

// Returns pressure in Pa as double. Output value of “96386.2” equals 96386.2 Pa = 963.862 hPa
double compensate_P(
  int32_t adc_P,
  uint16_t dig_P1, int16_t dig_P2, int16_t dig_P3, 
  int16_t dig_P4, int16_t dig_P5, int16_t dig_P6, 
  int16_t dig_P7, int16_t dig_P8, int16_t dig_P9
) {
  double var1, var2, p;
  adc_P = adc_P << 4;
  var1 = ((double)t_fine/2.0) - 64000.0;
  var2 = var1 * var1 * ((double)dig_P6) / 32768.0;
  var2 = var2 + var1 * ((double)dig_P5) * 2.0;
  var2 = (var2/4.0)+(((double)dig_P4) * 65536.0);
  var1 = (((double)dig_P3) * var1 * var1 / 524288.0 + ((double)dig_P2) * var1) / 524288.0;
  var1 = (1.0 + var1 / 32768.0)*((double)dig_P1);
  if (var1 == 0.0) {
    return 0; // avoid exception caused by division by zero
  }
  p = 1048576.0 - (double)adc_P;
  p = (p - (var2 / 4096.0)) * 6250.0 / var1;
  var1 = ((double)dig_P9) * p * p / 2147483648.0;
  var2 = p * ((double)dig_P8) / 32768.0;
  p = p + (var1 + var2 + ((double)dig_P7)) / 16.0;
  return p;
}

// Returns humidity in %rH as as double. Output value of “46.332” represents 46.332 %rH
double compensate_H (
  uint32_t adc_H, 
  uint8_t dig_H1, int16_t dig_H2, uint8_t dig_H3, 
  int16_t dig_H4, int16_t dig_H5, int8_t dig_H6
) {
  double var_H;
  var_H = (((double)t_fine) - 76800.0);
  var_H = (adc_H - (((double)dig_H4) * 64.0 + ((double)dig_H5) / 16384.0 *
  var_H)) * (((double)dig_H2) / 65536.0 * (1.0 + ((double)dig_H6) /
  67108864.0 * var_H *
  (1.0 + ((double)dig_H3) / 67108864.0 * var_H)));
  var_H = var_H * (1.0 - ((double)dig_H1) * var_H / 524288.0);
  if (var_H > 100.0)
    var_H = 100.0;
  else if (var_H < 0.0)
    var_H = 0.0;
  return var_H;
}
