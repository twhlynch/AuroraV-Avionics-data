#include <stdint.h>
#include <stdio.h>

// Returns temperature in DegC, resolution is 0.01 DegC. Output value of “5123” equals 51.23 DegC.
// t_fine carries fine temperature as global value
int32_t t_fine;
double compensate_T(int32_t adc_T, uint16_t dig_T1, int16_t dig_T2, int16_t dig_T3) {
  double var1, var2, T;
  var1 = (((double)adc_T)/16384.0 - ((double)dig_T1)/1024.0) * ((double)dig_T2);
  var2 = ((((double)adc_T)/131072.0 - ((double)dig_T1)/8192.0) * (((double)adc_T)/131072.0 - ((double) dig_T1)/8192.0)) * ((double)dig_T3);
  t_fine = (int32_t)(var1 + var2);
  T = (var1 + var2) / 5120.0;
  printf("%f\n", T);
  return T;
}
