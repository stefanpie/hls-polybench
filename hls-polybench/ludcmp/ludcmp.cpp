#include "ludcmp.h"


void kernel_ludcmp(
		   t_ap_fixed A[ 120 + 0][120 + 0],
		   t_ap_fixed b[ 120 + 0],
		   t_ap_fixed x[ 120 + 0],
		   t_ap_fixed y[ 120 + 0])
{
  #pragma HLS top name=kernel_ludcmp

    const int n = 120;

  int i, j, k;

  t_ap_fixed w;

  for (i = 0; i < n; i++) {
    for (j = 0; j <i; j++) {
       w = A[i][j];
       for (k = 0; k < j; k++) {
          w -= A[i][k] * A[k][j];
       }
        A[i][j] = w / A[j][j];
    }
   for (j = i; j < n; j++) {
       w = A[i][j];
       for (k = 0; k < i; k++) {
          w -= A[i][k] * A[k][j];
       }
       A[i][j] = w;
    }
  }

  for (i = 0; i < n; i++) {
     w = b[i];
     for (j = 0; j < i; j++)
        w -= A[i][j] * y[j];
     y[i] = w;
  }

   for (i = n-1; i >=0; i--) {
     w = y[i];
     for (j = i+1; j < n; j++)
        w -= A[i][j] * x[j];
     x[i] = w / A[i][i];
  }

}